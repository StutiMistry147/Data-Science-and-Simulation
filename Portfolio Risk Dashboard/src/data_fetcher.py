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
        if cached_data is not None and not cached_data.empty:
            print(f"Loaded {len(cached_data)} rows from cache")
            return cached_data
        
        print(f"Fetching data for {len(tickers)} tickers from Yahoo Finance...")
        
        try:
            data = yf.download(
                tickers, 
                start=start_date.strftime('%Y-%m-%d'), 
                end=end_date.strftime('%Y-%m-%d'),
                progress=False,
                group_by='ticker' if len(tickers) > 1 else False
            )
            
            print(f"Raw data shape: {data.shape}")
            print(f"Raw data columns: {data.columns}")
            
            processed_data = self._process_yfinance_data(data, tickers)
            

            self._save_to_cache(processed_data)
            
            print(f"Processed data shape: {processed_data.shape}")
            return processed_data
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def _process_yfinance_data(self, data, tickers):
        """Process yfinance data into consistent format"""
        if len(tickers) == 1:
            df = data.reset_index()
            df['Ticker'] = tickers[0]
            return df
        else:
            all_data = []
            
            if isinstance(data.columns, pd.MultiIndex):
                for ticker in tickers:
                    try:
                        if ticker in data.columns.get_level_values(0):
                            ticker_data = data[ticker].copy()
                            ticker_data = ticker_data.reset_index()
                            ticker_data['Ticker'] = ticker
                            all_data.append(ticker_data)
                    except:
                        continue
            else:
                data = data.reset_index()
                if 'Ticker' not in data.columns:
                    for ticker in tickers:
                        if any(ticker in str(col) for col in data.columns):
                            data['Ticker'] = ticker
                            all_data.append(data)
                            break
            
            if all_data:
                combined = pd.concat(all_data, ignore_index=True)
 
                column_map = {
                    'Date': 'Date',
                    'Open': 'Open',
                    'High': 'High',
                    'Low': 'Low',
                    'Close': 'Close',
                    'Adj Close': 'Close',  
                    'Volume': 'Volume'
                }
                

                for old_col in combined.columns:
                    for key, new_col in column_map.items():
                        if key in old_col:
                            combined = combined.rename(columns={old_col: new_col})
                            break
                
                return combined
            else:
                print("Warning: No data processed")
                return pd.DataFrame()
    
    def _load_from_cache(self, tickers, start_date, end_date):
        """Load cached data from SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            

            placeholders = ','.join(['?'] * len(tickers))
            query = f'''
                SELECT * FROM stock_prices 
                WHERE ticker IN ({placeholders}) 
                AND date BETWEEN ? AND ?
                ORDER BY ticker, date
            '''
            
            params = tickers + [start_str, end_str]
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if not df.empty:
                df = df.rename(columns={
                    'ticker': 'Ticker',
                    'date': 'Date',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })
                df['Date'] = pd.to_datetime(df['Date'])
            
            return df
            
        except Exception as e:
            print(f"Cache error: {e}")
            return pd.DataFrame()
    
    def _save_to_cache(self, df):
        """Save data to SQLite cache"""
        try:
            if df.empty:
                return
            
            conn = sqlite3.connect(self.db_path)
            
            df_to_save = df.copy()
            

            required_cols = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            
            for col in required_cols:
                if col not in df_to_save.columns:

                    for actual_col in df_to_save.columns:
                        if col.lower() in actual_col.lower():
                            df_to_save = df_to_save.rename(columns={actual_col: col})
                            break

            df_to_save['date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
            df_to_save['ticker'] = df_to_save['Ticker']
            
            cache_cols = ['ticker', 'date', 'Open', 'High', 'Low', 'Close', 'Volume']
            df_to_save = df_to_save[[col for col in cache_cols if col in df_to_save.columns]]
            
            df_to_save = df_to_save.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            df_to_save.to_sql(
                'stock_prices', 
                conn, 
                if_exists='append', 
                index=False,
                method='multi'
            )
            
            conn.commit()
            conn.close()
            print(f"Cached {len(df_to_save)} rows to database")
            
        except Exception as e:
            print(f"Cache save error: {e}")
            import traceback
            traceback.print_exc()
