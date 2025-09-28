import httpx
from exceptions.scheme import AppException
from core.config import CONFIG


class AgentClient:
    """
    Client for communicating with the Agent microservice.
    """

    async def trigger(
        self,
        refresh_token: str,
        garden_id: int,
        context: str | None = None
    ) -> dict:
        """
        Trigger the Agent to perform automation tasks for a given garden.

        This method sends a POST request to the Agent App with the user's
        refresh token, the garden ID, and optionally a context string.
        If the request succeeds, it returns the Agent's JSON response.
        Otherwise, it raises an exception.

        Parameters
        ----------
        refresh_token : str
            The refresh token of the authenticated user.
        garden_id : int
            Identifier of the garden to trigger automation for.
        context : str, optional
            Additional context string passed to the Agent App.

        Returns
        -------
        dict
            Parsed JSON response from the Agent service.

        Raises
        ------
        AppException
            If the Agent service returns a non-200 status code
            or if the response is not valid JSON.
        """
        payload = {
            "refresh_token": refresh_token,
            "garden_id": garden_id,
        }
        if context is not None:
            payload["context"] = context

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{CONFIG.BASE_AGENT_URL}/agent/trigger",
                json=payload
            )

        if resp.status_code != 200:
            raise AppException(f"Agent service error: {resp.text}")

        try:
            return resp.json()
        except Exception:
            raise AppException("Invalid response from Agent service")
