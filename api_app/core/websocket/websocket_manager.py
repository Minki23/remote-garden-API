from fastapi import WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from typing import Dict, Set
from collections import defaultdict
import asyncio
import json
import logging

from core.security.deps import get_current_subject, SubjectType

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for users and agents.

    Provides authentication, connection handling,
    and message delivery to connected clients.
    """

    def __init__(self):
        """
        Initialize the WebSocket manager.

        Uses a lock for concurrency and a map of
        (subject_type, subject_id) to active sockets.
        """
        self.active_connections: Dict[tuple[SubjectType,
                                            int], Set[WebSocket]] = defaultdict(set)
        self.lock = asyncio.Lock()

    async def connect(self, subject_id: int, websocket: WebSocket, subject_type: SubjectType):
        """
        Accept and register a new WebSocket connection.

        Parameters
        ----------
        subject_id : int
            ID of the connected subject (user or agent).
        websocket : WebSocket
            FastAPI WebSocket instance.
        subject_type : SubjectType
            Indicates whether the subject is a USER or AGENT.
        """
        await websocket.accept()
        async with self.lock:
            self.active_connections[(subject_type, subject_id)].add(websocket)
        logger.info(
            f"{subject_type} {subject_id} connected. "
            f"Total connections: {len(self.active_connections[(subject_type, subject_id)])}"
        )

    async def disconnect(self, subject_id: int, websocket: WebSocket, subject_type: SubjectType):
        """
        Remove a WebSocket connection from the active pool.

        Deletes the subject entry if no connections remain.
        """
        async with self.lock:
            self.active_connections[(
                subject_type, subject_id)].discard(websocket)
            if not self.active_connections[(subject_type, subject_id)]:
                del self.active_connections[(subject_type, subject_id)]
        logger.info(f"{subject_type} {subject_id} disconnected.")

    async def send_to_subject(self, subject_id: int, subject_type: SubjectType, data: dict):
        """
        Send a JSON message to all sockets of a subject.

        Parameters
        ----------
        subject_id : int
            Target subject identifier.
        subject_type : SubjectType
            USER or AGENT.
        data : dict
            JSON-serializable payload to deliver.
        """
        message = json.dumps(data)
        async with self.lock:
            sockets = list(self.active_connections.get(
                (subject_type, subject_id), []))
        if not sockets:
            logger.debug(
                f"No active WebSocket connections for {subject_type} {subject_id}.")
            return

        for socket in sockets:
            try:
                await socket.send_text(message)
            except Exception as e:
                logger.warning(
                    f"Failed to send to {subject_type} {subject_id}: {e}")
                await self.disconnect(subject_id, socket, subject_type)

    async def authenticate_and_connect(self, websocket: WebSocket) -> tuple[int, SubjectType] | None:
        """
        Authenticate and register a WebSocket client.

        Reads a Bearer token from query params, validates it,
        and associates the connection with a subject.
        """
        auth_header = websocket.query_params.get("authorization")
        scheme, token = get_authorization_scheme_param(auth_header)

        if scheme.lower() != "bearer" or not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning("Close connection due to missing Bearer token")
            return None

        try:
            credentials = HTTPAuthorizationCredentials(
                scheme=scheme, credentials=token)
            subject_id, subject_type = await get_current_subject(credentials)
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning("Close connection due to authentication issue")
            return None

        await self.connect(subject_id, websocket, subject_type)
        return subject_id, subject_type

    async def send_to_user(self, user_id: int, data: dict):
        """
        Send a message to a specific user by ID.
        """
        await self.send_to_subject(user_id, SubjectType.USER, data)

    async def send_to_agent(self, agent_id: int, data: dict):
        """
        Send a message to a specific agent by ID.
        """
        await self.send_to_subject(agent_id, SubjectType.AGENT, data)


websocket_manager = WebSocketManager()
