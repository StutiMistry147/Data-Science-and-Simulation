# Risk Analysis Engine
## Overview
- This project involves developing a formal prototype of a Monte Carlo Risk Engine designed as a Parallel Processing Pipeline.
- The system simulates over 100,000 "parallel universes" for a stock portfolio to calculate the Value at Risk (VaR), a critical financial metric used to determine maximum potential losses.
- The primary engineering challenge of this project was managing Concurrency Safety—ensuring that when thousands of simulations run in parallel, shared memory and result buffers remain protected from data corruption.

## Tools
- <ins>C++ (Pthreads)</ins>: Used for the high-performance, multi-threaded simulation engine to perform heavy stochastic computations.
- <ins>Python (Pandas, Matplotlib)</ins>: Utilized for statistical data analysis, percentile calculations, and generating risk distribution histograms
- <ins>SQL (SQLite)</ins>: Acts as the structured persistence layer for managing the high-volume output of simulation paths.
- <ins>SPIN Model Checker (Promela)</ins>: Employed for formal verification of the thread-locking mechanisms to prove the system is deadlock-free.

## Execution
1. Formal Verification :
```
spin -a threads.pml
gcc -o pan pan.c
./pan
```
2. High-Performance Simulation :
```
g++ -pthread monte_carlo.cpp -o monte_carlo
./monte_carlo
```
3. Import the simulation results into the SQL database for structured analysis :
```
sqlite3 risk_data.db ".mode csv" ".import sim_outcomes.csv outcomes"
```
4. Risk Reporting :
```python3 risk_plot.py```

## Result
<img width="639" height="525" alt="image" src="https://github.com/user-attachments/assets/e969e136-83ef-4ac3-9dc4-bfb39e3ab36d" />
