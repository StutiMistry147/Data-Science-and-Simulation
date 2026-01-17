import random
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
import uuid

class TransactionSimulator:
    def __init__(self, seed=42):
        random.seed(seed)
        
        self.accounts = [
            'ACC001', 'ACC002', 'ACC003', 'ACC004', 'ACC005',
            'ACC006', 'ACC007', 'ACC008', 'ACC009', 'ACC010'
        ]
        
        self.transaction_types = [
            'TRANSFER', 'WITHDRAWAL', 'DEPOSIT', 'BILL_PAYMENT', 'ONLINE_PURCHASE'
        ]
        
        self.merchants = [
            'AMAZON', 'EBAY', 'NETFLIX', 'SPOTIFY', 'UBER', 
            'WALMART', 'STARBUCKS', 'APPLE_STORE', 'GOOGLE_PLAY', 'MICROSOFT'
        ]
        
        self.countries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'SG', 'IN']
        
    def generate_normal_transaction(self) -> Dict[str, Any]:
        """Generate a normal transaction"""
        timestamp = datetime.now() - timedelta(
            minutes=random.randint(0, 10080),
            seconds=random.randint(0, 59)
        )
        
        amount = round(random.uniform(10, 1000), 2)
        account = random.choice(self.accounts)
        transaction_type = random.choice(self.transaction_types)
        
        return {
            'transaction_id': str(uuid.uuid4())[:8],
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'account_id': account,
            'transaction_type': transaction_type,
            'amount': amount,
            'currency': 'USD',
            'merchant': random.choice(self.merchants) if transaction_type == 'ONLINE_PURCHASE' else 'BANK',
            'country': random.choice(self.countries),
            'ip_address': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'device_id': f"DEV{random.randint(1000, 9999)}",
            'is_fraudulent': False
        }
    
    def generate_anomalous_transaction(self) -> Dict[str, Any]:
        """Generate an anomalous transaction based on patterns"""
        base_transaction = self.generate_normal_transaction()
        
        anomaly_type = random.choice([
            'large_amount', 'rapid_transactions', 'odd_hours', 
            'multiple_countries', 'suspicious_merchant'
        ])
        
        if anomaly_type == 'large_amount':
            base_transaction['amount'] = round(random.uniform(5000, 50000), 2)
            base_transaction['is_fraudulent'] = True
            base_transaction['anomaly_reason'] = 'LARGE_AMOUNT'
            
        elif anomaly_type == 'rapid_transactions':
            base_transaction['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            base_transaction['is_fraudulent'] = True
            base_transaction['anomaly_reason'] = 'RAPID_TRANSACTION'
            
        elif anomaly_type == 'odd_hours':
            odd_time = datetime.now().replace(
                hour=random.randint(2, 5),
                minute=random.randint(0, 59)
            )
            base_transaction['timestamp'] = odd_time.strftime('%Y-%m-%d %H:%M:%S')
            base_transaction['is_fraudulent'] = True
            base_transaction['anomaly_reason'] = 'ODD_HOURS'
            
        elif anomaly_type == 'multiple_countries':
            unusual_countries = ['RU', 'CN', 'NG', 'UA', 'BR']
            base_transaction['country'] = random.choice(unusual_countries)
            base_transaction['is_fraudulent'] = True
            base_transaction['anomaly_reason'] = 'SUSPICIOUS_COUNTRY'
            
        elif anomaly_type == 'suspicious_merchant':
            suspicious_merchants = ['DARK_WEB_STORE', 'UNKNOWN_VENDOR', 'TEST_MERCHANT']
            base_transaction['merchant'] = random.choice(suspicious_merchants)
            base_transaction['is_fraudulent'] = True
            base_transaction['anomaly_reason'] = 'SUSPICIOUS_MERCHANT'
        
        return base_transaction
    
    def generate_dataset(self, num_normal=950, num_anomalous=50) -> pd.DataFrame:
        """Generate dataset with mix of normal and anomalous transactions"""
        transactions = []
        
        print(f"Generating {num_normal} normal transactions...")
        for _ in range(num_normal):
            transactions.append(self.generate_normal_transaction())
        
        print(f"Generating {num_anomalous} anomalous transactions...")
        for _ in range(num_anomalous):
            transactions.append(self.generate_anomalous_transaction())
        
        random.shuffle(transactions)
        
        df = pd.DataFrame(transactions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = 'data/transactions.csv'):
        """Save transactions to CSV"""
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} transactions to {filename}")
        return df
    
    def generate_realtime_stream(self, num_transactions=100, anomaly_rate=0.05):
        """Generate real-time transaction stream"""
        for i in range(num_transactions):
            if random.random() < anomaly_rate:
                yield self.generate_anomalous_transaction()
            else:
                yield self.generate_normal_transaction()
