from fastapi import APIRouter

from . import (
    users,
    gardens,
    devices,
    readings,
    notifications,
)

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(gardens.router, prefix="/gardens", tags=["Gardens"])
router.include_router(devices.router, prefix="/devices", tags=["Devices"])
router.include_router(readings.router, prefix="/readings", tags=["Readings"])
router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
