import os
import requests
import logging

# Logger kullanımı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Key doğrudan yazılmıyor, Environment Variables'dan geliyor
API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL", "http://api.weatherapi.com/v1/current.json")
CITY = "Adana"


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
        temp = data['current']['temp_c']
        condition = data['current']['condition']['text']

        # Print yerine Logger kullanıldı.
        logger.info(f"{CITY} hava durumu: {temp}°C, Gökyüzü: {condition}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Hava durumu çekilirken bir hata oluştu: {e}")


if __name__ == "__main__":
    get_weather()