from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    ForeignKey,
    String,
    DateTime,
    Enum as SqlEnum,
    Boolean,
)
from sqlalchemy.orm import mapped_column, relationship, Mapped, DeclarativeBase
from .enums import DeviceType, NotificationType


class Base(DeclarativeBase):
    pass


class SuperDb(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UserDb(SuperDb):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    google_sub: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=True
    )
    auth: Mapped[str] = mapped_column(
        String, unique=True, nullable=True
    )
    admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    gardens: Mapped[list["GardenDb"]] = relationship(
        "GardenDb", back_populates="user"
    )
    notifications: Mapped[list["NotificationDb"]] = relationship(
        "NotificationDb", back_populates="user"
    )


class GardenDb(SuperDb):
    __tablename__ = "gardens"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    send_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_automation: Mapped[bool] = mapped_column(Boolean, default=False)
    use_fahrenheit: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["UserDb"] = relationship("UserDb", back_populates="gardens")
    devices: Mapped[list["DeviceDb"]] = relationship(
        "DeviceDb", back_populates="garden", cascade="all, delete-orphan"
    )
    esp_devices: Mapped[list["EspDeviceDb"]] = relationship(
        "EspDeviceDb", back_populates="garden", cascade="all, delete-orphan"
    )


class DeviceDb(SuperDb):
    __tablename__ = "devices"

    esp_id: Mapped[int] = mapped_column(Integer, ForeignKey("esp_devices.id"))
    type: Mapped[DeviceType] = mapped_column(
        SqlEnum(DeviceType), nullable=False)

    esp: Mapped["EspDeviceDb"] = relationship(
        "EspDeviceDb", back_populates="devices")
    readings: Mapped[list["ReadingDb"]] = relationship(
        "ReadingDb", back_populates="device", cascade="all, delete-orphan"
    )
    garden: Mapped[Optional["GardenDb"]] = relationship(
        "GardenDb", back_populates="devices"
    )


class ReadingDb(SuperDb):
    __tablename__ = "readings"

    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id"))
    value: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    device: Mapped["DeviceDb"] = relationship(
        "DeviceDb", back_populates="readings")


class NotificationDb(SuperDb):
    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(String, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        SqlEnum(NotificationType), nullable=False)

    user: Mapped["UserDb"] = relationship(
        "UserDb", back_populates="notifications")


class EspDeviceDb(SuperDb):
    __tablename__ = "esp_devices"

    mac: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    secret: Mapped[str] = mapped_column(String, nullable=False)

    client_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    client_crt: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    garden_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("gardens.id"), nullable=True
    )
    garden: Mapped[Optional["GardenDb"]] = relationship(
        "GardenDb", back_populates="esp_devices"
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    user: Mapped[Optional["UserDb"]] = relationship("UserDb")

    devices: Mapped[list["DeviceDb"]] = relationship(
        "DeviceDb", back_populates="esp", cascade="all, delete-orphan"
    )
