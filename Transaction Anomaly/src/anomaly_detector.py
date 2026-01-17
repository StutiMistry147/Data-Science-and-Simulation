import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import threading
import time
from tabulate import tabulate
import json

class AnomalyDetector:
    def __init__(self, rule_engine):
        self.rule_engine = rule_engine
        self.detected_anomalies = []
        self.stats = {
            'total_transactions': 0,
            'anomalous_transactions': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'rules_triggered': {}
        }
        self.lock = threading.Lock()

        self.account_history = {}
    
    def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Process single transaction and detect anomalies"""
        with self.lock:
            self.stats['total_transactions'] += 1

            account = transaction['account_id']
            previous = self.account_history.get(account)

            result = self.rule_engine.evaluate_transaction(transaction, previous)

            self.account_history[account] = transaction

            if result['is_anomalous']:
                self.stats['anomalous_transactions'] += 1
                self.detected_anomalies.append(result)
                
                for rule in result['triggered_rules']:
                    self.stats['rules_triggered'][rule] = self.stats['rules_triggered'].get(rule, 0) + 1

            result['processing_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return result
    
    def process_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process batch of transactions"""
        results = []
        for transaction in transactions:
            results.append(self.process_transaction(transaction))
        return results
    
    def process_csv(self, filepath: str) -> pd.DataFrame:
        """Process transactions from CSV file"""
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        for _, row in df.iterrows():
            transaction = row.to_dict()
            result = self.process_transaction(transaction)
            results.append(result)
        
        return pd.DataFrame(results)
    
    def stream_detection(self, transaction_stream, interval=1):
        """Process transactions from a stream"""
        print("Starting real-time anomaly detection...")
        print("Press Ctrl+C to stop\n")
        
        try:
            for transaction in transaction_stream:
                result = self.process_transaction(transaction)
                
                if result['is_anomalous']:
                    self._display_anomaly_alert(result)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nStream stopped by user")
            self.display_statistics()
    
    def _display_anomaly_alert(self, result: Dict[str, Any]):
        """Display anomaly alert in terminal"""
        print("\n" + "="*60)
        print("X ANOMALY DETECTED!")
        print("="*60)
        
        alert_data = [
            ["Transaction ID", result['transaction_id']],
            ["Account", result['account_id']],
            ["Time", result['timestamp']],
            ["Amount", f"${result['amount']:.2f}"],
            ["Risk Score", f"{result['risk_score']:.1f}/100"],
            ["Anomalies", len(result['anomalies'])]
        ]
        
        print(tabulate(alert_data, tablefmt="grid"))
        if result['anomalies']:
            print("\nTriggered Rules:")
            for anomaly in result['anomalies']:
                print(f"  • {anomaly['rule']}: {anomaly['reason']} ({anomaly['severity']})")
    
    def display_statistics(self):
        """Display detection statistics"""
        print("\n" + "="*60)
        print("DETECTION STATISTICS")
        print("="*60)
        
        if self.stats['total_transactions'] == 0:
            print("No transactions processed")
            return
        
        anomaly_rate = (self.stats['anomalous_transactions'] / self.stats['total_transactions']) * 100
        
        stats_data = [
            ["Total Transactions", self.stats['total_transactions']],
            ["Anomalies Detected", self.stats['anomalous_transactions']],
            ["Anomaly Rate", f"{anomaly_rate:.2f}%"],
            ["False Positives", self.stats['false_positives']],
            ["False Negatives", self.stats['false_negatives']]
        ]
        
        print(tabulate(stats_data, tablefmt="grid"))

        if self.stats['rules_triggered']:
            print("\nRules Triggered:")
            rules_data = []
            for rule, count in self.stats['rules_triggered'].items():
                rules_data.append([rule, count])
            
            print(tabulate(rules_data, headers=["Rule", "Count"], tablefmt="grid"))
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Get detailed detection report"""
        return {
            'summary': {
                'total_transactions': self.stats['total_transactions'],
                'anomalies_detected': self.stats['anomalous_transactions'],
                'detection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'anomalies': self.detected_anomalies,
            'rules_configuration': self.rule_engine.get_rules_status(),
            'statistics': self.stats
        }
    
    def save_report(self, filename: str = 'data/anomaly_report.json'):
        """Save detection report to JSON file"""
        report = self.get_detailed_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nReport saved to {filename}")
        return report
    
    def evaluate_performance(self, ground_truth: pd.DataFrame):
        """Evaluate detector performance against ground truth"""
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        for _, row in ground_truth.iterrows():
            transaction = row.to_dict()
            result = self.process_transaction(transaction)
            
            actual_fraud = transaction.get('is_fraudulent', False)
            detected_fraud = result['is_anomalous']
            
            if actual_fraud and detected_fraud:
                true_positives += 1
            elif not actual_fraud and detected_fraud:
                false_positives += 1
            elif actual_fraud and not detected_fraud:
                false_negatives += 1

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        performance = {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
        
        self.stats['false_positives'] = false_positives
        self.stats['false_negatives'] = false_negatives
        
        return performance
