import time
import requests
import asyncio
from bs4 import BeautifulSoup
from telegram import Bot
from flask import Flask
from threading import Thread

# Веб-сервер для Render, чтобы он не ругался на порты
app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Твои данные
TELEGRAM_TOKEN = "8568164301:AAGxkVcBTfABQ30Ryo3h_Di_s1ni9IFGb4E"
CHAT_ID = "368594682"

# Ссылка на OLX (2 комнаты, цена до 3000, Бемово и Беляны)
OLX_SEARCH_URL = (
    "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/warszawa/"
    "?search%5Bfilter_float_price%3Ato%5D=3000"
    "&search%5Bfilter_enum_rooms%5D%5B0%5D=two"
    "&search%5Bdistrict_id%5D%5B0%5D=11"  # Bemowo
    "&search%5Bdistrict_id%5D%5B1%5D=9"   # Bielany
)

CHECK_INTERVAL = 900 

bot = Bot(token=TELEGRAM_TOKEN)
sent_ads = set()

async def send_start_message():
    await bot.send_message(chat_id=CHAT_ID, text="🚀 Бот запущен! Слежу за Бемово и Белянами.")

def check_olx():
    print("Проверяю новые квартиры...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(OLX_SEARCH_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        ad_cards = soup.select('div[data-cy="l-card"]')
        
        for card in ad_cards:
            link_elem = card.find('a', href=True)
            if not link_elem: continue
            
            href = link_elem.get('href')
            ad_link = href if href.startswith('http') else f"https://www.olx.pl{href}"
            ad_id = ad_link.split('-ID')[-1].split('.')[0]
            
            if ad_id not in sent_ads:
                sent_ads.add(ad_id)
                title_elem = card.select_one('h6')
                title = title_elem.text if title_elem else "Квартира 2 комнаты"
                price_elem = card.select_one('p[data-testid="ad-price"]')
                price = price_elem.text if price_elem else "Цена не указана"
                
                message = f"🔥 Новая квартира!\n\n📌 {title}\n💰 {price}\n\n🔗 {ad_link}"
                asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message))
                time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    # Запускаем веб-сервер в фоне для Render
    keep_alive()
    
    # Отправляем сообщение о запуске
    asyncio.run(send_start_message())
    
    # Основной цикл проверки квартир
    while True:
        check_olx()
        time.sleep(CHECK_INTERVAL)
