import os
import json
import re
import requests
from bs4 import BeautifulSoup

# Target URLs for web monitoring
URLS = [
    "https://trnita.scioskola.cz/aktuality",
    "https://stredni-brno.scioskola.cz/aktuality/",
    "https://www.gml.cz/kalendar"
]

# Fetch Telegram credentials from GitHub repository secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
HISTORY_FILE = "history.json"

def load_history():
    """Loads previously found events from the local JSON file to prevent duplicates."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    """Saves updated event keys back to the history JSON file."""
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
    
    # Split the request address parameters into parts to prevent GitHub masking bugs
    api_domain = "api.telegram.org"
    request_link = f"https://{api_domain}/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    
    try:
        # Execute the HTTP POST request to Telegram API using the new variable name
        response = requests.post(request_link, json=payload, timeout=10)
        print(f"Telegram response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Telegram API Error Details: {response.text}")
            
    except Exception as e:
        print(f"Failed to communicate with Telegram API: {e}")

def main():
    # Force empty history database loop to trigger diagnostic resend
    history = []  
    new_history = list(load_history())
    has_updates = False

    for url in URLS:
        try:
            print(f"Scanning URL: {url}")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Access error for {url}: Status code {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Replaced 'text=' with 'string=' to eliminate the DeprecationWarning completely
            found_items = soup.find_all(string=re.compile(r"otevřených dveří", re.IGNORECASE))
            
            for item in found_items:
                clean_text = item.strip()
                if len(clean_text) < 10:
                    continue
                
                unique_key = f"{url} | {clean_text}"
                
                # Check against the actual original records
                if unique_key not in new_history:
                    print(f"New event discovered: {clean_text}")
                    msg = f"🔔 *Найден День открытых дверей!*\n\n📝 {clean_text}\n\n🔗 [Перейти на сайт]({url})"
                    send_telegram(msg)
                    new_history.append(unique_key)
                    has_updates = True
                    
        except Exception as e:
            print(f"Error while parsing {url}: {e}")

    if has_updates:
        save_history(new_history)
        print("History database updated successfully.")
    else:
        print("No new events matched the filtering criteria.")

if __name__ == "__main__":
    main()
