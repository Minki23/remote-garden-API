import logging
import base64
from pathlib import Path
from datetime import datetime
from core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler

logger = logging.getLogger(__name__)

class CameraFrameHandler(BaseMqttCallbackHandler):
    def __init__(self, save_frames: bool = False, output_dir: str = "./frames"):
        super().__init__("{mac}/device/camera/frame/{index}")
        self.save_frames = save_frames
        self.output_dir = Path(output_dir)
        self.frame_count = 0
        
        if self.save_frames:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Frame output directory: {self.output_dir}")

    async def __call__(self, topic: str, payload: dict | bytes):
        """
        Process a camera frame message from an ESP device.

        Parameters
        ----------
        topic : str
            The MQTT topic containing the frame index.
        payload : dict | bytes
            Binary JPEG image data or dict with image data.
        """
        logger.info(f"[CAMERA] Received frame on topic: {topic}")

        try:
            index = self.extract_from_topic(topic, "index")
        except Exception as e:
            logger.warning(f"Could not extract index from topic {topic}: {e}")
            index = "unknown"

        # Handle binary payload
        if isinstance(payload, bytes):
            image_data = payload
        elif isinstance(payload, dict):
            # If payload is dict, might be base64 encoded
            image_data = payload.get("data", b"")
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
        else:
            logger.warning(f"Unexpected payload type: {type(payload)}")
            return

        # Verify we have data
        if not image_data:
            logger.warning("No image data received")
            return

        # Log frame info
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        size_kb = len(image_data) / 1024
        
        logger.info("=" * 60)
        logger.info("CAMERA FRAME RECEIVED")
        logger.info(f"   Timestamp: {timestamp}")
        logger.info(f"   Topic:     {topic}")
        logger.info(f"   Index:     {index}")
        logger.info(f"   Size:      {size_kb:.2f} KB ({len(image_data)} bytes)")
        logger.info(f"   Format:    JPEG")

        self.frame_count += 1

        # Verify JPEG header
        if len(image_data) >= 2:
            is_jpeg = image_data[0] == 0xFF and image_data[1] == 0xD8
            logger.info(f"   Valid JPEG: {'Yes' if is_jpeg else 'No'}")
            if not is_jpeg:
                logger.warning("Received data is not a valid JPEG image")
        
        # Save to disk if enabled
        if self.save_frames and image_data:
            filename = f"frame_{index}_{timestamp}.jpg"
            filepath = self.output_dir / filename
            
            try:
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                logger.info(f"   Saved to:  {filepath}")
            except Exception as e:
                logger.error(f"Failed to save frame: {e}")
        
        logger.info("=" * 60)