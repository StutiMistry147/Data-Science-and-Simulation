# Trading Backtester
## Overview
- This project involves developing a formal prototype of a High-Frequency Trading (HFT) Backtester using C++, Python, and the SPIN Model Checker. 
- The system is designed as a Real-Time Data Pipeline, simulating a stock exchange environment where price updates occur at millisecond intervals.

## Architecture
- <ins>Exchange Process (C++)</ins>: Acts as the master data source, generating stochastic market shocks using a Normal Distribution to simulate realistic volatility.
- <ins>Backtester Process (Python)</ins>: Monitors the market feed, calculates rolling averages using Pandas, and executes the trading strategy.
- <ins>Database Layer (SQL)</ins>: Uses SQLite with PRIMARY KEY constraints to ensure data integrity and prevent double-counting of trades during high-frequency bursts.
- <ins>Order State Machine (Promela)</ins>: Represents the global synchronization logic between the Trader and the Exchange, verifying that all orders move from "Pending" to "Filled" states without deadlocking.

## Execution
1. ```
    spin -a exchange.pml
    gcc -o pan pan.c
    ./pan
   ```
2. ```
   # Terminal 1
       g++ exchange_sim.cpp -o exchange_sim
       ./exchange_sim
   # Terminal 2
       python3 exchange.py
   # Terminal 3
       python3 pl_report.py
   ```
