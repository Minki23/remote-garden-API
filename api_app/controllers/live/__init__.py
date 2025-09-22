from fastapi import APIRouter

from . import (
    live_stream,
)

router = APIRouter()
router.include_router(live_stream.router)
