# Triple MA Ribbon Swing Trading Scanner

Automated swing trading scanner based on the Triple Moving Average Ribbon strategy (9/21/55 EMA). Runs daily via GitHub Actions and sends alerts to Telegram.

## Strategy Logic

**Trend Following Strategy:**
*   **Indicators:** 9 EMA, 21 EMA, 55 EMA.
*   **Entry Signal:**
    *   Ribbon is ascending (9 > 21 > 55).
    *   Price closes above all three EMAs.
    *   Alert is sent only on the first occurrence (Entry).
*   **Exit Signal:**
    *   Price closes below the 21 EMA.
    *   OR 9 EMA crosses below 21 EMA.
    *   Alert is sent only if previously in a trade.

## Setup Instructions

### 1. Fork & Clone
Fork this repository to your GitHub account and clone it locally.

### 2. Configure Telegram Bot
1.  Open Telegram and search for `@BotFather`.
2.  Send `/newbot` to create a new bot.
3.  Copy the **API Token** provided.
4.  Start a chat with your new bot (or add it to a group).
5.  Get your **Chat ID** (forward a message to `@userinfobot` or use `getUpdates` API).

### 3. GitHub Secrets
Go to your repository **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.
Add the following secrets:
*   `TELEGRAM_BOT_TOKEN`: Your bot token.
*   `TELEGRAM_CHAT_ID`: Your chat ID.

### 4. Watchlist
Edit `watchlist.txt` to add tickers you want to monitor.
Format (one ticker per line):
```text
AAPL
MSFT
...
```

## Usage

### Automatic Scanning
The scanner runs automatically at **4:30 PM EST** on weekdays (Monday-Friday) via GitHub Actions.

### Manual Run (Local)
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set environment variables (optional, for alerts):
    ```bash
    export TELEGRAM_BOT_TOKEN="your_token"
    export TELEGRAM_CHAT_ID="your_chat_id"
    ```
3.  Run the scanner:
    ```bash
    python strategy.py
    ```

### Backtesting
Run the backtest script to see historical performance on your watchlist:
```bash
python backtest.py
```

## State Persistence
The system tracks active signals in `signals_state.json`. This file is automatically committed back to the repository by the GitHub Action to prevent duplicate alerts.

## Troubleshooting
*   **yfinance Errors:** Occasional API failures may occur. The script logs these to the GitHub Action output. Check the "Run Strategy Scanner" step logs.
*   **No Alerts:** Ensure your watchlist is populated and the market data is up to date. If no new signals match the strict criteria, no message is sent.
*   **Timezones:** The cron schedule is set for 21:30 UTC. Adjust `.github/workflows/scanner.yml` if you need a different time.

## Disclaimer
This software is for educational purposes only. Do not trade based solely on these alerts. Use your own risk management.
