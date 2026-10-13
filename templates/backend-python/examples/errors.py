"""Worked example: typed errors mapped to RFC 9457 problem responses (PY-4)."""
from typing import ClassVar

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog

log = structlog.get_logger()


class AppError(Exception):
    status: ClassVar[int] = 500
    type: ClassVar[str] = "about:blank"

    def __init__(self, title: str, detail: dict[str, object] | None = None) -> None:
        super().__init__(title)
        self.title = title
        self.detail = detail or {}


class NotFoundError(AppError):
    status = 404
    type = "https://errors.example.com/not-found"


class ForbiddenError(AppError):
    status = 403
    type = "https://errors.example.com/forbidden"


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        rid = request.state.request_id
        return JSONResponse(
            status_code=exc.status,
            media_type="application/problem+json",
            content={"type": exc.type, "title": exc.title, "status": exc.status,
                     "instance": request.url.path, "requestId": rid, "errors": exc.detail},
        )

    @app.exception_handler(Exception)
    async def _unknown(request: Request, exc: Exception) -> JSONResponse:
        rid = request.state.request_id
        log.error("unhandled_error", request_id=rid, error_type=type(exc).__name__)  # no message: may contain data
        return JSONResponse(
            status_code=500,
            media_type="application/problem+json",
            content={"type": "about:blank", "title": "Internal Server Error", "status": 500,
                     "instance": request.url.path, "requestId": rid},
        )
