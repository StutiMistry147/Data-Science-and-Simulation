# Portfolio Risk Dashboard
## Overview
CLI-based financial risk analysis tool that calculates portfolio risk metrics using statistical methods. Implements Value at Risk (VaR), Sharpe ratio, and correlation analysis for investment portfolios.
Core Features:
- Portfolio value tracking with P&L calculation
- Risk metrics: VaR, CVaR, Sharpe ratio, maximum drawdown
- Correlation matrix analysis
- SQLite data caching
- JSON report generation

## Architecture
CSV Portfolio → Data Fetcher → Risk Calculator → Terminal Display/JSON Report
## Execution
Requirements 
- Python 3.8+
- Ubuntu/linux
Execution :
1. ```
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install all required packages
   ```pip install pandas numpy yfinance matplotlib tabulate scipy seaborn```
3. ```python simple_dashboard.py```

## Result
<img width="827" height="668" alt="image" src="https://github.com/user-attachments/assets/5364fcaa-f517-4dbd-9cbf-262b1d94b3a9" />
<img width="451" height="696" alt="image" src="https://github.com/user-attachments/assets/66b6817a-2969-4418-aa50-d554173681e9" />
<img width="919" height="736" alt="image" src="https://github.com/user-attachments/assets/b9349ce5-16a6-49ec-9fc2-953cd318c3a7" />
