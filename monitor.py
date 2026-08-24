import os
import json
import re
import requests
from bs4 import BeautifulSoup

# Links for verification
URLS = [
    "https://trnita.scioskola.cz/aktuality",
    "https://stredni-brno.scioskola.cz/aktuality/",
    "https://www.gml.cz/kalendar"
]

# Telegram settings (taken from GitHub secrets)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def send_telegram(message):
    """Sends a notification message to the specified Telegram chat/channel."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram credentials are not configured in GitHub Secrets!")
        return
        
    # Clean the tokens to remove any accidental spaces
    token = str(TELEGRAM_TOKEN).strip()
    chat_id = str(TELEGRAM_CHAT_ID).strip()
    
    # Split the URL parts to bypass GitHub Actions automatic masking bugs
    base_url = "https://telegram.org"
    bot_prefix = "bot"
    endpoint = "/sendMessage"
    full_url = f"{base_url}{bot_prefix}{token}{endpoint}"
    
    payload = {
        "chat_id": chat_id, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    
    try:
        # Execute the HTTP POST request to Telegram API
        response = requests.post(full_url, json=payload, timeout=10)
        print(f"Telegram response status code: {response.status_code}")
        
        # If Telegram returns an explicit error code (e.g., 400 or 401)
        if response.status_code != 200:
            print(f"Telegram API Error Details: {response.text}")
            
    except Exception as e:
        print(f"Failed to communicate with Telegram API: {e}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        # CRITICAL DIAGNOSTIC LINE: Prints the exact reason why Telegram might block the message
        print(f"Telegram response: Status {response.status_code}, Text: {response.text}")
    except Exception as e:
        print(f"Failed to communicate with Telegram API: {e}")

def main():
    # history = load_history()
    history = []  # Temporarily ignore history database for debugging
    new_history = list(history)
    has_updates = False

    for url in URLS:
        try:
            print(f"Проверяем: {url}")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Ошибка доступа к {url}: статус {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Search for all titles and text blocks, where a phrase 
            # 'otevřených dveří' exists, including 'Den...', и 'Dny...'
            found_items = soup.find_all(text=re.compile(r"otevřených dveří", re.IGNORECASE))
            
            for item in found_items:
                clean_text = item.strip()
                # Ignore too short tech coincidences
                if len(clean_text) < 10:
                    continue
                
                # Create a unique key (link + text)
                unique_key = f"{url} | {clean_text}"
                
                if unique_key not in history:
                    print(f"Найдено новое событие: {clean_text}")
                    msg = f"🔔 *Найден День открытых дверей!*\n\n📝 {clean_text}\n\n🔗 [Перейти на сайт]({url})"
                    send_telegram(msg)
                    new_history.append(unique_key)
                    has_updates = True
                    
        except Exception as e:
            print(f"Error while processing {url}: {e}")

    if has_updates:
        save_history(new_history)
        print("History updated.")
    else:
        print("No new events found.")

if __name__ == "__main__":
    main()
