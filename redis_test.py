import redis
import time

# 1. Redis bağlantısı
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

print("--- Key-Value ve Expire İşlemi ---")
# 2. Key-Value Oluşturma ve 5 Saniye Expire (Süre) Verme
r.set('staj_anahtar', 'Bu mesaj 5 saniye sonra yok olacak', ex=5)
print(f"İlk okuma: {r.get('staj_anahtar')}")

# 3. Bekleyip Tekrar Erişmeye Çalış
print("5 saniye bekleniyor...")
time.sleep(6)
print(f"Süre dolduktan sonra okuma: {r.get('staj_anahtar')} (None dönmeli)")

print("\n--- Pub/Sub (Channel) İşlemi ---")
# 4. Kanala Mesaj Gönder (Publish)
r.publish('staj_kanali', 'Selam, bu bir canlı yayın mesajıdır!')
print("Mesaj 'staj_kanali' isimli kanala gönderildi.")