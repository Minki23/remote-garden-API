import os
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _init_firebase():
    """
    Initialize the Firebase Admin SDK once using a service account JSON file.

    Logs an error if the service account file is missing or initialization fails.
    """
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
    """
    Wrapper for sending push notifications via Firebase.
    """

    def __init__(self):
        """
        Initialize FirebaseWrapper.

        Ensures Firebase is initialized before sending any notifications.
        """
        _init_firebase()

    async def send_to_tokens(
        self,
        tokens: list[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
    ):
        """
        Send a push notification to the specified device tokens.

        Parameters
        ----------
        tokens : list[str]
            List of device registration tokens to receive the notification.
        title : str
            Notification title.
        body : str
            Notification body.
        data : Optional[dict]
            Optional key-value payload to send alongside the notification.

        Returns
        -------
        response
            Firebase response object if successful, None otherwise.
        """
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
