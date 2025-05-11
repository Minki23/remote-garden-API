from fastapi import FastAPI

from core import lifespan
from controllers.pages import page_controller
from controllers.api import router as api_router

from core.middlewares import cors_middleware
from core.middlewares import static_middleware
from exceptions import handler

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
