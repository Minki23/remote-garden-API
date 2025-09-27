import httpx
from datetime import datetime
from typing import List, Optional
from models.schedule import ScheduleDTO
from models.reading import ReadingDTO
from models.device import DeviceDTO
from models.enums import ScheduleActionType, DeviceType, ControlActionType

CONTROL_MAP: dict[tuple[DeviceType, ControlActionType], str] = {
    (DeviceType.WATERER, ControlActionType.WATER_ON): "water/on",
    (DeviceType.WATERER, ControlActionType.WATER_OFF): "water/off",
    (DeviceType.ATOMIZER, ControlActionType.ATOMIZE_ON): "atomizer/on",
    (DeviceType.ATOMIZER, ControlActionType.ATOMIZE_OFF): "atomizer/off",
    (DeviceType.FANNER, ControlActionType.FAN_ON): "fan/on",
    (DeviceType.FANNER, ControlActionType.FAN_OFF): "fan/off",
    (DeviceType.HEATER, ControlActionType.HEATING_MAT_ON): "heating-mat/on",
    (DeviceType.HEATER, ControlActionType.HEATING_MAT_OFF): "heating-mat/off",
}


class BackendAgentClient:
    """Client for communicating with the backend API for schedules, readings and devices.

    This client wraps asynchronous HTTP requests to the backend service
    and provides high-level methods for managing schedules, retrieving sensor
    readings, listing devices, and sending control commands.
    """

    def __init__(self, garden_id: int, base_url: str = "http://backend:8000", access_token: str | None = None):
        """Initialize the backend agent client.

        Args:
            garden_id (int): The ID of the garden to operate on.
            base_url (str, optional): Backend base URL. Defaults to ``"http://backend:8000"``.
            access_token (str, optional): Bearer access token for authorization. Defaults to ``None``.
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.garden_id = garden_id

    def _headers(self) -> dict:
        """Build HTTP headers with authorization.

        Returns:
            dict: Headers including the Bearer token.

        Raises:
            Exception: If no access token is provided.
        """
        if not self.access_token:
            raise Exception("Missing access token for BackendAgentClient")
        return {"Authorization": f"Bearer {self.access_token}"}

    async def list_schedules(self) -> List[ScheduleDTO]:
        """Retrieve all schedules for the current garden.

        Returns:
            List[ScheduleDTO]: A list of schedules.

        Raises:
            Exception: If the backend responds with an error.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/schedules/{self.garden_id}/", headers=self._headers())
        if resp.status_code != 200:
            raise Exception(f"Backend error: {resp.text}")
        return [ScheduleDTO(**item) for item in resp.json()]

    async def create_schedule(self, cron: str, action: ScheduleActionType) -> str:
        """Create a new schedule for the garden.

        Args:
            cron (str): Cron expression for scheduling.
            action (ScheduleActionType): The action to be executed.

        Returns:
            str: The ID of the created schedule task.

        Raises:
            Exception: If the backend responds with an error.
        """
        payload = {"cron": cron, "action": action.value}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/schedules/{self.garden_id}/", headers=self._headers(), json=payload
            )
        if resp.status_code != 200:
            raise Exception(f"Backend error: {resp.text}")
        return resp.json()["task_id"]

    async def update_schedule(self, task_id: str, cron: str) -> None:
        """Update an existing schedule.

        Args:
            task_id (str): The ID of the schedule task.
            cron (str): New cron expression.

        Raises:
            Exception: If the backend responds with an error.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.base_url}/schedules/{task_id}/", headers=self._headers(), json={"cron": cron}
            )
        if resp.status_code != 204:
            raise Exception(f"Backend error: {resp.text}")

    async def delete_schedule(self, task_id: str) -> None:
        """Delete a schedule.

        Args:
            task_id (str): The ID of the schedule task.

        Raises:
            Exception: If the backend responds with an error.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self.base_url}/schedules/{task_id}/", headers=self._headers())
        if resp.status_code != 204:
            raise Exception(f"Backend error: {resp.text}")

    async def get_readings(
        self,
        device_type: DeviceType,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ReadingDTO]:
        """Get readings for a given device type in the garden.

        Args:
            device_type (DeviceType): The type of device to fetch readings for.
            start_time (datetime, optional): Start of the time range.
            end_time (datetime, optional): End of the time range.
            offset (int, optional): Pagination offset. Defaults to 0.
            limit (int, optional): Pagination limit. Defaults to 100.

        Returns:
            list[ReadingDTO]: A list of readings.

        Raises:
            Exception: If the backend responds with an error.
        """
        params = {
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "offset": offset,
            "limit": limit,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/readings/garden/{self.garden_id}/device-type/{device_type.value}",
                headers=self._headers(),
                params=params,
            )
        if resp.status_code != 200:
            raise Exception(f"Backend error: {resp.text}")
        return [ReadingDTO(**item) for item in resp.json()]

    async def get_last_reading(self, device_type: DeviceType) -> ReadingDTO:
        """Get the last reading for a given device type.

        Args:
            device_type (DeviceType): The type of device.

        Returns:
            ReadingDTO: The latest reading.

        Raises:
            Exception: If the backend responds with an error.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/readings/garden/{self.garden_id}/device-type/{device_type.value}/last",
                headers=self._headers(),
            )
        if resp.status_code != 200:
            raise Exception(f"Backend error: {resp.text}")
        return ReadingDTO(**resp.json())

    async def get_devices(self) -> list[DeviceDTO]:
        """Get all devices registered in the garden.

        Returns:
            list[DeviceDTO]: A list of devices.

        Raises:
            Exception: If the backend responds with an error.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/devices/garden/{self.garden_id}", headers=self._headers())
        if resp.status_code != 200:
            raise Exception(f"Backend error: {resp.text}")
        return [DeviceDTO(**item) for item in resp.json()]

    async def control_device(
        self,
        device_type: DeviceType,
        action_type: ControlActionType,
    ) -> bool:
        """Send a control command to a device in the garden.

        Args:
            device_type (DeviceType): The type of device to control.
            action_type (ControlActionType): The control action to perform.

        Returns:
            bool: ``True`` if the action was successful, otherwise ``False``.

        Raises:
            Exception: If the backend responds with an error or action is unsupported.
        """
        path = CONTROL_MAP.get((device_type, action_type))
        if not path:
            raise Exception(
                f"Unsupported action for {device_type} {action_type}")

        url = f"{self.base_url}/devices/garden/{self.garden_id}/{path}"

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self._headers())

        if resp.status_code != 200:
            raise Exception(f"Backend error: {resp.text}")

        return resp.json()
