from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

import logging
logger = logging.getLogger(__name__)

def custom_openapi(app: FastAPI) -> dict:
    if app.openapi_schema:
        logger.info("Returning cached OpenAPI schema")
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Remote Garden API",
        version="1.0.0",
        description="API for Remote Garden with JWT Bearer Auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [{"BearerAuth": []}]

    logger.info("Generated OpenAPI schema")

    app.openapi_schema = openapi_schema
    return app.openapi_schema
