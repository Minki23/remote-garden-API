from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from os import getenv


@dataclass(frozen=True)
class Config:
    DB_CONNECTION_STRING: str
    COOKIES_KEY_NAME: str
    SESSION_TIME: timedelta
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AGENT_TRIGGER: int = 2
    SECRET_KEY: str = getenv("SECRET", "default_secret_key")

    GOOGLE_CLIENT_ID: str = getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = getenv("GOOGLE_REDIRECT_URI")
    BASE_AGENT_URL: str = getenv("BASE_AGENT_URL")
    BASE_CSR_URL: str = getenv("BASE_CSR_URL")
    RTSP_URL: str = getenv("RTSP_URL")
    REDIS_HOST: str = getenv("REDIS_HOST")
    MQTT_BROKER_HOST: str = getenv("MQTT_BROKER_HOST")
    MQTT_BROKER_PORT: str = getenv("MQTT_BROKER_PORT")
    USE_MOCK_CAMERA: bool = False

    @staticmethod
    def get_config() -> Config:
        db_connection_string = getenv(
            "DB_CONNECTION_STRING", "sqlite:///db.sqlite")
        if db_connection_string == "":
            raise ValueError(
                "Environment variable 'DB_CONNECTION_STRING' must be set and cannot be empty. "
            )

        cookies_key_name = "session_token"
        session_time = timedelta(days=30)
        use_mock = getenv("USE_MOCK_CAMERA", "0").lower() in (
            "1", "true", "yes")

        return Config(
            db_connection_string,
            cookies_key_name,
            session_time,
            USE_MOCK_CAMERA=use_mock,
        )


CONFIG = Config.get_config()
