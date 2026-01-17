# Transaction Anomaly Detector
## Overview
Transaction Anomaly Detector is a data science and systems project that identifies suspicious financial transactions using rule-based detection with concurrency verification. The system implements multiple detection rules and uses Promela/Spin for formal verification of thread safety in concurrent transaction processing.

## Architecture
<img width="1494" height="1497" alt="Transactionsim" src="https://github.com/user-attachments/assets/4d9205e6-f321-4b28-b3e8-54dc065c976a" />
## Execution
1. ```
   python3 -m venv venv
   source venv/bin/activate
   ```
2. ```pip install pandas numpy matplotlib tabulate```
3. ```
   python run_detector.py
   ```
