from datetime import datetime

from fastapi.requests import Request
from app.core.templates import templates


def main_page(req: Request):
    now = datetime.now()
    return templates.TemplateResponse(
        req, "main.jinja", {"date": now.replace(microsecond=0)}
    )
