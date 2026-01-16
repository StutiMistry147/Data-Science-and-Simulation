import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os

class DataFetcher:
    def __init__(self, db_path='data/historical_data.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for caching"""
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                ticker TEXT,
                date DATE,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (ticker, date)
            )
        ''')
        conn.commit()
        conn.close()
    
    def fetch_stock_data(self, tickers, days=365):
        """Fetch historical stock data, cache in database"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        

        cached_data = self._load_from_cache(tickers, start_date, end_date)
        if cached_data is not None:
            return cached_data
        

        try:
            data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
            

            all_data = []
            for ticker in tickers:
                if ticker in data.columns.levels[0]:
                    ticker_data = data[ticker].reset_index()
                    ticker_data['Ticker'] = ticker
                    all_data.append(ticker_data)
            
            combined_data = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
            

            self._save_to_cache(combined_data)
            
            return combined_data
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def _load_from_cache(self, tickers, start_date, end_date):
        """Load cached data from SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT * FROM stock_prices 
                WHERE ticker IN ({}) AND date BETWEEN ? AND ?
            '''.format(','.join(['?']*len(tickers)))
            
            params = tickers + [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df if not df.empty else None
            
        except Exception as e:
            print(f"Cache error: {e}")
            return None
    
    def _save_to_cache(self, df):
        """Save data to SQLite cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            if not df.empty:
                df_to_save = df.copy()
                if 'Date' in df_to_save.columns:
                    df_to_save['date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
                elif 'Date' not in df_to_save.columns and 'date' not in df_to_save.columns:
                    df_to_save['date'] = datetime.now().strftime('%Y-%m-%d')

                columns_needed = ['ticker', 'date', 'Open', 'High', 'Low', 'Close', 'Volume']
                df_to_save = df_to_save.rename(columns={
                    'Ticker': 'ticker',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                
                df_to_save[['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']].to_sql(
                    'stock_prices', conn, if_exists='append', index=False
                )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Cache save error: {e}")
