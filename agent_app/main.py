import uvicorn
import logging
from fastapi import FastAPI
from api.core import router as trigger_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

#: FastAPI application instance
app = FastAPI(
    title="Agent API",
    version="1.0.0",
    description="Microservice agent",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
"""FastAPI application providing the Agent API."""


#: Register API routes
app.include_router(trigger_router, prefix="/agent", tags=["agent"])


if __name__ == "__main__":
    """
    Entry point for running the Agent API service.

    This starts a Uvicorn server listening on host ``0.0.0.0`` and port ``8001``.
    The application is reloaded automatically on code changes.
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
