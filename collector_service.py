import os
import redis
import json
import logging

# Logger Yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Redis Bağlantısı
REDIS_HOST = os.getenv("REDIS_HOST", "redis_db")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


def start_collector():
    pubsub = r.pubsub()
    pubsub.subscribe('weather_updates')

    logger.info("Collector servisi 'weather_updates' kanalını dinlemeye başladı...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                city = data['location']['name'].lower()

                # Veriyi Redis'e kalıcı olarak yazıyoruz
                r.set(f"weather:hourly:{city}", json.dumps(data))

                logger.info(f"Collector: {city.capitalize()} verisi Redis'e başarıyla kaydedildi.")
            except Exception as e:
                logger.error(f"Collector veri işlerken hata oluştu: {e}")


if __name__ == "__main__":
    start_collector()