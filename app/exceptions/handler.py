from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.scheme import AppException
from views import common_view
import logging

logger = logging.getLogger(__name__)


def add_json(app: FastAPI):
    logger.info("Adding JSON exception handler")

    async def exception_handler(request: Request, exc: AppException):
        """
        Handle exceptions and return a JSON response.
        :param request: FastAPI request object
        :param exc: Exception object
        :return: JSON response with error details
        """
        return JSONResponse(
            {
                "message": exc.message,
            },
            status_code=exc.status_code,
        )

    app.add_exception_handler(AppException, exception_handler)


def add_html(app: FastAPI):
    logger.info("Adding HTML exception handler")

    async def exception_handler(request: Request, exc: AppException):
        return common_view.error_page(request, exc)

    app.add_exception_handler(AppException, exception_handler)
