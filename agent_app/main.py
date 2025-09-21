import uvicorn
import logging
from fastapi import FastAPI
from api.core import router as trigger_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="Agent API",
    version="1.0.0",
    description="Microservice agent",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(trigger_router, prefix="/agent", tags=["agent"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
