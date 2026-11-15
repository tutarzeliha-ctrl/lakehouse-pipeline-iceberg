import duckdb
import os

SILVER_PARQUET = "lakehouse/silver/orders.parquet"
QUARANTINE_PARQUET = "lakehouse/quarantine/bad_orders.parquet"

def query_analytics():
    con = duckdb.connect()

    print("\n--- Lakehouse Silver Analytics Report ---")
    if os.path.exists(SILVER_PARQUET):
        con.sql(f"""
            SELECT 
                customer_name,
                COUNT(order_id) AS total_orders,
                SUM(amount) AS total_spent,
                MAX(updated_at) AS last_order_time
            FROM '{SILVER_PARQUET}'
            GROUP BY customer_name
            ORDER BY total_spent DESC;
        """).show()
    else:
        print("No valid Silver data found yet.")

    if os.path.exists(QUARANTINE_PARQUET):
        q_count = con.sql(f"SELECT COUNT(*) FROM '{QUARANTINE_PARQUET}'").fetchone()[0]
        print(f"[DATA QUALITY] Total quarantined invalid records: {q_count}")

    con.close()

if __name__ == "__main__":
    query_analytics()