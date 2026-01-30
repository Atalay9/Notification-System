import requests
import os
import logging
from .base_channel import AlarmChannel

logger = logging.getLogger(__name__)


class EmailChannel(AlarmChannel):
    def __init__(self):
        self.api_key = os.getenv("MAILGUN_API_KEY")
        self.api_url = os.getenv("MAILGUN_API_URL")
        self.domain = os.getenv("MAILGUN_DOMAIN")
        self.receiver = os.getenv("EMAIL_RECEIVER")

    def send(self, message: str):
        if not all([self.api_key, self.domain, self.receiver]):
            logger.error("Email gönderimi için gerekli çevre değişkenleri eksik!")
            return False

        try:
            response = requests.post(
                self.api.url,
                auth=("api", self.api_key),
                data={
                    "from": f"Weather Alert System <mailgun@{self.domain}>",
                    "to": [self.receiver],
                    "subject": "Hava Durumu Alarmı!",
                    "text": message
                }
            )

            if response.status_code == 200:
                logger.info("Mailgun üzerinden mail başarıyla gönderildi!")
                return True
            else:
                logger.error(f"Mail gönderilirken hata oluştu (HTTP {response.status_code}): {response.text}")
                return False

        except Exception as e:
            logger.error(f"Email servisi bağlantı hatası: {e}")
            return False