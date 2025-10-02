# 🟡 Binance Futures Trading Bot (CLI)

A modular Command-Line Interface (CLI) Binance Futures Trading Bot built using the official [Binance Python SDK](https://github.com/binance/binance-connector-python).  
It supports multiple futures order types, account operations, and structured logging—all designed for **educational and testnet usage**.

---

## 📌 Features

- ✅ Interactive CLI Menu
- ✅ Core & Advanced Order Types:
  - `MARKET` – Immediate execution at market price
  - `LIMIT` – Execute at a specific price
  - `STOP_LIMIT` – Conditional trigger with limit execution
  - `OCO` – One-Cancels-the-Other (Stop-Limit + Take-Profit)
  - `TWAP` – Time-Weighted Average Price (sliced execution)
- 💰 Account management:
  - Check account balance
  - View open orders
  - View trade history
  - Cancel active orders
- 🔐 Secure credential handling via `.env`
- 🪵 Structured rotating logs for debugging

---

## 📂 Project Structure
```
trading_bot/
├── src/
│   ├── advanced/
│   │   ├── oco.py                    # One-Cancels-Other order implementation
│   │   ├── stop_limit.py             # Stop-limit order implementation
│   │   └── twap.py                   # Time-Weighted Average Price implementation
│   ├── bot.py                        # Main bot logic
│   ├── config.py                     # Configuration and API key management
│   ├── limit_orders.py               # Limit order implementations
│   ├── logger.py                     # Logging configuration
│   ├── market_orders.py              # Market order implementations
│   └── trading_interface.py          # CLI menu and user interaction
├── .env                             # Environment variables (API keys)
├── .env.example                     # Sample environment configuration
├── .gitignore                       # Git ignore rules
├── bot.log                          # Application log file
├── README.md                        # Project documentation
├── report.pdf                       # Project report/documentation
└── requirements.txt                 # Python dependencies
```
---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/AdityaPatadiya/aditya-binance-bot.git
cd aditya-binance-bot
```

### 2️⃣ Set up a virtual environment
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Configure your Binance Testnet API credentials
`cp .env.example .env`
```
API_KEY=your_testnet_api_key
API_SECRET=your_testnet_secret
```
Get your API keys from the [Binance Futures Testnet](https://testnet.binancefuture.com/en/futures/BTCUSDT).

---
## Usage
Launch the trading bot:
`python src/trading_interface.py`

You'll see:
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
## Order Types Explained
- `Market Order`
Execute immediately at current market price.

- `Limit Order`
Place an order to buy/sell at a specific price or better.

- `Stop-Limit Order`
A stop price triggers the placement of a limit order. Useful for managing risk.

- `OCO (One Cancels Other)`
Two orders are placed simultaneously: one take-profit, one stop-loss. When one is triggered, the other is canceled.

- `TWAP (Time-Weighted Average Price)`
Breaks a large order into smaller slices and executes them over time to reduce market impact.


## Logging
All activities are logged with timestamps and severity levels.
Logs are stored in the `bot.log` directory with a rotating file handler.

---
> [!WARNING]
> This bot is intended for educational and testnet use only. It is not suitable for live trading without extensive testing and risk management. Use at your own risk.
