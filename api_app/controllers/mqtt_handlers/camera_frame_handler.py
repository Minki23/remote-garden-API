import logging
import base64
from pathlib import Path
from datetime import datetime
from PIL import Image
import numpy as np
from core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler

logger = logging.getLogger(__name__)


class CameraFrameHandler(BaseMqttCallbackHandler):
    """
    Improved camera frame handler with multiple RGB565 conversion variants
    """

    def __init__(
        self,
        save_frames: bool = True,
        output_dir: str = "./frames",
        frame_width: int = 96,
        frame_height: int = 96,
        save_all_variants: bool = True,
    ):
        super().__init__("{mac}/device/camera/frame/{index}/#")

        self.save_frames = save_frames
        self.output_dir = Path(output_dir)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.save_all_variants = save_all_variants
        self.partial_frames = {}

        if self.save_frames:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Frame output directory: {self.output_dir}")
            if self.save_all_variants:
                logger.info("⚠️  DEBUG MODE: Saving all conversion variants")

    def _convert_rgb565_variant_1_big_endian(self, image_data: bytes) -> np.ndarray:
        """Original conversion - big endian RGB565"""
        arr = np.frombuffer(image_data, dtype=">u2").reshape(
            (self.frame_height, self.frame_width))

        r5 = (arr >> 11) & 0x1F
        g6 = (arr >> 5) & 0x3F
        b5 = arr & 0x1F

        r8 = ((r5 * 255 + 15) // 31).astype(np.uint8)
        g8 = ((g6 * 255 + 31) // 63).astype(np.uint8)
        b8 = ((b5 * 255 + 15) // 31).astype(np.uint8)

        return np.stack([r8, g8, b8], axis=-1)

    def _convert_rgb565_variant_2_little_endian(self, image_data: bytes) -> np.ndarray:
        """Little endian RGB565 (more common for ESP32)"""
        arr = np.frombuffer(image_data, dtype="<u2").reshape(
            (self.frame_height, self.frame_width))

        r5 = (arr >> 11) & 0x1F
        g6 = (arr >> 5) & 0x3F
        b5 = arr & 0x1F

        r8 = ((r5 * 255 + 15) // 31).astype(np.uint8)
        g8 = ((g6 * 255 + 31) // 63).astype(np.uint8)
        b8 = ((b5 * 255 + 15) // 31).astype(np.uint8)

        return np.stack([r8, g8, b8], axis=-1)

    def _convert_rgb565_variant_3_byte_swapped(self, image_data: bytes) -> np.ndarray:
        """Byte-swapped RGB565"""
        # Swap every pair of bytes
        swapped = bytearray(image_data)
        for i in range(0, len(swapped) - 1, 2):
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]

        arr = np.frombuffer(swapped, dtype=">u2").reshape(
            (self.frame_height, self.frame_width))

        r5 = (arr >> 11) & 0x1F
        g6 = (arr >> 5) & 0x3F
        b5 = arr & 0x1F

        r8 = ((r5 * 255 + 15) // 31).astype(np.uint8)
        g8 = ((g6 * 255 + 31) // 63).astype(np.uint8)
        b8 = ((b5 * 255 + 15) // 31).astype(np.uint8)

        return np.stack([r8, g8, b8], axis=-1)

    def _convert_rgb565_variant_4_bgr_order(self, image_data: bytes) -> np.ndarray:
        """BGR order instead of RGB"""
        arr = np.frombuffer(image_data, dtype="<u2").reshape(
            (self.frame_height, self.frame_width))

        r5 = (arr >> 11) & 0x1F
        g6 = (arr >> 5) & 0x3F
        b5 = arr & 0x1F

        r8 = ((r5 * 255 + 15) // 31).astype(np.uint8)
        g8 = ((g6 * 255 + 31) // 63).astype(np.uint8)
        b8 = ((b5 * 255 + 15) // 31).astype(np.uint8)

        # Return BGR instead of RGB
        return np.stack([b8, g8, r8], axis=-1)

    def _convert_rgb565_variant_5_transposed(self, image_data: bytes) -> np.ndarray:
        """Try different width/height interpretation"""
        arr = np.frombuffer(image_data, dtype="<u2").reshape(
            (self.frame_width, self.frame_height))

        r5 = (arr >> 11) & 0x1F
        g6 = (arr >> 5) & 0x3F
        b5 = arr & 0x1F

        r8 = ((r5 * 255 + 15) // 31).astype(np.uint8)
        g8 = ((g6 * 255 + 31) // 63).astype(np.uint8)
        b8 = ((b5 * 255 + 15) // 31).astype(np.uint8)

        rgb = np.stack([r8, g8, b8], axis=-1)
        return np.transpose(rgb, (1, 0, 2))  # Transpose back

    def _convert_rgb565_variant_6_raw_bytes(self, image_data: bytes) -> np.ndarray:
        """Interpret as raw byte stream and try to recover"""
        # Try interpreting every 2 bytes as a pixel
        pixels = []
        for i in range(0, len(image_data) - 1, 2):
            # Little endian interpretation
            pixel = image_data[i] | (image_data[i + 1] << 8)

            r5 = (pixel >> 11) & 0x1F
            g6 = (pixel >> 5) & 0x3F
            b5 = pixel & 0x1F

            r8 = (r5 * 255 + 15) // 31
            g8 = (g6 * 255 + 31) // 63
            b8 = (b5 * 255 + 15) // 31

            pixels.append([r8, g8, b8])

        # Reshape to image dimensions
        total_pixels = self.frame_width * self.frame_height
        if len(pixels) >= total_pixels:
            arr = np.array(pixels[:total_pixels], dtype=np.uint8)
            return arr.reshape((self.frame_height, self.frame_width, 3))
        else:
            # Pad with zeros if not enough pixels
            while len(pixels) < total_pixels:
                pixels.append([0, 0, 0])
            arr = np.array(pixels, dtype=np.uint8)
            return arr.reshape((self.frame_height, self.frame_width, 3))

    async def __call__(self, topic: str, payload: dict | bytes):
        logger.debug(f"[CAMERA] Received data on topic: {topic}")

        # Clean partial frame buffer if too large
        if len(self.partial_frames) > 50:
            logger.warning(
                "Cleaning partial frame buffer (too many incomplete frames)")
            self.partial_frames.clear()

        # Handle fragments /part/N
        if "/part/" in topic:
            try:
                frame_id = self.extract_from_topic(topic, "index")
                part_number = int(topic.split("/part/")[1])
            except Exception as e:
                logger.warning(f"Cannot parse part topic '{topic}': {e}")
                return

            if isinstance(payload, bytes):
                chunk = payload
            elif isinstance(payload, dict):
                data = payload.get("data")
                chunk = base64.b64decode(
                    data) if isinstance(data, str) else data
            else:
                return

            if not chunk:
                return

            self.partial_frames.setdefault(frame_id, [])
            self.partial_frames[frame_id].append((part_number, chunk))
            logger.info(
                f"📦 Received part {part_number} for frame {frame_id} ({len(chunk)} bytes)")
            return

        # Handle end /end
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
                f"🧩 Assembled full frame {frame_id}: {len(image_data)} bytes, {len(parts)} parts")
            await self._handle_full_frame(frame_id, image_data, topic)
            return

        # Handle full frame (no fragmentation)
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

        # Detect JPEG
        is_jpeg = len(image_data) > 2 and image_data[:2] == b"\xFF\xD8"
        fmt = "JPEG" if is_jpeg else "RGB565"
        logger.info(f"   Format:    {fmt}")

        # Debug: Print first few bytes
        if len(image_data) >= 16:
            hex_start = ' '.join(f'{b:02X}' for b in image_data[:16])
            logger.info(f"   First 16 bytes: {hex_start}")

        if not self.save_frames:
            return

        try:
            if fmt == "JPEG":
                path = self.output_dir / f"frame_{index}_{timestamp}.jpg"
                with open(path, "wb") as f:
                    f.write(image_data)
                logger.info(f"✓ Saved JPEG: {path}")

            else:
                expected_size = self.frame_width * self.frame_height * 2
                logger.info(
                    f"Expected size: {expected_size}, actual: {len(image_data)}")

                if len(image_data) != expected_size:
                    logger.warning(
                        f"Size mismatch! Expected {expected_size}, got {len(image_data)}")
                    if len(image_data) > expected_size:
                        image_data = image_data[:expected_size]
                        logger.info(f"Truncated to {expected_size} bytes")
                    else:
                        padding = expected_size - len(image_data)
                        image_data += b"\x00" * padding
                        logger.info(f"Padded with {padding} zero bytes")

                if self.save_all_variants:
                    variants = [
                        ("v1_big_endian", self._convert_rgb565_variant_1_big_endian,
                         "Big Endian RGB565"),
                        ("v2_little_endian", self._convert_rgb565_variant_2_little_endian,
                         "Little Endian RGB565 (ESP32 common)"),
                        ("v3_byte_swapped", self._convert_rgb565_variant_3_byte_swapped,
                         "Byte-swapped RGB565"),
                        ("v4_bgr_order",
                         self._convert_rgb565_variant_4_bgr_order, "BGR order"),
                        ("v5_transposed", self._convert_rgb565_variant_5_transposed,
                         "Transposed dimensions"),
                        ("v6_raw_bytes", self._convert_rgb565_variant_6_raw_bytes,
                         "Raw byte interpretation"),
                    ]

                    logger.info(
                        f"🔬 Saving {len(variants)} conversion variants...")
                    for name, func, desc in variants:
                        try:
                            rgb = func(image_data)
                            img = Image.fromarray(rgb)
                            file = self.output_dir / \
                                f"frame_{index}_{timestamp}_{name}.png"
                            img.save(file)
                            logger.info(f"   ✓ {name} ({desc}) → {file.name}")
                        except Exception as e:
                            logger.error(f"   ✗ {name} failed: {e}")

                    logger.info(
                        "💡 Check which variant looks correct and update your conversion function.")
                else:
                    # Use the most likely variant for ESP32 (little endian)
                    rgb = self._convert_rgb565_variant_2_little_endian(
                        image_data)
                    img = Image.fromarray(rgb)
                    file = self.output_dir / f"frame_{index}_{timestamp}.png"
                    img.save(file)
                    logger.info(f"✓ Saved RGB565 → PNG: {file}")

        except Exception as e:
            logger.error(f"✗ Error saving frame {index}: {e}")
            import traceback
            logger.error(traceback.format_exc())

        logger.info("=" * 60)
