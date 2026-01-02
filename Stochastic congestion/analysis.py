import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect('network_data.db')
df = pd.read_sql_query("SELECT * FROM traffic LIMIT 10000", conn)

plt.figure(figsize=(10, 5))
sns.histplot(df['inter_arrival'], kde=True, color='blue')
plt.title("Stochastic Validation: Inter-Arrival Time Distribution")
plt.xlabel("Time between packets (seconds)")
plt.savefig("stochastic_dist.png")

df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
df.set_index('timestamp', inplace=True)
throughput = df['size'].resample('1S').sum() # Sum of bytes per second

plt.figure(figsize=(12, 6))
throughput.plot()
plt.title("Time-Series: Network Throughput (Bytes/Second)")
plt.ylabel("Bytes")
plt.savefig("time_series_throughput.png")

print("Analysis complete. Charts saved as PNG files.")
