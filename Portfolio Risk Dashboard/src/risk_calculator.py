import numpy as np
import pandas as pd
from scipy import stats
import math

class RiskCalculator:
    @staticmethod
    def calculate_portfolio_value(portfolio_df, current_prices):
        """Calculate current portfolio value"""
        portfolio_df = portfolio_df.copy()
        portfolio_df['current_price'] = portfolio_df['ticker'].map(current_prices)
        portfolio_df['current_value'] = portfolio_df['shares'] * portfolio_df['current_price']
        portfolio_df['cost_basis'] = portfolio_df['shares'] * portfolio_df['purchase_price']
        portfolio_df['unrealized_pnl'] = portfolio_df['current_value'] - portfolio_df['cost_basis']
        portfolio_df['pnl_percent'] = (portfolio_df['unrealized_pnl'] / portfolio_df['cost_basis'] * 100)
        
        return portfolio_df
    
    @staticmethod
    def calculate_returns(prices_df, tickers):
        """Calculate daily returns for each stock"""
        returns_data = {}
        
        for ticker in tickers:
            ticker_data = prices_df[prices_df['Ticker'] == ticker]
            if not ticker_data.empty and 'Close' in ticker_data.columns:
                prices = ticker_data['Close'].values
                returns = np.diff(prices) / prices[:-1] 
                returns_data[ticker] = returns
        
        return pd.DataFrame(returns_data)
    
    @staticmethod
    def calculate_var(returns, confidence_level=0.95, method='historical'):
        """Calculate Value at Risk"""
        if method == 'historical':
            var = np.percentile(returns, (1 - confidence_level) * 100)
            return var
        elif method == 'parametric':
            mean = np.mean(returns)
            std = np.std(returns)
            z_score = stats.norm.ppf(1 - confidence_level)
            var = mean + z_score * std
            return var
        else:
            raise ValueError("Method must be 'historical' or 'parametric'")
    
    @staticmethod
    def calculate_cvar(returns, confidence_level=0.95):
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = RiskCalculator.calculate_var(returns, confidence_level, 'historical')
        cvar = returns[returns <= var].mean()
        return cvar
    
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02/252):
        """Calculate Sharpe ratio (daily)"""
        excess_returns = returns - risk_free_rate
        if len(excess_returns) > 0 and np.std(excess_returns) > 0:
            sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
            return sharpe
        return 0
    
    @staticmethod
    def calculate_sortino_ratio(returns, risk_free_rate=0.02/252, target_return=0):
        """Calculate Sortino ratio"""
        excess_returns = returns - risk_free_rate
        downside_returns = returns[returns < target_return] - target_return
        
        if len(downside_returns) > 0:
            downside_std = np.std(downside_returns)
            if downside_std > 0:
                sortino = np.mean(excess_returns) / downside_std * np.sqrt(252)
                return sortino
        return 0
    
    @staticmethod
    def calculate_max_drawdown(returns):
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return max_drawdown
    
    @staticmethod
    def calculate_correlation_matrix(returns_df):
        """Calculate correlation matrix"""
        return returns_df.corr()
    
    @staticmethod
    def calculate_portfolio_metrics(portfolio_returns, weights):
        """Calculate portfolio-level risk metrics"""
        portfolio_returns_series = (portfolio_returns * weights).sum(axis=1)
        
        metrics = {
            'daily_mean_return': float(np.mean(portfolio_returns_series)),
            'daily_std_dev': float(np.std(portfolio_returns_series)),
            'annualized_return': float(np.mean(portfolio_returns_series) * 252),
            'annualized_volatility': float(np.std(portfolio_returns_series) * np.sqrt(252)),
            'sharpe_ratio': RiskCalculator.calculate_sharpe_ratio(portfolio_returns_series),
            'sortino_ratio': RiskCalculator.calculate_sortino_ratio(portfolio_returns_series),
            'max_drawdown': RiskCalculator.calculate_max_drawdown(portfolio_returns_series),
            'var_95': RiskCalculator.calculate_var(portfolio_returns_series, 0.95),
            'cvar_95': RiskCalculator.calculate_cvar(portfolio_returns_series, 0.95),
            'var_99': RiskCalculator.calculate_var(portfolio_returns_series, 0.99),
            'cvar_99': RiskCalculator.calculate_cvar(portfolio_returns_series, 0.99)
        }
        
        return metrics
