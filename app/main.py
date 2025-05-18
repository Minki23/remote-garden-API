from app.exceptions.scheme import AppException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core import lifespan
from controllers.pages import page_controller
from controllers.api import router as api_router

from app.core.middlewares import cors_middleware
from app.core.middlewares import static_middleware
from app.exceptions import handler

import logging

logging.basicConfig(level=logging.INFO)

# HTML/Jinja2 app
app = FastAPI(lifespan=lifespan.lifespan)

# API (JSON) app
api = FastAPI(lifespan=lifespan.lifespan)

# custom exception handlers
handler.add_html(app)
handler.add_json(api)

# middlewares
static_middleware.add(app)
cors_middleware.add(api)

# HTML routes (Jinja)
app.include_router(page_controller.router)

# API routes (JSON)
api.include_router(api_router)

# mount API under /api
app.mount("/api", api)
