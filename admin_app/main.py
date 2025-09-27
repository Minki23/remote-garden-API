from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import create_async_engine

from common_db.models import (
    UserDb,
    GardenDb,
    DeviceDb,
    NotificationDb,
    ReadingDb,
    EspDeviceDb,
    UserDeviceDb,
    AgentDb,
)
import os

app = FastAPI()

engine = create_async_engine(os.getenv("DB_CONNECTION_STRING"), echo=True)

admin = Admin(app, engine)


class UserAdmin(ModelView, model=UserDb):
    column_list = [
        UserDb.id,
        UserDb.email,
        UserDb.google_sub,
        UserDb.auth,
        UserDb.admin,
        UserDb.created_at,
        UserDb.updated_at,
        UserDb.refresh_expires_at,
        UserDb.refresh_token_hash,
    ]


class GardenAdmin(ModelView, model=GardenDb):
    column_list = [
        GardenDb.id,
        GardenDb.user_id,
        GardenDb.name,
        GardenDb.send_notifications,
        GardenDb.enable_automation,
        GardenDb.use_fahrenheit,
        GardenDb.created_at,
        GardenDb.updated_at,
    ]


class EspDeviceAdmin(ModelView, model=EspDeviceDb):
    column_list = [
        EspDeviceDb.id,
        EspDeviceDb.mac,
        EspDeviceDb.secret,
        EspDeviceDb.client_key,
        EspDeviceDb.client_crt,
        EspDeviceDb.garden_id,
        EspDeviceDb.user_id,
        EspDeviceDb.status,
        EspDeviceDb.created_at,
        EspDeviceDb.updated_at,
    ]


class DeviceAdmin(ModelView, model=DeviceDb):
    column_list = [
        DeviceDb.id,
        DeviceDb.esp_id,
        DeviceDb.type,
        DeviceDb.enabled,
        DeviceDb.created_at,
        DeviceDb.updated_at,
    ]


class NotificationAdmin(ModelView, model=NotificationDb):
    column_list = [
        NotificationDb.id,
        NotificationDb.user_id,
        NotificationDb.message,
        NotificationDb.read,
        NotificationDb.type,
        NotificationDb.created_at,
        NotificationDb.updated_at,
    ]


class ReadingAdmin(ModelView, model=ReadingDb):
    column_list = [
        ReadingDb.id,
        ReadingDb.device_id,
        ReadingDb.value,
        ReadingDb.timestamp,
        ReadingDb.created_at,
        ReadingDb.updated_at,
    ]


class UserDeviceAdmin(ModelView, model=UserDeviceDb):
    column_list = [
        UserDeviceDb.id,
        UserDeviceDb.user_id,
        UserDeviceDb.fcm_token,
        UserDeviceDb.platform,
        UserDeviceDb.last_seen,
        UserDeviceDb.created_at,
        UserDeviceDb.updated_at,
    ]


class AgentAdmin(ModelView, model=AgentDb):
    column_list = [
        AgentDb.id,
        AgentDb.garden_id,
        AgentDb.enabled,
        AgentDb.refresh_token_hash,
        AgentDb.refresh_expires_at,
        AgentDb.created_at,
        AgentDb.updated_at,
    ]


admin.add_view(UserAdmin)
admin.add_view(GardenAdmin)
admin.add_view(EspDeviceAdmin)
admin.add_view(DeviceAdmin)
admin.add_view(NotificationAdmin)
admin.add_view(ReadingAdmin)
admin.add_view(UserDeviceAdmin)
admin.add_view(AgentAdmin)
