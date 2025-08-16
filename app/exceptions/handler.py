import traceback
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.scheme import AppException
from views import common_view
import logging

logger = logging.getLogger(__name__)


def add_json(app: FastAPI):
    logger.info("Adding JSON exception handler")

    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            {
                "message": exc.message,
            },
            status_code=exc.status_code,
        )

    app.add_exception_handler(AppException, app_exception_handler)


def add_html(app: FastAPI):
    logger.info("Adding HTML exception handler")

    async def app_exception_handler(request: Request, exc: AppException):
        return common_view.error_page(request, exc)

    app.add_exception_handler(AppException, app_exception_handler)


def add_general_exception_handler(app: FastAPI):
    logger.info("Adding general exception handler")

    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception in {request.method} {request.url.path}: {str(exc)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")

        accept_header = request.headers.get("accept", "")
        content_type = request.headers.get("content-type", "")

        if "application/json" in accept_header or "application/json" in content_type or request.url.path.startswith("/api"):
            return JSONResponse(
                {
                    "message": "Internal server error",
                    "detail": str(exc),
                    "traceback": traceback.format_exc(),
                    "path": str(request.url.path)
                },
                status_code=500,
            )
        else:
            return JSONResponse(
                {
                    "message": "Internal server error",
                    "detail": str(exc),
                    "traceback": traceback.format_exc(),
                    "path": str(request.url.path)
                },
                status_code=500,
            )

    app.add_exception_handler(Exception, general_exception_handler)
