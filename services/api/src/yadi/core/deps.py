"""Request dependencies: a database session and the current user."""

import uuid
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from yadi.config import Settings
from yadi.core.errors import AppError
from yadi.db.seed import DEV_EMAIL
from yadi.modules.users.models import User


def get_session(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine, expire_on_commit=False) as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]


def get_current_user_id(
    request: Request,
    session: DbSession,
    x_dev_user: Annotated[str | None, Header(include_in_schema=False)] = None,
) -> uuid.UUID:
    """Development identity (ADR-005). Real sign-in replaces this function by M05."""
    settings: Settings = request.app.state.settings
    unauthenticated = AppError("UNAUTHENTICATED", 401, "Sign-in is required.")
    if not settings.dev_identity_enabled:
        raise unauthenticated
    user_id = session.scalar(select(User.id).where(User.email == (x_dev_user or DEV_EMAIL)))
    if user_id is None:
        raise unauthenticated
    return user_id


CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
