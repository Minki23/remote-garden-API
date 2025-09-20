from fastapi import APIRouter

from . import (
    users,
    gardens,
    devices,
    readings,
    notifications,
    schedules,
    auth,
    esp_devices,
    admin,
    user_devices, agents
)

router = APIRouter()
router.include_router(agents.router, prefix="/agents", tags=["Agents"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(gardens.router, prefix="/gardens", tags=["Gardens"])
router.include_router(devices.router, prefix="/devices", tags=["Devices"])
router.include_router(readings.router, prefix="/readings", tags=["Readings"])
router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)
router.include_router(
    schedules.router, prefix="/schedules", tags=["Schedules"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(esp_devices.router, prefix="/esp", tags=["Esp Devices"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
router.include_router(user_devices.router, prefix="/userdevices",
                      tags=["User Devices"])
