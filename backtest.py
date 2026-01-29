import pandas as pd
import yfinance as yf

# Configuration
WATCHLIST_FILE = 'watchlist.txt'
EMA_SHORT = 9
EMA_MEDIUM = 21
EMA_LONG = 55
INITIAL_CAPITAL = 10000

def load_watchlist():
    try:
        with open(WATCHLIST_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {WATCHLIST_FILE} not found.")
        return []

def calculate_emas(df):
    df['EMA_9'] = df['Close'].ewm(span=EMA_SHORT, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=EMA_MEDIUM, adjust=False).mean()
    df['EMA_55'] = df['Close'].ewm(span=EMA_LONG, adjust=False).mean()
    return df

def backtest_ticker(ticker):
    print(f"Backtesting {ticker}...")
    df = yf.download(ticker, period="2y", interval="1d", progress=False)
    if df.empty or len(df) < EMA_LONG:
        return []

    # Flatten MultiIndex columns if present (yfinance v0.2+)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = calculate_emas(df)
    
    trades = []
    position = None # None or dict with entry_price, entry_date

    # Iterate through rows
    # We need to look at 'yesterday' to decide for 'today' or just row by row
    # Vectorized would be faster but iteration is clearer for stateful logic
    
    for i in range(EMA_LONG, len(df)):
        date = df.index[i]
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        close = float(row['Close'])
        ema9 = float(row['EMA_9'])
        ema21 = float(row['EMA_21'])
        ema55 = float(row['EMA_55'])
        
        prev_ema9 = float(prev_row['EMA_9'])
        prev_ema21 = float(prev_row['EMA_21'])

        # Logic matches strategy.py
        # Entry
        is_ascending = (ema9 > ema21) and (ema21 > ema55)
        price_above_all = (close > ema9) and (close > ema21) and (close > ema55)
        entry_signal = is_ascending and price_above_all
        
        # Exit
        price_below_21 = close < ema21
        cross_below = (prev_ema9 >= prev_ema21) and (ema9 < ema21)
        exit_signal = price_below_21 or cross_below

        if position is None:
            if entry_signal:
                position = {
                    "ticker": ticker,
                    "entry_date": date,
                    "entry_price": close
                }
        else:
            if exit_signal:
                position["exit_date"] = date
                position["exit_price"] = close
                position["pct_change"] = (close - position["entry_price"]) / position["entry_price"]
                trades.append(position)
                position = None
                
    return trades

def main():
    tickers = load_watchlist()
    all_trades = []
    
    for ticker in tickers:
        try:
            trades = backtest_ticker(ticker)
            all_trades.extend(trades)
        except Exception as e:
            print(f"Error backtesting {ticker}: {e}")

    if not all_trades:
        print("No trades found in backtest period.")
        return

    # Analyze results
    results = pd.DataFrame(all_trades)
    print("\n--- Backtest Results ---")
    print(f"Total Trades: {len(results)}")
    
    wins = results[results['pct_change'] > 0]
    losses = results[results['pct_change'] <= 0]
    
    win_rate = len(wins) / len(results) * 100
    avg_gain = wins['pct_change'].mean() * 100 if not wins.empty else 0
    avg_loss = losses['pct_change'].mean() * 100 if not losses.empty else 0
    
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Avg Gain: {avg_gain:.2f}%")
    print(f"Avg Loss: {avg_loss:.2f}%")
    
    results['cumulative'] = (1 + results['pct_change']).cumprod()
    print(f"Total Return: {(results['cumulative'].iloc[-1] - 1) * 100:.2f}%" if not results.empty else "Total Return: 0%")

if __name__ == "__main__":
    main()
