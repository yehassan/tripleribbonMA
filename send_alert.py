import requests
import os
import sys

def send_telegram_message(message):
    """
    Sends a message to the configured Telegram chat.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram alert sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram alert: {e}")
        return False

if __name__ == "__main__":
    # Test execution
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
        send_telegram_message(msg)
    else:
        print("Usage: python send_alert.py 'Message to send'")
