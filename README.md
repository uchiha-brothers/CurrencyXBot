
````markdown
# 🤖 CurrencyXBot – Telegram Currency Converter Bot

CurrencyXBot is a Python-powered Telegram bot that allows users to:
- 🌍 Convert between over 150 international currencies
- 💹 Check real-time exchange rates
- 📜 List all supported currencies

This project integrates:
- **Telegram Bot API** for communication
- **ExchangeRate-API** for currency conversion

---

## 🚀 Features

- `/start`: Begin interaction with the bot
- `/help`: Instructions and usage guide
- `/convert 100 USD to GHS`: Convert amount from one currency to another
- `/showrate USD to GHS`: Get current exchange rate between currencies
- `/currencysupported`: List all supported currencies

---

## 🛠 Requirements

- Python 3.7+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Free API key from [https://www.exchangerate-api.com](https://www.exchangerate-api.com)

---

## 🔧 Setup

### 📁 1. Clone this Repository

```bash
git clone https://github.com/ManaenB/CurrencyXBot.git
cd CurrencyXBot
````

### 📦 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

### 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### ⚙️ 4. Create `config.json`

```json
{
  "TELEGRAM_BOT_TOKEN": "your-telegram-bot-token",
  "EXCHANGE_RATE_API_KEY": "your-exchange-rate-api-key"
}
```

### ▶️ 5. Run the Bot

```bash
python currency_x_bot.py
```

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🤝 Acknowledgments

* Telegram Bot API Docs: [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)
* ExchangeRate-API: [https://www.exchangerate-api.com](https://www.exchangerate-api.com)

---

## ✨ Created by

**Manaen** – self-Proclaimed back street Python & C# programmer exploring APIs, bots, and backend systems.

