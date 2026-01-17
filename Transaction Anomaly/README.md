# Transaction Anomaly Detector
## Overview
Transaction Anomaly Detector is a data science and systems project that identifies suspicious financial transactions using rule-based detection with concurrency verification. The system implements multiple detection rules and uses Promela/Spin for formal verification of thread safety in concurrent transaction processing.

## Architecture
┌──────────────────────────────────────────────────────────┐
│              Transaction Anomaly Detector                │
├──────────────────────────────────────────────────────────┤
│  Detection Layer   │   Analysis Layer   │  Verification  │
│  • Rule Engine     │   • Risk Scoring   │  • Promela     │
│  • Real-time       │   • Statistics     │  • Spin        │
│  • Batch           │   • Reporting      │  • Concurrency │
└──────────────────────────────────────────────────────────┘
         │                     │                    │
         ▼                     ▼                    ▼
┌──────────────┐      ┌──────────────┐     ┌────────────────┐
│  Transaction │      │  Analytics   │     │  Model Checker │
│  Simulator   │      │  Dashboard   │     │  (Spin)        │
└──────────────┘      └──────────────┘     └────────────────┘

## Execution
1. ```
   python3 -m venv venv
   source venv/bin/activate
   ```
2. ```pip install pandas numpy matplotlib tabulate```
3. ```
   python run_detector.py
   ```
