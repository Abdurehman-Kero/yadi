"""Single error format for the whole API: {"error": {code, message, details, requestId}}."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("yadi.errors")

_HTTP_CODES = {
    401: "UNAUTHENTICATED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    429: "RATE_LIMITED",
    503: "SERVICE_UNAVAILABLE",
}


class AppError(Exception):
    def __init__(
        self, code: str, status_code: int, message: str, details: list[dict[str, Any]] | None = None
    ) -> None:
        super().__init__(message)
        self.code, self.status_code, self.message = code, status_code, message
        self.details = details or []


def _body(
    request: Request, code: str, message: str, details: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    rid = getattr(request.state, "request_id", "")
    return {"error": {"code": code, "message": message, "details": details or [], "requestId": rid}}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(_body(request, exc.code, exc.message, exc.details), exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]), "issue": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(_body(request, "VALIDATION_FAILED", "Invalid request.", details), 400)

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _HTTP_CODES.get(exc.status_code, "ERROR")
        return JSONResponse(_body(request, code, str(exc.detail)), exc.status_code)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.error("unhandled exception", exc_info=exc)
        return JSONResponse(_body(request, "INTERNAL", "Something went wrong."), 500)
