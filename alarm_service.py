import os
import redis
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis_db")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


def start_alarm_service():
    pubsub = r.pubsub()
    pubsub.subscribe('weather_updates')

    logger.info("Alarm servisi aktif, kritik değişimleri izliyor.")

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            city = data['location']['name']
            temp = data['current']['temp_c']

            logger.info(f"ALARM BİLGİSİ: {city} için yeni veri alındı. Mevcut Sıcaklık: {temp}°C")


if __name__ == "__main__":
    start_alarm_service()