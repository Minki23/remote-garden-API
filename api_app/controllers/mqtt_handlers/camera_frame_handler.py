import logging
import base64
import struct
from pathlib import Path
from datetime import datetime
from PIL import Image
import numpy as np
from core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler

logger = logging.getLogger(__name__)

class CameraFrameHandler(BaseMqttCallbackHandler):
    def __init__(self, save_frames: bool = True, output_dir: str = "./frames", frame_width: int = 96, frame_height: int = 96):
        super().__init__("{mac}/device/camera/frame/{index}")
        self.save_frames = save_frames
        self.output_dir = Path(output_dir)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = 0
        
        if self.save_frames:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Frame output directory: {self.output_dir}")

    async def __call__(self, topic: str, payload: dict | bytes):
        logger.info(f"[CAMERA] Received frame on topic: {topic}")

        try:
            index = self.extract_from_topic(topic, "index")
        except Exception as e:
            logger.warning(f"Could not extract index from topic {topic}: {e}")
            index = "unknown"

        if isinstance(payload, bytes):
            image_data = payload
        elif isinstance(payload, dict):
            image_data = payload.get("data", b"")
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
        else:
            logger.warning(f"Unexpected payload type: {type(payload)}")
            return

        if not image_data:
            logger.warning("No image data received")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        size_kb = len(image_data) / 1024
        logger.info("=" * 60)
        logger.info("CAMERA FRAME RECEIVED")
        logger.info(f"   Timestamp: {timestamp}")
        logger.info(f"   Topic:     {topic}")
        logger.info(f"   Index:     {index}")
        logger.info(f"   Size:      {size_kb:.2f} KB ({len(image_data)} bytes)")

        is_jpeg = len(image_data) > 2 and image_data[0] == 0xFF and image_data[1] == 0xD8
        if is_jpeg:
            fmt = "JPEG"
        else:
            fmt = "RGB565"
        logger.info(f"   Detected format: {fmt}")

        self.frame_count += 1

        if self.save_frames:
            try:
                if fmt == "JPEG":
                    filename = f"frame_{index}_{timestamp}.jpg"
                    filepath = self.output_dir / filename
                    with open(filepath, "wb") as f:
                        f.write(image_data)
                    logger.info(f"   Saved JPEG frame to: {filepath}")

                else:
                    arr = np.frombuffer(image_data, dtype=np.uint16).reshape((self.frame_height, self.frame_width))
                    r = ((arr >> 11) & 0x1F) << 3
                    g = ((arr >> 5) & 0x3F) << 2
                    b = (arr & 0x1F) << 3
                    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)

                    img = Image.fromarray(rgb, "RGB")
                    filename = f"frame_{index}_{timestamp}.bmp"
                    filepath = self.output_dir / filename
                    img.save(filepath)
                    logger.info(f"   Saved RGB565 frame as BMP: {filepath}")

            except Exception as e:
                logger.error(f"Failed to process frame: {e}")

        logger.info("=" * 60)
