import os
import requests
import logging
import redis  # Yeni ekledik
import json   # Veriyi metin olarak saklamak için

# Logger kullanımı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Key Environment Variables'dan geliyor
API_KEY = os.getenv("WEATHER_API_KEY")
# current.json yerine forecast.json tercih edildi.
BASE_URL = os.getenv("WEATHER_API_URL", "http://api.weatherapi.com/v1/forecast.json")
CITY = "Adana"

# Redis bağlantı bilgileri env'den geliyor
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Redis bağlantısının kurulumu
try:
    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    logger.info("Redis bağlantısı başarılı.")
except Exception as e:
    logger.error(f"Redis'e bağlanılamadı: {e}")

def get_hourly_weather():
    if not API_KEY:
        logger.error("API_KEY bulunamadı!")
        return

    params = {
        "key": API_KEY,
        "q": CITY,
        "days" : 1,
        "aqi": "no",
        "lang": "tr"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        hourly_data = data['forecast']['forecastday'][0]['hour']
        current_temp = data['current']['temp_c']
        logger.info(f"{CITY} anlık sıcaklık: {current_temp}°C. 24 saatlik veri işleniyor...")

        cache_key = f"weather:{CITY.lower()}"

        cache.set(cache_key, json.dumps(hourly_data), ex=3600)
        logger.info(f"==> Veri Redis'e '{cache_key}' anahtarıyla basıldı.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Dış servis (API) hatası: {e}")
    except Exception as e:
        logger.error(f"Redis işlemi sırasında hata: {e}")


if __name__ == "__main__":
    get_hourly_weather()