from fastapi import APIRouter, Request

from yadi.config import Settings
from yadi.core.deps import CurrentUserId, DbSession
from yadi.modules.assistant import service
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
