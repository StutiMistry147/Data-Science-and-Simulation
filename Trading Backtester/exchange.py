import pandas as pd
import sqlite3
import time
import os

DB_NAME = 'hft_results.db'
conn = sqlite3.connect(DB_NAME)
conn.execute("DROP TABLE IF EXISTS portfolio")
conn.execute("CREATE TABLE portfolio (trade_id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, action TEXT, price REAL)")
conn.commit()

def run_backtest():
    print("Backtester Engine Started... Monitoring market_data.csv")
    while True:
        try:
            if not os.path.exists('market_data.csv'):
                continue
              
            df = pd.read_csv('market_data.csv').tail(10)
            if len(df) < 10: continue

            current_price = df['price'].iloc[-1]
            avg_price = df['price'].mean()

            buy_signal = avg_price * 0.9995
            sell_signal = avg_price * 1.0005

            ts = time.strftime('%H:%M:%S')

            if current_price < buy_signal:
                conn.execute("INSERT INTO portfolio (ts, action, price) VALUES (?, 'BUY', ?)", (ts, current_price))
                conn.commit()
                print(f"[{ts}] Action: BUY  | Price: {current_price:.2f} | Target: <{buy_signal:.2f}")
            
            elif current_price > sell_signal:
                conn.execute("INSERT INTO portfolio (ts, action, price) VALUES (?, 'SELL', ?)", (ts, current_price))
                conn.commit()
                print(f"[{ts}] Action: SELL | Price: {current_price:.2f} | Target: >{sell_signal:.2f}")
            
            time.sleep(0.1)
        except Exception as e:
            time.sleep(0.1)

if __name__ == "__main__":
    run_backtest()
