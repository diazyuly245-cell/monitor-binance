import requests
import time
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
INTERVALO_MINUTOS = int(os.environ.get("INTERVALO_MINUTOS", "5"))

def get_p2p_price(fiat):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    body = {
        "asset": "USDT",
        "fiat": fiat,
        "merchantCheck": False,
        "page": 1,
        "payTypes": [],
        "publisherType": None,
        "rows": 10,
        "tradeType": "SELL"
    }
    response = requests.post(url, json=body, headers=headers)
    data = response.json()
    precios = [float(d["adv"]["price"]) for d in data["data"]]
    return precios[4]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def calcular_y_enviar():
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Consultando Binance P2P...")
        cop = get_p2p_price("COP")
        ves = get_p2p_price("VES")
        tasa = cop / ves

        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        mensaje = (
            f"📊 *Tasa COP/BS - Master Exchange*\n\n"
            f"🕐 {now}\n\n"
            f"🇺🇸 USDT/COP (5to): {cop:,.2f}\n"
            f"🇻🇪 USDT/VES (5to): {ves:,.2f}\n\n"
            f"💱 *Tasa: {tasa:.4f} COP x BS*\n\n"
            f"_Ejemplo: 100.000 COP = {100000/tasa:,.0f} BS_"
        )

        result = send_telegram(mensaje)
        if result.get("ok"):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Mensaje enviado. Tasa: {tasa:.4f}")
        else:
            print(f"Error Telegram: {result}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Monitor iniciado — enviando cada {INTERVALO_MINUTOS} minuto(s)")
    while True:
        calcular_y_enviar()
        time.sleep(INTERVALO_MINUTOS * 60)
