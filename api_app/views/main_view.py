import os
from datetime import datetime
from fastapi.requests import Request
from core.templates import templates


def main_page(req: Request):
    now = datetime.now()
    host_url = os.getenv("HOST_URL", "https://localhost")
    return templates.TemplateResponse(
        req,
        "main.jinja",
        {
            "date": now.replace(microsecond=0),
            "host_url": host_url,
        },
    )
