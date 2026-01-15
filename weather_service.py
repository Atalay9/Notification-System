import os
import requests
import logging
import redis
import json

# Logger kullanımı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Key doğrudan yazılmıyor, Environment Variables'dan geliyor
API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL", "http://api.weatherapi.com/v1/current.json")
CITY = "Adana"

# 3. Redis Bağlantısı
# Docker için host olarak 'redis_db' ismini kullanıyoruz
REDIS_HOST = os.getenv("REDIS_HOST", "redis_db")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def get_weather():
    if not API_KEY:
        logger.error("API_KEY bulunamadı!")
        return

    # URL artık 'hardcoded' değil
    params = {
        "key": API_KEY,
        "q": CITY,
        "aqi": "no",
        "lang": "tr"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Veriyi publish ediyoruz
        r.publish('weather_updates', json.dumps(data))

        # Print yerine Logger kullanıldı.
        logger.info(f"{CITY} verisi 'weather_updates' kanalına publish edildi.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Hava durumu çekilirken bir hata oluştu: {e}")


if __name__ == "__main__":
    get_weather()