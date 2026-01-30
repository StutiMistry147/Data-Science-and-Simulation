# Transaction Anomaly Detector
## Overview
Transaction Anomaly Detector is a data science and systems project that identifies suspicious financial transactions using rule-based detection with concurrency verification. The system implements multiple detection rules and uses Promela/Spin for formal verification of thread safety in concurrent transaction processing.

## Execution
```
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy matplotlib tabulate
python run_detector.py
```
