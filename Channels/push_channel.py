from .base_channel import AlarmChannel
import logging

logger = logging.getLogger(__name__)

class PushChannel(AlarmChannel):
    def send(self, message: str):
        logger.info(f"[PUSH NOTIFICATION]: {message}")
        return True