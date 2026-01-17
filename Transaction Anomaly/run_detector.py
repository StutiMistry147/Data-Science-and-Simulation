#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime
import subprocess

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
        print("3. Start Real-time Detection (Demo)")
        print("4. View Rules Configuration")
        print("5. View Statistics")
        print("6. Save Report")
        print("7. Run Concurrency Verification (Promela)")
        print("8. Exit")
        print("\nSelect option (1-8): ", end="")
    
    def generate_dataset(self):
        """Generate sample transaction dataset"""
        print("\nGenerating sample dataset...")

        os.makedirs('data', exist_ok=True)

        df = self.simulator.generate_dataset(num_normal=50, num_anomalous=10)

        self.simulator.save_to_csv(df, 'data/transactions.csv')
        
        print(f"✓ Dataset generated with {len(df)} transactions")
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
            print("\nTop 3 anomalies by risk score:")
            top_anomalies = anomalies.nlargest(3, 'risk_score')
            
            for idx, (_, row) in enumerate(top_anomalies.iterrows(), 1):
                print(f"  {idx}. Account: {row['account_id']}")
                print(f"     Amount: ${row['amount']:.2f}")
                print(f"     Risk Score: {row['risk_score']:.1f}/100")
                if row['anomalies']:
                    for anomaly in row['anomalies']:
                        print(f"     Rule: {anomaly['rule']} - {anomaly['reason']}")
                print()
        
        return results_df
    
    def start_realtime_detection(self):
        """Start real-time anomaly detection demo"""
        print("\nStarting real-time anomaly detection DEMO...")
        print("Will simulate 20 transactions with 20% anomaly rate")
        print("Press Ctrl+C to stop early\n")

        stream = self.simulator.generate_realtime_stream(
            num_transactions=20,
            anomaly_rate=0.2
        )
        
        try:
            for i, transaction in enumerate(stream, 1):
                print(f"\nTransaction {i}:")
                print(f"  Account: {transaction['account_id']}")
                print(f"  Amount: ${transaction['amount']:.2f}")
                print(f"  Type: {transaction['transaction_type']}")
                
                result = self.detector.process_transaction(transaction)
                
                if result['is_anomalous']:
                    print(f"  🚨 ANOMALY DETECTED! Risk: {result['risk_score']:.1f}")
                    for anomaly in result['anomalies']:
                        print(f"    - {anomaly['rule']}: {anomaly['reason']}")
                else:
                    print(f"  ✓ Normal transaction")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nDetection stopped by user")
        
        print("\nReal-time demo completed!")
    
    def view_rules_configuration(self):
        """Display current rules configuration"""
        print("\nCurrent Rules Configuration:")
        print("="*60)
        
        rules = self.rule_engine.get_rules_status()
        
        for rule_name, config in rules.items():
            status = "ENABLED" if config['enabled'] else "DISABLED"
            print(f"\n{rule_name.upper()} [{status}]")
            print(f"  Description: {config['description']}")
            for key, value in config.items():
                if key not in ['enabled', 'description']:
                    print(f"  {key}: {value}")
    
    def view_statistics(self):
        """Display detection statistics"""
        self.detector.display_statistics()
    
    def save_report(self):
        """Save detection report"""
        report = self.detector.save_report('data/anomaly_report.json')
        print(f"Report saved with {len(report['anomalies'])} anomalies")
    
    def run_concurrency_verification(self):
        """Run Promela concurrency verification"""
        print("\nRunning Promela Concurrency Verification...")
        print("This verifies thread safety in anomaly detection")
        
        promela_dir = 'src/promela_verifier'
        model_file = os.path.join(promela_dir, 'detection_model.pml')
        script_file = os.path.join(promela_dir, 'verify_concurrency.sh')

        if not os.path.exists(model_file):
            print(f"Error: Promela model not found at {model_file}")
            return

        if os.path.exists(script_file):
            os.chmod(script_file, 0o755)
        
        try:
            print("Checking for Spin model checker...")
            result = subprocess.run(['which', 'spin'], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("Spin not found. Installing...")
                subprocess.run(['sudo', 'apt-get', 'update'], check=False)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'spin'], check=False)

            print("\nRunning verification (this may take a moment)...")

            original_dir = os.getcwd()
            os.chdir(promela_dir)

            print("\n1. Generating and compiling verifier...")
            subprocess.run(['spin', '-a', 'detection_model.pml'], check=True)
            subprocess.run(['gcc', '-o', 'pan', 'pan.c'], check=True)
            
            print("\n2. Checking for deadlocks...")
            result = subprocess.run(['./pan', '-l'], capture_output=True, text=True)
            print(result.stdout)
            
            if "errors: 0" in result.stdout:
                print("✓ No deadlocks detected!")
            else:
                print("✗ Potential deadlocks found")
            
            print("\n3. Running assertion checks...")
            result = subprocess.run(['./pan', '-a'], capture_output=True, text=True)
            print(result.stdout[-500:])

            os.remove('pan')
            files_to_remove = ['pan.c', 'pan.h', 'pan.b', 'pan.t', 'pan.m']
            for file in files_to_remove:
                if os.path.exists(file):
                    os.remove(file)

            os.chdir(original_dir)
            
            print("\n✓ Concurrency verification completed!")
            
        except Exception as e:
            print(f"Error during verification: {e}")
            print("\nYou can still run the Python detection without Promela verification")
    
    def run(self):
        """Main application loop"""
        while True:
            self.display_menu()
            
            try:
                choice = input().strip()
                
                if choice == '1':
                    self.generate_dataset()
                elif choice == '2':
                    self.run_batch_detection()
                elif choice == '3':
                    self.start_realtime_detection()
                elif choice == '4':
                    self.view_rules_configuration()
                elif choice == '5':
                    self.view_statistics()
                elif choice == '6':
                    self.save_report()
                elif choice == '7':
                    self.run_concurrency_verification()
                elif choice == '8':
                    print("\nExiting Transaction Anomaly Detector. Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
                
                print("\nPress Enter to continue...", end="")
                input()
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
                print("\nPress Enter to continue...", end="")
                input()

def main():
    detector = TransactionAnomalyDetector()
    detector.run()

if __name__ == "__main__":
    main()
