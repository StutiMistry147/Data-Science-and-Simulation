import sqlite3

def calculate_performance():
    conn = sqlite3.connect('hft_results.db')
    cursor = conn.cursor()

    cursor.execute("SELECT action, COUNT(*), AVG(price), SUM(price) FROM portfolio GROUP BY action")
    rows = cursor.fetchall()

    if not rows:
        print("No trades found yet.")
        return

    total_pnl = 0
    print("\n--- Trading Performance Summary ---")
    for row in rows:
        action, count, avg_p, total_sum = row
        print(f"{action}: {count} trades | Avg Price: ${avg_p:.4f}")
        
        if action == 'BUY':
            total_pnl -= total_sum
        else:
            total_pnl += total_sum

    print("-----------------------------------")
    print(f"Net Realized P&L: ${total_pnl:.2f}")
    print("-----------------------------------\n")

if __name__ == "__main__":
    calculate_performance()
