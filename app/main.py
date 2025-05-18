import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import Request

from app.core import lifespan
from app.core.middlewares import cors_middleware
from app.core.middlewares import static_middleware
from app.exceptions import handler
from app.exceptions.scheme import AppException
from controllers.pages import page_controller
from controllers.api import router as api_router

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)

# Tworzymy jedną aplikację FastAPI z lifespan
app = FastAPI(lifespan=lifespan.lifespan)

# Middleware
static_middleware.add(app)
cors_middleware.add(app)

# Rejestracja handlerów wyjątków
handler.add_html(app)
handler.add_json(app)

# Routing
app.include_router(page_controller.router)
app.include_router(api_router, prefix="/api")
