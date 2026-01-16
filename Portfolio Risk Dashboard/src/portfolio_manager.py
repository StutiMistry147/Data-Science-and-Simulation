import pandas as pd
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
from datetime import datetime
import json

class PortfolioManager:
    def __init__(self, portfolio_file='data/sample_portfolio.csv'):
        self.portfolio_file = portfolio_file
        self.portfolio_df = None
        self.current_prices = {}
        self.risk_metrics = {}
        
    def load_portfolio(self):
        """Load portfolio from CSV file"""
        try:
            self.portfolio_df = pd.read_csv(self.portfolio_file)
            self.portfolio_df['purchase_date'] = pd.to_datetime(self.portfolio_df['purchase_date'])
            return True
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return False
    
    def update_prices(self, data_fetcher):
        """Update current prices for all tickers"""
        if self.portfolio_df is None:
            print("Portfolio not loaded")
            return
        
        tickers = self.portfolio_df['ticker'].unique().tolist()
        stock_data = data_fetcher.fetch_stock_data(tickers, days=30)
        
        for ticker in tickers:
            ticker_data = stock_data[stock_data['Ticker'] == ticker]
            if not ticker_data.empty:
                latest_price = ticker_data.iloc[-1]['Close']
                self.current_prices[ticker] = latest_price
            else:
                print(f"Warning: No data for {ticker}")
                self.current_prices[ticker] = 0
    
    def get_portfolio_summary(self):
        """Generate portfolio summary"""
        if self.portfolio_df is None or not self.current_prices:
            return None
        
        from src.risk_calculator import RiskCalculator
        portfolio_value_df = RiskCalculator.calculate_portfolio_value(
            self.portfolio_df, self.current_prices
        )
        
        summary = {
            'total_investment': float(portfolio_value_df['cost_basis'].sum()),
            'current_value': float(portfolio_value_df['current_value'].sum()),
            'total_pnl': float(portfolio_value_df['unrealized_pnl'].sum()),
            'total_pnl_percent': float(
                portfolio_value_df['unrealized_pnl'].sum() / 
                portfolio_value_df['cost_basis'].sum() * 100
            ),
            'holdings': portfolio_value_df.to_dict('records')
        }
        
        return summary
    
    def display_portfolio_table(self):
        """Display portfolio in formatted table"""
        summary = self.get_portfolio_summary()
        if summary is None:
            print("No portfolio data available")
            return
        
        print("\n" + "="*80)
        print("PORTFOLIO SUMMARY")
        print("="*80)
        
        
        total_summary = [
            ["Total Investment", f"${summary['total_investment']:,.2f}"],
            ["Current Value", f"${summary['current_value']:,.2f}"],
            ["Total P&L", f"${summary['total_pnl']:,.2f}"],
            ["P&L %", f"{summary['total_pnl_percent']:.2f}%"]
        ]
        
        print(tabulate(total_summary, tablefmt="grid"))
        print("\n")
        

        holdings_data = []
        for holding in summary['holdings']:
            holdings_data.append([
                holding['ticker'],
                holding['shares'],
                f"${holding['purchase_price']:.2f}",
                f"${holding['current_price']:.2f}",
                f"${holding['current_value']:.2f}",
                f"${holding['unrealized_pnl']:.2f}",
                f"{holding['pnl_percent']:.2f}%"
            ])
        
        headers = ["Ticker", "Shares", "Cost", "Current", "Value", "P&L", "P&L %"]
        print(tabulate(holdings_data, headers=headers, tablefmt="grid"))
    
    def generate_risk_report(self, data_fetcher):
        """Generate comprehensive risk report"""
        from src.risk_calculator import RiskCalculator
        
        if self.portfolio_df is None:
            return
        
        tickers = self.portfolio_df['ticker'].tolist()
        

        stock_data = data_fetcher.fetch_stock_data(tickers, days=365)
        
        if stock_data.empty:
            print("No historical data available for risk analysis")
            return
        

        returns_df = RiskCalculator.calculate_returns(stock_data, tickers)
        
        if returns_df.empty:
            print("Insufficient data for returns calculation")
            return
        
        portfolio_value_df = RiskCalculator.calculate_portfolio_value(
            self.portfolio_df, self.current_prices
        )
        total_value = portfolio_value_df['current_value'].sum()
        weights = {}
        
        for ticker in tickers:
            ticker_value = portfolio_value_df[
                portfolio_value_df['ticker'] == ticker
            ]['current_value'].sum()
            weights[ticker] = ticker_value / total_value
        

        individual_metrics = {}
        for ticker in tickers:
            if ticker in returns_df.columns:
                returns = returns_df[ticker].dropna()
                if len(returns) > 0:
                    individual_metrics[ticker] = {
                        'daily_volatility': np.std(returns),
                        'annual_volatility': np.std(returns) * np.sqrt(252),
                        'sharpe': RiskCalculator.calculate_sharpe_ratio(returns),
                        'var_95': RiskCalculator.calculate_var(returns, 0.95),
                        'max_drawdown': RiskCalculator.calculate_max_drawdown(returns)
                    }
        

        weights_array = np.array([weights[ticker] for ticker in tickers if ticker in returns_df.columns])
        valid_tickers = [ticker for ticker in tickers if ticker in returns_df.columns]
        valid_returns = returns_df[valid_tickers]
        
        portfolio_metrics = RiskCalculator.calculate_portfolio_metrics(
            valid_returns, weights_array
        )

        correlation_matrix = RiskCalculator.calculate_correlation_matrix(valid_returns)
        
        self.risk_metrics = {
            'individual': individual_metrics,
            'portfolio': portfolio_metrics,
            'correlation': correlation_matrix,
            'weights': weights
        }
        
        return self.risk_metrics
    
    def display_risk_report(self):
        """Display risk report in terminal"""
        if not self.risk_metrics:
            print("No risk metrics calculated. Run generate_risk_report() first.")
            return
        
        print("\n" + "="*80)
        print("RISK ANALYSIS REPORT")
        print("="*80)
        
        print("\nPORTFOLIO-LEVEL METRICS:")
        print("-"*40)
        
        portfolio_data = []
        for key, value in self.risk_metrics['portfolio'].items():
            if 'ratio' in key or 'drawdown' in key:
                formatted_value = f"{value:.4f}"
            elif 'var' in key or 'cvar' in key:
                formatted_value = f"{value*100:.2f}%"
            elif 'return' in key or 'volatility' in key:
                formatted_value = f"{value*100:.2f}%"
            else:
                formatted_value = f"{value:.6f}"
            
            portfolio_data.append([key.replace('_', ' ').title(), formatted_value])
        
        print(tabulate(portfolio_data, tablefmt="grid"))
        
        print("\nINDIVIDUAL STOCK METRICS:")
        print("-"*40)
        
        individual_data = []
        for ticker, metrics in self.risk_metrics['individual'].items():
            individual_data.append([
                ticker,
                f"{metrics['annual_volatility']*100:.2f}%",
                f"{metrics['sharpe']:.2f}",
                f"{metrics['var_95']*100:.2f}%",
                f"{metrics['max_drawdown']*100:.2f}%"
            ])
        
        headers = ["Ticker", "Ann. Vol", "Sharpe", "VaR 95%", "Max DD"]
        print(tabulate(individual_data, headers=headers, tablefmt="grid"))
        
        # Weights
        print("\nPORTFOLIO WEIGHTS:")
        print("-"*40)
        
        weights_data = []
        for ticker, weight in self.risk_metrics['weights'].items():
            weights_data.append([ticker, f"{weight*100:.2f}%"])
        
        print(tabulate(weights_data, tablefmt="grid"))
        
        print("\nTOP CORRELATIONS:")
        print("-"*40)
        
        corr_matrix = self.risk_metrics['correlation']
        correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                ticker1 = corr_matrix.columns[i]
                ticker2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                correlations.append((abs(corr_value), ticker1, ticker2, corr_value))
        
        correlations.sort(reverse=True, key=lambda x: x[0])
        
        top_corr_data = []
        for _, ticker1, ticker2, corr_value in correlations[:5]:
            top_corr_data.append([
                f"{ticker1}-{ticker2}",
                f"{corr_value:.3f}",
                "High" if abs(corr_value) > 0.7 else "Medium" if abs(corr_value) > 0.3 else "Low"
            ])
        
        if top_corr_data:
            print(tabulate(top_corr_data, headers=["Pair", "Correlation", "Level"], tablefmt="grid"))
    
    def plot_correlation_heatmap(self):
        """Plot correlation heatmap (optional visual)"""
        if 'correlation' not in self.risk_metrics:
            return
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                self.risk_metrics['correlation'],
                annot=True,
                cmap='coolwarm',
                center=0,
                square=True
            )
            plt.title('Stock Correlation Matrix')
            plt.tight_layout()
            
            plt.savefig('data/correlation_heatmap.png', dpi=100)
            print("Correlation heatmap saved to data/correlation_heatmap.png")
            plt.close()
            
        except ImportError:
            print("Install seaborn for heatmap visualization: pip install seaborn")
        except Exception as e:
            print(f"Error generating heatmap: {e}")
    
    def save_report(self, filename='data/risk_report.json'):
        """Save risk report to JSON file"""
        import json
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_summary': self.get_portfolio_summary(),
            'risk_metrics': self.risk_metrics
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report saved to {filename}")
