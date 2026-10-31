"""Delivery channels. They decide how a message is sent, never when."""

import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from pywebpush import WebPushException, webpush  # type: ignore[import-untyped]
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from yadi.config import Settings
from yadi.modules.reminders.models import PushSubscription

log = logging.getLogger("yadi.delivery")


@dataclass(frozen=True)
class Message:
    reminder_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    body: str


class PushChannel(Protocol):
    def send(self, session: Session, message: Message) -> str:
        """Returns the outcome to record. Never raises for a delivery problem."""
        ...


Sender = Callable[[PushSubscription, str], None]


class ExpiredSubscriptionError(Exception):
    pass


class WebPushChannel:
    def __init__(self, sender: Sender) -> None:
        self._sender = sender

    def send(self, session: Session, message: Message) -> str:
        subscriptions = session.scalars(
            select(PushSubscription).where(PushSubscription.user_id == message.user_id)
        ).all()
        if not subscriptions:
            return "no_subscription"
        payload = json.dumps(
            {"title": message.title, "body": message.body, "tag": str(message.reminder_id)}
        )
        accepted = 0
        for subscription in subscriptions:
            try:
                self._sender(subscription, payload)
                accepted += 1
            except ExpiredSubscriptionError:
                session.execute(
                    delete(PushSubscription).where(PushSubscription.id == subscription.id)
                )
            except Exception as exc:  # A push failure must never undo the in-app delivery.
                log.warning("push failed: %s", type(exc).__name__)
        session.commit()
        # "Accepted" means the push service took it. Whether a device showed it is unknown.
        return "accepted" if accepted else "failed"


def build_push_channel(settings: Settings) -> PushChannel | None:
    if not settings.vapid_private_key or not settings.vapid_private_key.get_secret_value():
        return None
    private_key = settings.vapid_private_key.get_secret_value()

    def send(subscription: PushSubscription, payload: str) -> None:
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                },
                data=payload,
                vapid_private_key=private_key,
                vapid_claims={"sub": settings.vapid_subject},
                timeout=10,
            )
        except WebPushException as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status in (404, 410):
                raise ExpiredSubscriptionError from exc
            raise

    return WebPushChannel(send)
