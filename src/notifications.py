# src/notifications.py
import requests
import os

def send_telegram_message(message: str):
    """
    Sends a message to the Telegram chat configured in .env
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("[WARN] Telegram not configured. Message omitted.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML" # Allows using bold <b> etc
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[INFO] Telegram notification sent.")
        else:
            print(f"[ERROR] Failed to send to Telegram: {response.text}")
    except Exception as e:
        print(f"[ERROR] Error connecting to Telegram: {e}")