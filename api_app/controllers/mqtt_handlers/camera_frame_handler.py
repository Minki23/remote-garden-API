import logging
import base64
from pathlib import Path
from datetime import datetime
from common_db.enums import DeviceType
from controllers.mqtt_handlers.base_device_handler import BaseDeviceHandler


logger = logging.getLogger(__name__)


class CameraFrameHandler(BaseDeviceHandler):
    """
    Handles incoming camera frames over MQTT.
    Saves only JPEG frames and forwards them to user and agent via WebSocket.
    """

    def __init__(
        self,
        save_frames: bool = True,
        output_dir: str = "./frames",
        frame_width: int = 96,
        frame_height: int = 96,
    ):
        super().__init__("{mac}/device/camera/frame/{index}/#")

        self.save_frames = save_frames
        self.output_dir = Path(output_dir)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.partial_frames = {}

        if self.save_frames:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Frame output directory: {self.output_dir}")

    async def __call__(self, topic: str, payload: dict | bytes):
        logger.debug(f"[CAMERA] Received data on topic: {topic}")

        # clean buffer if too large
        if len(self.partial_frames) > 50:
            logger.warning(
                "Cleaning partial frame buffer (too many incomplete frames)")
            self.partial_frames.clear()

        # handle multipart frames
        if "/part/" in topic:
            try:
                frame_id = self.extract_from_topic(topic, "index")
                part_number = int(topic.split("/part/")[1])
            except Exception as e:
                logger.warning(f"Cannot parse part topic '{topic}': {e}")
                return

            chunk = None
            if isinstance(payload, bytes):
                chunk = payload
            elif isinstance(payload, dict):
                data = payload.get("data")
                chunk = base64.b64decode(
                    data) if isinstance(data, str) else data

            if not chunk:
                return

            self.partial_frames.setdefault(frame_id, [])
            self.partial_frames[frame_id].append((part_number, chunk))
            logger.info(
                f"Received part {part_number} for frame {frame_id} ({len(chunk)} bytes)")
            return

        # handle end marker for multipart
        if topic.endswith("/end"):
            try:
                frame_id = self.extract_from_topic(topic, "index")
            except Exception as e:
                logger.warning(
                    f"Cannot extract frame id from topic {topic}: {e}")
                return

            if frame_id not in self.partial_frames:
                logger.warning(
                    f"Frame {frame_id} /end received but no parts stored")
                return

            parts = sorted(self.partial_frames[frame_id], key=lambda x: x[0])
            image_data = b"".join(chunk for _, chunk in parts)
            del self.partial_frames[frame_id]

            logger.info(
                f"Assembled full frame {frame_id}: {len(image_data)} bytes, {len(parts)} parts")
            await self._handle_full_frame(frame_id, image_data, topic)
            return

        # single-frame payload
        if isinstance(payload, bytes):
            image_data = payload
        elif isinstance(payload, dict):
            data = payload.get("data")
            image_data = base64.b64decode(
                data) if isinstance(data, str) else data
        else:
            return

        await self._handle_full_frame("single", image_data, topic)

    async def _handle_full_frame(self, index: str, image_data: bytes, topic: str):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        size_kb = len(image_data) / 1024

        logger.info("=" * 60)
        logger.info(f"CAMERA FRAME {index}")
        logger.info(f"   Topic:     {topic}")
        logger.info(f"   Size:      {size_kb:.2f} KB")
        logger.info(f"   Timestamp: {timestamp}")

        # detect JPEG format
        is_jpeg = len(image_data) > 2 and image_data[:2] == b"\xFF\xD8"
        fmt = "JPEG" if is_jpeg else "RGB565"
        logger.info(f"   Format:    {fmt}")

        if not is_jpeg:
            logger.debug("Non-JPEG frame ignored.")
            return

        if len(image_data) >= 16:
            hex_start = ' '.join(f'{b:02X}' for b in image_data[:16])
            logger.info(f"   First 16 bytes: {hex_start}")

        if not self.save_frames:
            return

        try:
            # --- ORIGINAL JPEG SAVE LOGIC (unchanged) ---
            path = self.output_dir / f"frame_{index}_{timestamp}.jpg"
            with open(path, "wb") as f:
                f.write(image_data)
            logger.info(f"Saved JPEG: {path}")
            # ---------------------------------------------

            # --- Send to user & agent via WebSocket ---
            try:
                parts = topic.split("/")
                mac = parts[1] if len(parts) > 1 else None
                if not mac:
                    logger.warning(f"Cannot extract MAC from topic: {topic}")
                    return

                await self.process_device_event(
                    topic=topic,
                    mac=mac,
                    device_type=DeviceType.CAMERA,
                    payload={},
                    websocket_event="camera_frame",
                    extra_fields={
                        "timestamp": timestamp,
                        "image_base64": base64.b64encode(image_data).decode("utf-8"),
                        "format": "jpg",
                    },
                )
            except Exception as e:
                logger.error(f"WebSocket send failed: {e}")

        except Exception as e:
            logger.error(f"Error saving frame {index}: {e}", exc_info=True)

        logger.info("=" * 60)
