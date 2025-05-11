from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import create_async_engine

from app.models.db import UserDb, GardenDb, DeviceDb, NotificationDb, ReadingDb
from app.core.config import CONFIG

app = FastAPI()

engine = create_async_engine(CONFIG.DB_CONNECTION_STRING, echo=True)

admin = Admin(app, engine)


class UserAdmin(ModelView, model=UserDb):
    column_list = [UserDb.id, UserDb.email]


class GardenAdmin(ModelView, model=GardenDb):
    column_list = [GardenDb.id, GardenDb.user_id, GardenDb.name, GardenDb.created_at]


class DeviceAdmin(ModelView, model=DeviceDb):
    column_list = [
        DeviceDb.id,
        DeviceDb.mac,
        DeviceDb.type,
        DeviceDb.garden_id,
        DeviceDb.created_at,
    ]


class NotificationAdmin(ModelView, model=NotificationDb):
    column_list = [NotificationDb.id, NotificationDb.user_id]


class ReadingAdmin(ModelView, model=ReadingDb):
    column_list = [ReadingDb.id, ReadingDb.device_id, ReadingDb.value, ReadingDb.timestamp]


admin.add_view(UserAdmin)
admin.add_view(GardenAdmin)
admin.add_view(DeviceAdmin)
admin.add_view(NotificationAdmin)
admin.add_view(ReadingAdmin)
