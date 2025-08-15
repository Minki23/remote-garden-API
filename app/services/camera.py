from aiortc import MediaStreamTrack
from fractions import Fraction
import time, asyncio
import av
import cv2
from app.core.config import CONFIG


class VideoTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()
        self.container = av.open(CONFIG.RTSP_URL, options={"rtsp_transport": "tcp"})
        self.stream = self.container.streams.video[0]
        self._start = time.time()

    async def recv(self):
        timestamp = int((time.time() - self._start) * 90000)
        for packet in self.container.demux(self.stream):
            for frame in packet.decode():
                frame.pts = timestamp
                frame.time_base = Fraction(1, 90000)
                return frame


class MockVideoTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self._start = time.time()

    async def recv(self):
        pts = int((time.time() - self._start) * 90000)
        ret, frame = self.cap.read()
        if not ret:
            await asyncio.sleep(1 / 30)
            return await self.recv()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = av.VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = Fraction(1, 90000)
        return video_frame
