# 🔔 Automated Web Page Monitor for Open House Events (DOD)

A lightweight, 100% free, and autonomous Python script powered by **GitHub Actions** that monitors specific school web pages for changes. It scans content for Czech keywords like *"otevřených dveří"* (Open House) and instantly sends notifications via a **Telegram Bot** whenever a new event is announced.

This project completely replaces paid SaaS monitoring alternatives (such as Feedly Web Feeds) by combining web scraping logic with automated cloud triggers.

---

## 🛠️ How It Works

[GitHub Actions Timer] ──► Triggers once every 24 hours│▼[Python Script (monitor.py)] ──► Downloads target URLs using BeautifulSoup│▼[Keyword Analysis] ──► Searches for "otevřených dveří" (case-insensitive)│├──► Matches found? Check local database (history.json)│         ││         ├──► YES (New text): Sends Telegram push notification & saves to history│         └──► NO (Duplicate): Quietly terminates to prevent spam

---

## 📂 Repository Structure

* `monitor.py` — The core Python script responsible for fetching web data, parsing strings, tracking event history, and triggering the Telegram API.
* `history.json` — A local database automatically managed by the script to store previously discovered events and prevent duplicate notifications.
* `.github/workflows/check.yml` — A GitHub Actions configuration file that acts as a cron-timer to run the monitor automatically every day.

---

## 🌐 Monitored Websites

The monitor currently tracks the following endpoints:
1. `https://scioskola.cz` (ScioŠkola Trnitá)
2. `https://scioskola.cz` (Střední ScioŠkola Brno)
3. `https://gml.cz` (Gymnázium Matyáše Lercha)

---

## 🔒 Required GitHub Secrets

To make the Telegram integration work securely without exposing sensitive credentials in the codebase, the following **Repository Secrets** must be configured under `Settings -> Secrets and variables -> Actions`:

* `TELEGRAM_TOKEN` — The HTTP API token obtained from official `@BotFather` upon bot creation.
* `TELEGRAM_CHAT_ID` — Your unique personal Telegram user ID (can be fetched using `@userinfobot`). Do not use the chat ID of the bot itself.

---

## ⚙️ Workflow Permissions

For the script to autonomously save its progress and prevent duplicate alerts, GitHub Actions requires write permissions to update `history.json`.
1. Go to your repository **Settings** -> **Actions** -> **General**.
2. Scroll to the bottom section: **Workflow permissions**.
3. Toggle the option to **Read and write permissions**.
4. Click **Save**.

---

## 💬 Notification Format Example

When a new announcement is discovered on the web pages, you will receive an instant push notification formatted in markdown layout:

> 🔔 **Найден День открытых дверей!**
> 
> 📝 Den otevřených dveří 21.1.
> 
> 🔗 [Перейти на сайт](https://scioskola.cz)

---

## 🔄 Future Customizations

### Adding New Websites
To monitor more schools, edit `monitor.py` and append new target URLs inside the `URLS` list block at the top of the file:
```python
URLS = [
    "https://scioskola.cz",
    "https://scioskola.cz",
    "https://gml.cz",
    "https://example-new-school.cz"  # Add like this
]
```

### Resetting Monitor Memory
If you ever want the bot to completely re-scan the websites and force-resend current event notifications, simply edit or clear the content inside `history.json` back to empty brackets `[]`, or delete the `history.json` file entirely from the GitHub interface.
