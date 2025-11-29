import os
from datetime import datetime
from fastapi.requests import Request
from core.templates import templates


def main_page(req: Request):
    now = datetime.now()
    ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() == "true"
    server_hostname = os.getenv("SERVER_HOSTNAME", "localhost")

    scheme = "https" if ssl_enabled else "http"
    host_url = f"{scheme}://{server_hostname}"

    return templates.TemplateResponse(
        req,
        "main.jinja",
        {
            "date": now.replace(microsecond=0),
            "host_url": host_url,
        },
    )
