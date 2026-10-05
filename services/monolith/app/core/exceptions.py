"""The single error envelope and the handlers that produce it.

Every error the API returns uses one shape (roadmap §4.6, doc 40 §6)::

    {"error": {"code": "...", "message": "...", "details": [...]}}
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """A business error that maps to an HTTP status + machine ``code``."""

    def __init__(self, status_code: int, code: str, message: str,
                 details: list[dict[str, Any]] | None = None,
                 headers: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        self.headers = headers or {}
        super().__init__(message)


def _envelope(
    code: str, message: str, details: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or []}}


def register_exception_handlers(app: FastAPI) -> None:
    """Wire the envelope handlers onto the app."""

    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details),
            headers=exc.headers or None,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"field": ".".join(str(p) for p in e["loc"][1:]), "issue": e["msg"]}
                   for e in exc.errors()]
        return JSONResponse(
            status_code=422,
            content=_envelope("validation_error", "Validation failed.", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        _codes = {401: "unauthorized", 403: "forbidden", 404: "not_found"}
        code = _codes.get(exc.status_code, "error")
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(code, str(exc.detail)),
        )
