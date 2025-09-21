import logging
import traceback
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from controllers.mqtt_handlers import subscribe_topics
# from core.custom_openapi import custom_openapi
from fastapi import FastAPI, Request
from core.lifespan import lifespan

# from core.middlewares import cors_middleware
# from core.middlewares import static_middleware
from exceptions import handler

# from exceptions.scheme import AppException
from exceptions.scheme import AppException
from controllers.pages import page_controller
from controllers.api import router as api_router
from controllers.websocket import router as ws_router
from fastapi.middleware.cors import CORSMiddleware
# from controllers.live import router as live_router
import colorlog

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers = [handler]

logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").disabled = True


app = FastAPI(lifespan=lambda app: lifespan(app, subscribe_topics))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    logging.error(f"CAUGHT EXCEPTION: {str(exc)}")
    logging.error(f"REQUEST: {request.method} {request.url}")
    logging.error(f"TRACEBACK: {traceback.format_exc()}")

    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
            }
        )

    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "path": str(request.url.path)
        }
    )

# Routing
app.include_router(page_controller.router)
app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")
# app.include_router(live_router, prefix="/live")

# @TODO add env that mocks db
