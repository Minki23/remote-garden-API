import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from exceptions.scheme import AppException
from views import common_view

logger = logging.getLogger(__name__)


def add_json(app: FastAPI):
    """
    Register a JSON exception handler for AppException.

    Parameters
    ----------
    app : FastAPI
        FastAPI application instance.
    """
    logger.info("Adding JSON exception handler")

    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            {"message": exc.message},
            status_code=exc.status_code,
        )

    app.add_exception_handler(AppException, app_exception_handler)


def add_html(app: FastAPI):
    """
    Register an HTML exception handler for AppException.

    Parameters
    ----------
    app : FastAPI
        FastAPI application instance.
    """
    logger.info("Adding HTML exception handler")

    async def app_exception_handler(request: Request, exc: AppException):
        return common_view.error_page(request, exc)

    app.add_exception_handler(AppException, app_exception_handler)


def add_general_exception_handler(app: FastAPI):
    """
    Register a general exception handler for unhandled exceptions.

    Logs the error with traceback and returns either JSON or HTML response
    depending on request headers and path.

    Parameters
    ----------
    app : FastAPI
        FastAPI application instance.
    """
    logger.info("Adding general exception handler")

    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception in {request.method} {request.url.path}: {str(exc)}"
        )
        logger.error(f"Full traceback: {traceback.format_exc()}")

        accept_header = request.headers.get("accept", "")
        content_type = request.headers.get("content-type", "")
        prefers_json = (
            "application/json" in accept_header
            or "application/json" in content_type
            or request.url.path.startswith("/api")
        )

        response_payload = {
            "message": "Internal server error",
            "detail": str(exc),
            "traceback": traceback.format_exc(),
            "path": str(request.url.path),
        }

        return JSONResponse(response_payload, status_code=500)

    app.add_exception_handler(Exception, general_exception_handler)
