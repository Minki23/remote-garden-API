from .status_handler import DeviceStatusHandler
from .soil_sensor_handler import SoilSensorHandler
from .temperature_handler import TemperatureHandler
from .co2_handler import CO2Handler
from .light_handler import LightHandler
from .water_pump_handler import WaterPumpHandler
from .roof_handler import RoofHandler
from .heater_handler import HeaterHandler

from app.core.mqtt.mqtt_subscriber import MqttTopicSubscriber


async def subscribe_topics():
    for handler in (
        DeviceStatusHandler,
        SoilSensorHandler,
        TemperatureHandler,
        CO2Handler,
        LightHandler,
        WaterPumpHandler,
        RoofHandler,
        HeaterHandler,
    ):
        await MqttTopicSubscriber().subscribe_handler(handler())

__all__ = ["subscribe_topics"]
