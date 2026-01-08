import os
import redis
import json
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

# .env yapılandırması
load_dotenv()

# 2. Logger yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Redis bağlantı bilgileri
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Redis bağlantısının kurulumu
cache = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)


@app.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    # Redis anahtarının oluşturulması
    cache_key = f"weather:hourly:{city.lower()}"

    # Redis'ten veriyi çek
    data = cache.get(cache_key)

    if data:
        logger.info(f"Cache HIT: {city} verisi Redis'ten getirildi.")  # Bilgilendirme logu
        return jsonify({"status": "success", "city": city, "data": json.loads(data)})
    else:
        logger.warning(f"Cache MISS: {city} verisi Redis'te bulunamadı.")  # Uyarı logu
        return jsonify({"status": "error", "message": "Veri bulunamadı."}), 404


if __name__ == '__main__':
    logger.info("API Sunucusu başlatılıyor... http://127.0.0.1:5000/weather/adana")
    app.run(debug=True, host='0.0.0.0', port=5000)