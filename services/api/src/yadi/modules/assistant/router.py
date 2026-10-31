from fastapi import APIRouter, Request

from yadi.config import Settings
from yadi.core.deps import CurrentUserId, DbSession
from yadi.modules.assistant import actions, service
from yadi.modules.assistant.conversation import ApplyRequest, AssistantReply, MessageRequest
from yadi.modules.assistant.schemas import ExtractRequest, ExtractResponse

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/extract")
def extract(
    data: ExtractRequest, request: Request, session: DbSession, user_id: CurrentUserId
) -> ExtractResponse:
    """Understands free text as task drafts for the user to review. Saves nothing."""
    settings: Settings = request.app.state.settings
    return service.extract_tasks(
        session,
        user_id,
        data.text,
        client=request.app.state.llm_client,
        daily_limit=settings.ai_daily_call_limit,
    )


@router.post("/message")
def message(
    data: MessageRequest, request: Request, session: DbSession, user_id: CurrentUserId
) -> AssistantReply:
    """Interprets a message and, unless it needs a choice or confirmation, carries it out."""
    settings: Settings = request.app.state.settings
    return service.handle_message(
        session,
        user_id,
        data,
        client=request.app.state.llm_client,
        daily_limit=settings.ai_daily_call_limit,
    )


@router.post("/apply")
def apply(data: ApplyRequest, session: DbSession, user_id: CurrentUserId) -> AssistantReply:
    """Runs a proposed action. Checked again in full, whatever the client sends."""
    return actions.perform(session, user_id, data.action, confirmed=data.confirmed)
