# Trading Bot - Binance Futures Testnet

Python CLI bot for placing Binance USDT-M Futures Testnet orders.

## Features

- Place `MARKET` and `LIMIT` orders
- Support `BUY` and `SELL`
- Validate symbol, side, order type, quantity, and price
- Log API requests, responses, and errors
- Use `.env` configuration for credentials

## Project Structure

```text
trading_bot/
|-- bot/
|   |-- client.py
|   |-- orders.py
|   |-- validators.py
|   |-- logging_config.py
|   `-- cli.py
|-- .env.example
|-- requirements.txt
|-- README.md
`-- logs/
```

## How To Setup

1. Clone the repository and open the project folder.
2. Create a virtual environment.
3. Install dependencies.
4. Copy `.env.example` to `.env`.
5. Add your Binance Futures Testnet API credentials.

### Windows PowerShell

```powershell
cd trading_bot
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### `.env` file

```env
API_KEY=your_testnet_api_key_here
API_SECRET=your_testnet_api_secret_here
BASE_URL=https://testnet.binancefuture.com
```

Create your testnet API keys here:
[https://testnet.binancefuture.com](https://testnet.binancefuture.com)

## How To Run

From the `trading_bot` folder:

```powershell
.\venv\Scripts\python.exe -m bot.cli --help
```

## Example Commands For GitHub

### Test connection

```powershell
.\venv\Scripts\python.exe -m bot.cli test
```

### Place a MARKET order

```powershell
.\venv\Scripts\python.exe -m bot.cli place BTCUSDT BUY MARKET 0.001
```

### Place a LIMIT order

```powershell
.\venv\Scripts\python.exe -m bot.cli place BTCUSDT SELL LIMIT 0.001 --price 35000 --tif GTC
```

### Check order status

```powershell
.\venv\Scripts\python.exe -m bot.cli status BTCUSDT 123456789
```

### Cancel an order

```powershell
.\venv\Scripts\python.exe -m bot.cli cancel BTCUSDT 123456789
```

## Logging

Logs are saved to `logs/trading.log`.

## Notes

- This project uses Binance Futures Testnet only.
- `LIMIT` orders require `--price`.
- Do not commit your real `.env` file to GitHub.
