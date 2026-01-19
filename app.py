import os
import redis
import json
import logging
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flasgger import Swagger

# .env yapılandırması
load_dotenv()

# 2. Logger yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
swagger = Swagger(app)

# Redis bağlantı bilgileri
REDIS_HOST = os.getenv("REDIS_HOST", "redis_db")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Redis bağlantısının kurulumu
cache = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)

@app.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    """
        Hava Durumu Verisini Getir
        ---
        parameters:
          - name: city
            in: path
            type: string
            required: true
            description: Hava durumu sorgulanacak şehir adı (örn. adana)
        responses:
          200:
            description: Şehir verisi başarıyla getirildi
          404:
            description: Şehir verisi Redis'te bulunamadı
        """
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

@app.route('/threshold', methods=['POST'])
def set_threshold():
    """
        Sıcaklık Eşik Değeri Belirle
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
              id: Threshold
              required:
                - value
              properties:
                value:
                  type: number
                  description: Alarm verilmesini istediğiniz sıcaklık derecesi
        responses:
          200:
            description: Eşik değeri başarıyla güncellendi
          400:
            description: Hatalı JSON formatı
        """
    try:
        # Kullanıcıdan veriyi alıyoruz
        data = request.get_json()

        if not data or 'value' not in data:
            return jsonify({"status": "error", "message": "Lütfen 'value' içeren bir JSON gönderin."}), 400

        threshold_value = data['value']

        # Verinin sayı olduğundan emin oluyoruz
        if not isinstance(threshold_value, (int, float)):
            return jsonify({"status": "error", "message": "Değer bir sayı olmalıdır."}), 400

        # Redis'e kaydediyoruz
        cache.set("weather_threshold", threshold_value)

        logger.info(f"Yeni threshold değeri ayarlandı: {threshold_value}")
        return jsonify({
            "status": "success",
            "message": f"Threshold {threshold_value} olarak güncellendi."
        }), 200
    except Exception as e:
        logger.error(f"Threshold kaydedilirken hata: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    logger.info("API Sunucusu başlatılıyor... http://127.0.0.1:5000/weather/adana")
    app.run(debug=True, host='0.0.0.0', port=5000)