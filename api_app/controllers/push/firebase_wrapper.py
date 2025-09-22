import os
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return

    path = "/app/firebase-service-account.json"
    if not os.path.exists(path):
        logger.error(f"Firebase service account file not found at: {path}")
        return

    try:
        cred = credentials.Certificate(path)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize Firebase: {e}")


class FirebaseWrapper:
    def __init__(self):
        _init_firebase()

    async def send_to_tokens(
        self,
        tokens: list[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
    ):
        if not _firebase_initialized:
            logger.error(
                "Firebase not initialized. Push notifications unavailable.")
            return None

        if not tokens:
            logger.warning("No tokens provided, skipping push notification.")
            return None

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                tokens=tokens,
            )
            response = messaging.send_each_for_multicast(message)
            return response
        except Exception as e:
            logger.exception(f"Error sending push notification: {e}")
            return None
