import logging
from fastapi.staticfiles import StaticFiles
from app.controllers.mqtt_handlers import subscribe_topics
from app.core.custom_openapi import custom_openapi
from fastapi import FastAPI
from app.core.lifespan import lifespan
# from app.core.middlewares import cors_middleware
# from app.core.middlewares import static_middleware
from app.exceptions import handler
# from app.exceptions.scheme import AppException
from controllers.pages import page_controller
from controllers.api import router as api_router
from controllers.websocket import router as ws_router
from fastapi.middleware.cors import CORSMiddleware
from controllers.live import router as live_router
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").disabled = True

app = FastAPI(lifespan=lambda app: lifespan(app, subscribe_topics))

# app.openapi = lambda: custom_openapi(app)

# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
# import logging
# logger = logging.getLogger(__name__)
# class LogHeadersMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         logger.info("Incoming request headers:")
#         for k, v in request.headers.items():
#             logger.info(f"{k}: {v}")
#         return await call_next(request)

# app.add_middleware(LogHeadersMiddleware)
# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

handler.add_html(app)
handler.add_json(app)

# Routing
app.include_router(page_controller.router)
app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")
app.include_router(live_router, prefix="/live")
