from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.config import CONFIG

import time
import cv2
import av

router = APIRouter()


def get_frame_generator():
    if CONFIG.USE_MOCK_CAMERA:
        cap = cv2.VideoCapture(0)

        def frame_gen():
            while True:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue
                ret, jpeg = cv2.imencode(".jpg", frame)
                if not ret:
                    continue
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
                )

        return frame_gen()

    else:
        container = av.open(CONFIG.RTSP_URL, options={"rtsp_transport": "tcp"})
        stream = container.streams.video[0]

        def frame_gen():
            for packet in container.demux(stream):
                for frame in packet.decode():
                    img = frame.to_ndarray(format="bgr24")
                    ret, jpeg = cv2.imencode(".jpg", img)
                    if not ret:
                        continue
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
                    )

        return frame_gen()


@router.get("/video")
async def video_feed():
    return StreamingResponse(
        get_frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame"
    )
