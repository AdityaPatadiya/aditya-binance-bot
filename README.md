# 🟡 Binance Futures Trading Bot (CLI)

A Command-Line Interface (CLI) based Binance Futures Trading Bot built using the official [Binance Python SDK](https://github.com/binance/binance-connector-python). This bot supports placing various types of futures orders, account balance checks, order cancellations, and more.

---

## 📌 Features

- ✅ Interactive CLI Menu
- 📈 Place orders:
  - MARKET
  - LIMIT
  - STOP_LIMIT
  - OCO (One Cancels Other)
  - TWAP (Time-Weighted Average Price)
- 🧾 View trade history and open orders
- 💰 Check account balance
- 🗑 Cancel open orders
- 🔐 Secure API key handling with `.env`
- 🧠 TWAP slicing logic with interval-based execution
- 📋 Structured logging using Python's `logging` module

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/binance-futures-bot.git
cd binance-futures-bot
```

### 2️⃣ Setup a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure API keys

Create a `.env` file in the project root with the following content:

```
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret
```

Use the Binance **Futures Testnet** to avoid risking real funds:
- Testnet signup: https://testnet.binancefuture.com

---

## 🧪 Usage

Start the bot using:

```bash
python main.py
```

Follow the on-screen prompts:

```
┌────────────────────────────────────────────┐
│        BINANCE FUTURES TRADING BOT         │
├────────────────────────────────────────────┤
│ 1. Place New Order                         │
│ 2. Check Account Balance                   │
│ 3. View Open Orders                        │
│ 4. View Trade History                      │
│ 5. Cancel Order                            │
│ 6. Exit                                    │
└────────────────────────────────────────────┘
```

---

## 🛠 Project Structure

```
├── main.py               # CLI interface
├── tradingbot.py         # Core trading logic
├── order_types.py        # Encapsulated order functions
├── config.py             # Loads credentials from .env
├── logger.py             # Logging configuration
├── requirements.txt      # Python dependencies
└── .env.example          # Sample environment config
```

---

## 📄 Example `.env.example`

```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

---

## 🪵 Logging

All actions and errors are logged in `logs` using a rotating log system. Log entries include timestamps, levels, and detailed messages to aid debugging.

---

## ⚠️ Disclaimer

This bot is intended for **educational** and **testnet** use only. It is **not suitable for live trading** without extensive testing and risk management. Use at your own risk.
