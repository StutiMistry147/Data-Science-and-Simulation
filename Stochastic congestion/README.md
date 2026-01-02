# Stochastic Network Congestion Simulator
## Overview 
This project involves developing a formal prototype of a High-Performance Network Congestion Simulator using C++, SQL, Python, and the SPIN Model Checker. The system is designed as a Stochastic Data Pipeline, modeling real-world "bursty" network traffic where packet arrivals follow a Poisson distribution.
The primary challenge of this project was validating that a low-level, high-speed C++ engine correctly adheres to mathematical stochastic models while ensuring the system's buffer management logic is formally verified to prevent deadlocks during extreme traffic spikes.

## Specification 
The simulator operates across three stages of data maturity:
- <ins>Generation Stage</ins> : Produces high-volume synthetic traffic using an Exponential Distribution for inter-arrival times.
- <ins>Verification Stage</ins> : Uses Promela to prove that the "Drop Policy" and "Buffer Consumption" logic is safe and liveness-compliant.
- <ins>Analysis Stage</ins> : Performs Time-Series Analysis on millions of records to identify congestion patterns and throughput volatility.

## Architecture
- <ins>Traffic Engine (C++)</ins> : Acts as the data producer, using stochastic differential logic($t = -\frac{\ln(U)}{\lambda}$) to generate realistic packet timestamps.
- <ins>Formal Model (Promela)</ins> : Models the producer-consumer relationship between the network line and the router buffer to ensure no system hangs occur when the buffer is full.
- <ins>Storage Layer (SQL)</ins> : A structured repository that utilizes SQLite to manage "Big Data" volumes, allowing for rapid querying and indexing of traffic logs.
- <ins>Analytics Engine (Python)</ins> : The master observer, utilizing Pandas and Seaborn to perform statistical validation and plot network throughput over time

## Execution 
1. Run the SPIN model checker to ensure the buffer logic is deadlock-free
```
spin -a buffer.pml
gcc -o pan pan.c
./pan
```
2. <ins>Generate Traffic</ins> : Compile and run the C++ engine to produce raw CSV data
```g++ -O3 generator.cpp -o generator && ./generator```
3. <ins>Ingest Data</ins> : Use the automated bash script to populate the SQL database.
```chmod +x import_data.sh && ./import_data.sh```
4. <ins>Perform Analysis</ins> : Activate the virtual environment and generate Time-Series plots
```
source bigdata_env/bin/activate
python3 network_analysis.py
```
## Result
<img width="899" height="471" alt="image" src="https://github.com/user-attachments/assets/e67390ab-ec2f-48a1-8044-c911bc4ba904" />
<img width="764" height="474" alt="image" src="https://github.com/user-attachments/assets/545b23e9-a06a-4d95-96ff-2a6f399701e9" />
