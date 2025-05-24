import logging

from app.controllers.mqtt_handlers import subscribe_topics
from app.core.custom_openapi import custom_openapi
from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.core.middlewares import cors_middleware
from app.core.middlewares import static_middleware
from app.exceptions import handler
from app.exceptions.scheme import AppException
from controllers.pages import page_controller
from controllers.api import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").disabled = True

app = FastAPI(lifespan=lambda app: lifespan(app, subscribe_topics))

# app.openapi = lambda: custom_openapi(app)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
logger = logging.getLogger(__name__)
class LogHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info("Incoming request headers:")
        for k, v in request.headers.items():
            logger.info(f"{k}: {v}")
        return await call_next(request)

app.add_middleware(LogHeadersMiddleware)
# Middleware
static_middleware.add(app)
cors_middleware.add(app)

handler.add_html(app)
handler.add_json(app)

# Routing
app.include_router(page_controller.router)
app.include_router(api_router, prefix="/api")
