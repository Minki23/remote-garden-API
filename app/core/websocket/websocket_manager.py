from app.core.security.deps import get_current_user_id
from fastapi import WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from typing import Dict, Set
from collections import defaultdict
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        # user_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        self.lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections[user_id].add(websocket)
        logger.info(
            f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}"
        )

    async def disconnect(self, user_id: int, websocket: WebSocket):
        async with self.lock:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected.")

    async def send_to_user(self, user_id: int, data: dict):
        message = json.dumps(data)
        async with self.lock:
            sockets = list(self.active_connections.get(user_id, []))
        if not sockets:
            logger.debug(
                f"No active WebSocket connections for user {user_id}.")
            return

        for socket in sockets:
            try:
                await socket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to user {user_id}: {e}")
                await self.disconnect(user_id, socket)

    async def authenticate_and_connect(self, websocket: WebSocket) -> int | None:
        """Extracts user ID from WebSocket headers and connects the socket."""
        auth_header = websocket.query_params.get("authorization")
        scheme, token = get_authorization_scheme_param(auth_header)

        if scheme.lower() != "bearer" or not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning("Close connection due to missing Bearer token")
            return None

        try:
            credentials = HTTPAuthorizationCredentials(
                scheme=scheme, credentials=token)
            user_id = await get_current_user_id(credentials)
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning("Close connection due to authentication issue")
            return None

        await self.connect(user_id, websocket)
        return user_id


websocket_manager = WebSocketManager()
