from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.websocket.websocket_manager import websocket_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/wsinit")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for initializing a real-time connection with a user.

    This endpoint authenticates the user, registers the WebSocket connection
    with the WebSocket manager, and keeps the connection alive. All incoming
    messages are ignored (or could be extended for custom handling).

    Parameters
    ----------
    websocket : WebSocket
        The WebSocket connection object provided by FastAPI.
    """
    logger.info("Connection to websocket started")
    user_id = await websocket_manager.authenticate_and_connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(user_id, websocket)
