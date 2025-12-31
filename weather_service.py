import requests

#API key tanımlandı.
API_KEY = "dabee3e33c774bc0b4391205252412"
CITY = "Adana"


def get_weather():
    # WeatherAPI'nin istek adresi oluşturuldu ve Türkçeleştirildi.
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}&aqi=no&lang=tr"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temp = data['current']['temp_c']
        condition = data['current']['condition']['text']
        print(f"{CITY} için hava durumu: {temp}°C, Gökyüzü: {condition}")
    else:
        print("Hata: Veri çekilemedi", response.status_code)


if __name__ == "__main__":
    get_weather()