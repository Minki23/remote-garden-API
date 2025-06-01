from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from app.core.websocket.websocket_manager import websocket_manager
from app.core.dependencies import CurrentUserDep

import logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/wsinit")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("Connection to websocket started")
    user_id = await websocket_manager.authenticate_and_connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(user_id, websocket)
