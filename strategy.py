import pandas as pd
import yfinance as yf
import json
import os
import datetime
from send_alert import send_telegram_message

# Configuration
WATCHLIST_FILE = 'watchlist.txt'
STATE_FILE = 'signals_state.json'
EMA_SHORT = 9
EMA_MEDIUM = 21
EMA_LONG = 55

def load_watchlist():
    try:
        with open(WATCHLIST_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {WATCHLIST_FILE} not found.")
        return []

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error decoding state file. Starting fresh.")
            return {}
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def fetch_data(ticker):
    try:
        # Fetch enough history for 55 EMA calculation
        # 55 EMA requires at least 55 periods, preferably more for stabilization
        # 6 months is plenty for daily data
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if data.empty:
            return None
        
        # Flatten MultiIndex columns if present (yfinance v0.2+)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def calculate_emas(df):
    try:
        # Check if we have enough data
        if len(df) < EMA_LONG:
            return df
        
        # Calculate EMAs
        # adjust=False is standard for technical analysis EMAs
        df['EMA_9'] = df['Close'].ewm(span=EMA_SHORT, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=EMA_MEDIUM, adjust=False).mean()
        df['EMA_55'] = df['Close'].ewm(span=EMA_LONG, adjust=False).mean()
        return df
    except Exception as e:
        print(f"Error calculating EMAs: {e}")
        return df

def analyze_ticker(ticker, current_state):
    df = fetch_data(ticker)
    if df is None or len(df) < EMA_LONG:
        print(f"Insufficient data for {ticker}")
        return None, current_state

    df = calculate_emas(df)
    
    # Get the latest row (today/yesterday depending on run time)
    # and the previous row for crossover checks if needed
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # Current values
    close = float(latest['Close'])
    ema9 = float(latest['EMA_9'])
    ema21 = float(latest['EMA_21'])
    ema55 = float(latest['EMA_55'])

    prev_ema9 = float(prev['EMA_9'])
    prev_ema21 = float(prev['EMA_21'])

    # Determine Signal Status
    # Entry Logic: 9 > 21 > 55 AND Price > All 3
    is_ascending = (ema9 > ema21) and (ema21 > ema55)
    price_above_all = (close > ema9) and (close > ema21) and (close > ema55)
    
    entry_signal = is_ascending and price_above_all

    # Exit Logic: Price < 21 EMA OR 9 crosses below 21
    price_below_21 = close < ema21
    cross_below = (prev_ema9 >= prev_ema21) and (ema9 < ema21)
    
    exit_signal = price_below_21 or cross_below

    # State Management
    ticker_state = current_state.get(ticker, {"status": "FLAT"})
    status = ticker_state.get("status", "FLAT")
    
    signal_type = None
    
    if status == "FLAT":
        if entry_signal:
            signal_type = "ENTRY"
            ticker_state["status"] = "LONG"
            ticker_state["entry_date"] = str(datetime.date.today())
            ticker_state["entry_price"] = close
    elif status == "LONG":
        if exit_signal:
            signal_type = "EXIT"
            ticker_state["status"] = "FLAT"
            ticker_state["exit_date"] = str(datetime.date.today())
            ticker_state["exit_price"] = close

    current_state[ticker] = ticker_state
    
    if signal_type:
        return {
            "ticker": ticker,
            "type": signal_type,
            "price": close,
            "ema9": ema9,
            "ema21": ema21,
            "ema55": ema55
        }, current_state
    
    return None, current_state

def main():
    print("Starting Triple MA Ribbon Scan...")
    tickers = load_watchlist()
    state = load_state()
    
    signals = []
    
    for ticker in tickers:
        try:
            signal, state = analyze_ticker(ticker, state)
            if signal:
                signals.append(signal)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    save_state(state)
    print("Scan complete. State updated.")

    if signals:
        print(f"Found {len(signals)} new signals.")
        message_lines = ["🚀 *Triple MA Ribbon Alerts* 🚀\n"]
        for s in signals:
            icon = "🟢" if s['type'] == "ENTRY" else "🔴"
            line = f"{icon} *{s['type']}* - *{s['ticker']}* @ ${s['price']:.2f}\n" \
                   f"   (9EMA: {s['ema9']:.2f} | 21EMA: {s['ema21']:.2f} | 55EMA: {s['ema55']:.2f})"
            message_lines.append(line)
        
        full_message = "\n".join(message_lines)
        print(full_message)
        send_telegram_message(full_message)
    else:
        print("No new signals found.")

if __name__ == "__main__":
    main()
