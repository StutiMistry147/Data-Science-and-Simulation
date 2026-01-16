#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import DataFetcher
from src.portfolio_manager import PortfolioManager
import time
from datetime import datetime

class RiskDashboard:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.portfolio_manager = PortfolioManager()
        self.running = True
    
    def display_header(self):
        """Display dashboard header"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n" + "="*80)
        print("PORTFOLIO RISK DASHBOARD")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
    
    def display_menu(self):
        """Display main menu"""
        print("\nMAIN MENU:")
        print("1. Load Portfolio")
        print("2. Update Prices")
        print("3. View Portfolio")
        print("4. Run Risk Analysis")
        print("5. View Risk Report")
        print("6. Generate Correlation Heatmap")
        print("7. Save Report")
        print("8. Exit")
        print("\nSelect an option (1-8): ", end="")
    
    def run(self):
        """Main dashboard loop"""
        while self.running:
            self.display_header()
            self.display_menu()
            
            try:
                choice = input().strip()
                
                if choice == '1':
                    self.load_portfolio()
                elif choice == '2':
                    self.update_prices()
                elif choice == '3':
                    self.view_portfolio()
                elif choice == '4':
                    self.run_risk_analysis()
                elif choice == '5':
                    self.view_risk_report()
                elif choice == '6':
                    self.generate_heatmap()
                elif choice == '7':
                    self.save_report()
                elif choice == '8':
                    self.exit_dashboard()
                else:
                    print("Invalid choice. Press Enter to continue...")
                    input()
                    
            except KeyboardInterrupt:
                self.exit_dashboard()
            except Exception as e:
                print(f"Error: {e}")
                print("Press Enter to continue...")
                input()
    
    def load_portfolio(self):
        """Load portfolio from file"""
        print("\nLoading portfolio...")
        if self.portfolio_manager.load_portfolio():
            print("Portfolio loaded successfully!")
        else:
            print("Failed to load portfolio.")
        print("\nPress Enter to continue...")
        input()
    
    def update_prices(self):
        """Update stock prices"""
        print("\nUpdating stock prices...")
        if self.portfolio_manager.portfolio_df is None:
            print("Please load portfolio first!")
        else:
            print("Fetching latest prices (this may take a moment)...")
            self.portfolio_manager.update_prices(self.data_fetcher)
            print("Prices updated!")
        
        print("\nPress Enter to continue...")
        input()
    
    def view_portfolio(self):
        """Display portfolio"""
        if self.portfolio_manager.portfolio_df is None:
            print("Please load portfolio first!")
        else:
            self.portfolio_manager.display_portfolio_table()
        
        print("\nPress Enter to continue...")
        input()
    
    def run_risk_analysis(self):
        """Run risk analysis"""
        print("\nRunning risk analysis...")
        if self.portfolio_manager.portfolio_df is None:
            print("Please load portfolio first!")
        elif not self.portfolio_manager.current_prices:
            print("Please update prices first!")
        else:
            print("Calculating risk metrics (this may take a moment)...")
            self.portfolio_manager.generate_risk_report(self.data_fetcher)
            print("Risk analysis complete!")
        
        print("\nPress Enter to continue...")
        input()
    
    def view_risk_report(self):
        """Display risk report"""
        self.portfolio_manager.display_risk_report()
        print("\nPress Enter to continue...")
        input()
    
    def generate_heatmap(self):
        """Generate correlation heatmap"""
        if not self.portfolio_manager.risk_metrics:
            print("Please run risk analysis first!")
        else:
            self.portfolio_manager.plot_correlation_heatmap()
        
        print("\nPress Enter to continue...")
        input()
    
    def save_report(self):
        """Save report to file"""
        if not self.portfolio_manager.risk_metrics:
            print("Please run risk analysis first!")
        else:
            filename = input("Enter filename (default: data/risk_report.json): ").strip()
            if not filename:
                filename = 'data/risk_report.json'
            self.portfolio_manager.save_report(filename)
        
        print("\nPress Enter to continue...")
        input()
    
    def exit_dashboard(self):
        """Exit the dashboard"""
        print("\nExiting Portfolio Risk Dashboard...")
        self.running = False

def main():
    dashboard = RiskDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
