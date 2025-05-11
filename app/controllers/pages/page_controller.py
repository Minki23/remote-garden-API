from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from views import main_view

router = APIRouter(prefix="", tags=["Pages"], default_response_class=HTMLResponse)


@router.get("/")
def main(req: Request):
    return main_view.main_page(req)
