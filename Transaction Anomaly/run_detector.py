#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from transaction_simulator import TransactionSimulator
from rule_engine import RuleEngine
from anomaly_detector import AnomalyDetector
import pandas as pd

class TransactionAnomalyDetector:
    def __init__(self):
        self.simulator = TransactionSimulator()
        self.rule_engine = RuleEngine()
        self.detector = AnomalyDetector(self.rule_engine)
        
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("TRANSACTION ANOMALY DETECTOR")
        print("="*60)
        print("1. Generate Sample Dataset")
        print("2. Run Batch Detection")
        print("3. Start Real-time Detection")
        print("4. View Rules Configuration")
        print("5. Toggle Rules")
        print("6. View Statistics")
        print("7. Save Report")
        print("8. Run Concurrency Verification (Promela)")
        print("9. Exit")
        print("\nSelect option (1-9): ", end="")
    
    def generate_dataset(self):
        """Generate sample transaction dataset"""
        print("\nGenerating sample dataset...")

        os.makedirs('data', exist_ok=True)

        df = self.simulator.generate_dataset(num_normal=200, num_anomalous=20)

        self.simulator.save_to_csv(df, 'data/transactions.csv')
        
        print(f"Dataset generated with {len(df)} transactions")
        print(f"  - Normal transactions: {len(df[~df['is_fraudulent']])}")
        print(f"  - Anomalous transactions: {len(df[df['is_fraudulent']])}")
        
        return df
    
    def run_batch_detection(self):
        """Run detection on batch of transactions"""
        if not os.path.exists('data/transactions.csv'):
            print("\nNo dataset found. Generating one first...")
            self.generate_dataset()
        
        print("\nRunning batch anomaly detection...")

        results_df = self.detector.process_csv('data/transactions.csv')

        anomalies = results_df[results_df['is_anomalous']]
        
        print(f"\nDetection Results:")
        print(f"  Total transactions processed: {len(results_df)}")
        print(f"  Anomalies detected: {len(anomalies)}")
        
        if len(anomalies) > 0:
            print("\nTop anomalies by risk score:")
            top_anomalies = anomalies.nlargest(5, 'risk_score')
            
            for _, row in top_anomalies.iterrows():
                print(f"  • {row['account_id']}: ${row['amount']:.2f} "
                      f"(Risk: {row['risk_score']:.1f})")
        
        return results_df
    
    def start_realtime_detection(self):
        """Start real-time anomaly detection"""
        print("\nStarting real-time anomaly detection...")
        print("Gener
