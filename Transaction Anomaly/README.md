# Transaction Anomaly Detector
## Overview
Transaction Anomaly Detector is a data science and systems project that identifies suspicious financial transactions using rule-based detection with concurrency verification. The system implements multiple detection rules and uses Promela/Spin for formal verification of thread safety in concurrent transaction processing.

## Architecture
flowchart TD
    subgraph "Transaction Anomaly Detector"
        DL[Detection Layer<br/>• Rule Engine<br/>• Real-time<br/>• Batch]
        AL[Analysis Layer<br/>• Risk Scoring<br/>• Statistics<br/>• Reporting]
        VL[Verification<br/>• Promela<br/>• Spin<br/>• Concurrency]
    end
    
    TS[Transaction Simulator] --> DL
    DL --> AD[Analytics Dashboard]
    VL --> MC[Model Checker<br/>(Spin)]
    
    DL -.->|Processes| AL
    DL -.->|Verifies| VL
## Execution
1. ```
   python3 -m venv venv
   source venv/bin/activate
   ```
2. ```pip install pandas numpy matplotlib tabulate```
3. ```
   python run_detector.py
   ```
