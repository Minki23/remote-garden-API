from fastapi import APIRouter

from . import (
    users,
    gardens,
    devices,
    readings,
    notifications,
    schedules,
    auth
)

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(gardens.router, prefix="/gardens", tags=["Gardens"])
router.include_router(devices.router, prefix="/devices", tags=["Devices"])
router.include_router(readings.router, prefix="/readings", tags=["Readings"])
router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
router.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
