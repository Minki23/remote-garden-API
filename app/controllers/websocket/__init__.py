from fastapi import APIRouter

from . import (
    websocket_init,
)

router = APIRouter()
router.include_router(websocket_init.router)
