from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription
from app.services.camera import VideoTrack, MockVideoTrack
import logging
from app.core.config import CONFIG


router = APIRouter()
pcs = set()
logger = logging.getLogger(__name__)

@router.post("/offer")
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("Connection: %s", pc.connectionState)
        if pc.connectionState == "closed":
            pcs.discard(pc)

    track = MockVideoTrack() if CONFIG.USE_MOCK_CAMERA else VideoTrack()
    pc.addTrack(track)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return JSONResponse({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })
