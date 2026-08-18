import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

TELEGRAM_TOKEN = "8568164301:AAGxkVcBTfABQ30Ryo3h_Di_s1ni9IFGb4E"
CHAT_ID = "368594682"

OLX_SEARCH_URL = (
    "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/warszawa/"
    "?search%5Bfilter_float_price%3Ato%5D=3000"
    "&search%5Bfilter_enum_rooms%5D%5B0%5D=two"
    "&search%5Bdistrict_id%5D%5B0%5D=11"
    "&search%5Bdistrict_id%5D%5B1%5D=9"
)

CHECK_INTERVAL = 900 
bot = Bot(token=TELEGRAM_TOKEN)
sent_ads = set()

def check_olx():
    print("Проверяю новые квартиры...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(OLX_SEARCH_URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for card in soup.select('div[data-cy="l-card"]'):
            link_elem = card.find('a', href=True)
            if not link_elem: continue
            href = link_elem.get('href')
            ad_link = href if href.startswith('http') else f"https://www.olx.pl{href}"
            ad_id = ad_link.split('-ID')[-1].split('.')[0]
            if ad_id not in sent_ads:
                sent_ads.add(ad_id)
                title = card.select_one('h6').text if card.select_one('h6') else "Квартира"
                price = card.select_one('p[data-testid="ad-price"]').text if card.select_one('p[data-testid="ad-price"]') else ""
                bot.send_message(chat_id=CHAT_ID, text=f"🔥 Новая квартира!\n\n📌 {title}\n💰 {price}\n\n🔗 {ad_link}")
                time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    bot.send_message(chat_id=CHAT_ID, text="🚀 Бот запущен! Слежу за Бемово и Белянами.")
    while True:
        check_olx()
        time.sleep(CHECK_INTERVAL)
