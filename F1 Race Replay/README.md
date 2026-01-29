# F1 Race Relay
## Overview
- F1 Race Relay is a Formula 1 race visualization and data analysis tool built with Python.
- It transforms raw F1 timing data into interactive visualizations, comprehensive dashboards, and detailed race analytics through an elegant, modern interface.

## Architechture
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐    │
│  │ Modern GUI  │  │ CLI Tools   │  │ Visualizations    │    │
│  │ (PySide6)   │  │ (CLI)       │  │ (Matplotlib/Seab.)│    │
│  └─────────────┘  └─────────────┘  └───────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                   APPLICATION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐    │
│  │ Data        │  │ Analysis    │  │ Visualization     │    │
│  │ Processor   │  │ Engine      │  │ Generator         │    │
│  └─────────────┘  └─────────────┘  └───────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                         DATA LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │                     FastF1 API                        │  │
│  │      (Official Formula 1 Timing Data)                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
