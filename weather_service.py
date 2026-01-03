import os
import requests
import logging
import redis
import json
import time

# Logger kullanımı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Key Environment Variables'dan geliyor
API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL", "http://api.weatherapi.com/v1/forecast.json")
CITY = "Adana"

# Redis bağlantı bilgileri
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Redis bağlantısının kurulumu
try:
    cache = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)
    logger.info("Redis bağlantısı başarılı.")
except Exception as e:
    logger.error(f"Redis'e bağlanılamadı: {e}")


def get_hourly_weather():
    if not API_KEY:
        logger.error("API_KEY bulunamadı!")
        return

    while True:
        try:
            params = {"key": API_KEY, "q": CITY, "days": 1, "aqi": "no", "lang": "tr"}

            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            hourly_data = data['forecast']['forecastday'][0]['hour']

            cache_key = f"weather:hourly:{CITY.lower()}"
            cache.set(cache_key, json.dumps(hourly_data), ex=3900)

            logger.info(f"==> Redis güncellendi: {CITY} saatlik verileri tazelendi.")
            logger.info("Sistem 1 saat beklemeye geçiyor...")

            time.sleep(3600)

        except requests.exceptions.RequestException as e:
            logger.error(f"Dış servis (API) hatası: {e}")
            time.sleep(60)
        except Exception as e:
            logger.error(f"Redis işlemi sırasında hata: {e}")
            time.sleep(60)


if __name__ == "__main__":
    get_hourly_weather()