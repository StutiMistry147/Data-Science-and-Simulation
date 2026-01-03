# Risk Analysis Engine
## Overview
- This project involves developing a formal prototype of a Monte Carlo Risk Engine designed as a Parallel Processing Pipeline.
- The system simulates over 100,000 "parallel universes" for a stock portfolio to calculate the Value at Risk (VaR), a critical financial metric used to determine maximum potential losses.
- The primary engineering challenge of this project was managing Concurrency Safety—ensuring that when thousands of simulations run in parallel, shared memory and result buffers remain protected from data corruption.
- 
## Tools
- C++ (Pthreads): Used for the high-performance, multi-threaded simulation engine to perform heavy stochastic computations.
- Python (Pandas, Matplotlib): Utilized for statistical data analysis, percentile calculations, and generating risk distribution histograms
- SQL (SQLite): Acts as the structured persistence layer for managing the high-volume output of simulation paths.

## Execution
1. High-Performance Simulation :
```
g++ -pthread monte_carlo.cpp -o monte_carlo
./monte_carlo
```
2. Import the simulation results into the SQL database for structured analysis :
```sqlite3 risk_data.db ".mode csv" ".import sim_outcomes.csv outcomes"```
3. Risk Reporting :
```python3 risk_plot.py```
