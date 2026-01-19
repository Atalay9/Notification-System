import os
import redis
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis_db")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def send_email_notification(city, temp, threshold):
    api_key = os.getenv("MAILGUN_API_KEY")
    domain = os.getenv("MAILGUN_DOMAIN")
    receiver_email = os.getenv("EMAIL_RECEIVER")
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    logger.info(f"İstek atılan URL: {url}")

    if domain is None:
        logger.error("KRİTİK HATA: .env dosyasından MAILGUN_DOMAIN okunamadı!")
        return

    try:
        response = requests.post(
            url,
            auth=("api", api_key),
            data={
                "from": f"Hava Durumu Alarmı <mailgun@{domain}>",
                "to": [receiver_email],
                "subject": f"KRİTİK HAVA DURUMU: {city}",
                "text": f"DİKKAT! {city} için sıcaklık {temp}°C ölçüldü. Eşik değer ({threshold}°C) aşıldı!"
            }
        )

        if response.status_code == 200:
            logger.info(f"Mailgun üzerinden mail başarıyla gönderildi!")
        else:
            logger.error(f"Mailgun hatası: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Mail gönderilirken teknik bir hata oluştu: {e}")


def start_alarm_service():
    pubsub = r.pubsub()
    pubsub.subscribe('weather_updates')

    logger.info("Alarm servisi aktif, kritik değişimleri izliyor.")

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            city = data['location']['name']
            temp = data['current']['temp_c']

            # Redis'ten değeri çekiyoruz.
            raw_threshold = r.get("weather_threshold")
            threshold = float(raw_threshold) if raw_threshold else 30.0

            logger.info(f"Yeni veri alındı: {city} | Sıcaklık: {temp}°C | Mevcut Eşik: {threshold}°C")

            # Eşik kontrolü yapıyoruz.
            if temp > threshold:
                logger.warning(f"KRİTİK DURUM! {city} SICAKLIĞI ({temp}°C) EŞİK DEĞERİNİ ({threshold}°C) AŞTI!")
                send_email_notification(city, temp, threshold)
            else:
                logger.info(f"Sıcaklık normal sınırlarda.")


if __name__ == "__main__":
    start_alarm_service()