import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Load data
df = pd.read_csv('sim_outcomes.csv')

# Calculate Value at Risk (VaR)
var_95 = df['final_price'].quantile(0.05)
initial_investment = 100.0
potential_loss = initial_investment - var_95

print(f"95% Confidence Price Level: ${var_95:.2f}")
print(f"Value at Risk (VaR): ${potential_loss:.2f}")

# Plotting the "Parallel Universes"
plt.hist(df['final_price'], bins=100, color='skyblue', edgecolor='black')
plt.axvline(var_95, color='red', linestyle='dashed', linewidth=2, label=f'VaR (95%): ${var_95:.2f}')
plt.title("Monte Carlo Price Distribution")
plt.xlabel("Final Stock Price")
plt.ylabel("Frequency")
plt.legend()
plt.show()
