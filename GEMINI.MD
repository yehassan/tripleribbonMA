You are building an automated Triple MA Ribbon swing trading scanner that runs on GitHub Actions and delivers Telegram alerts.
System purpose:
Monitor a user-defined watchlist for Triple MA Ribbon (9/21/55 EMA) entry and exit signals. Alert user via Telegram when new signals emerge. User executes trades manually.
Core strategy logic:

Entry signal: All three EMAs ascending (9>21>55 when looking back 1-2 periods) AND price closes above all three EMAs
Exit signal: Price closes below 21 EMA OR 9 EMA crosses below 21 EMA
Data source: yfinance daily EOD data
Execution: Scan runs automatically after market close on weekdays

Technical architecture:

Python scripts for data fetch, calculation, alert delivery
GitHub Actions workflow scheduled at 4:30 PM EST weekdays
Telegram Bot API for push notifications
State persistence via JSON file in repo to track active signals and prevent duplicate alerts
Watchlist managed via CSV file in repository

Critical requirements:

Data validation: Handle yfinance NaN values, missing data, API failures gracefully
No duplicate alerts: Track which signals already sent, only notify on NEW entries/exits
Consolidated messaging: Single Telegram message listing all signals, not one per ticker
Timezone handling: Convert UTC cron to EST, account for market holidays via data availability check
Error transparency: Log failures to GitHub Actions output for debugging

Output structure:
/
├── .github/workflows/scanner.yml
├── strategy.py
├── send_alert.py
├── requirements.txt
├── watchlist.csv
├── signals_state.json (created on first run)
├── backtest.py
├── .gitignore
└── README.md
Non-requirements:

No trade execution automation
No broker API integration
No intraday data or real-time monitoring
No position sizing or risk management logic
No database—state stored in flat JSON file

Build for reliability over complexity. Prioritize clear error messages and operational transparency.