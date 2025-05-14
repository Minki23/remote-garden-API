from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, DateTime, Enum as SqlEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship, Mapped
from .enums import DeviceType, NotificationType
from sqlalchemy import Column, Enum
import enum

Base = declarative_base()


class UserDb(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    gardens: Mapped[list["GardenDb"]] = relationship("GardenDb", back_populates="user")
    notifications: Mapped[list["NotificationDb"]] = relationship(
        "NotificationDb", back_populates="user"
    )


class GardenDb(Base):
    __tablename__ = "gardens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    send_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_automation: Mapped[bool] = mapped_column(Boolean, default=False)
    use_fahrenheit: Mapped[bool] = mapped_column(Boolean, default=False)


    user: Mapped["UserDb"] = relationship("UserDb", back_populates="gardens")
    devices: Mapped[list["DeviceDb"]] = relationship(
        "DeviceDb", back_populates="garden", cascade="all, delete-orphan"
    )


class DeviceDb(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    garden_id: Mapped[int] = mapped_column(Integer, ForeignKey("gardens.id"))
    mac: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[DeviceType] = mapped_column(SqlEnum(DeviceType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    garden: Mapped["GardenDb"] = relationship("GardenDb", back_populates="devices")
    readings: Mapped[list["ReadingDb"]] = relationship(
        "ReadingDb", back_populates="device", cascade="all, delete-orphan"
    )


class ReadingDb(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id"))
    value: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["DeviceDb"] = relationship("DeviceDb", back_populates="readings")


class NotificationDb(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(String, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, nullable=False)
    type: Mapped[NotificationType] = mapped_column(SqlEnum(NotificationType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["UserDb"] = relationship("UserDb", back_populates="notifications")
