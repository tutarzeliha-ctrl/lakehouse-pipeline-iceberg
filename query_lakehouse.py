import duckdb

def query_local_lakehouse():
    con = duckdb.connect()
    
    print("Querying data directly from Local Lakehouse (Parquet layer)...")
    
    # Query the Parquet file as an analytical table using DuckDB
    query = """
        SELECT 
            customer_name,
            COUNT(order_id) as total_orders,
            SUM(amount) as total_spent,
            MAX(updated_at) as last_order_time
        FROM 'lakehouse/silver/orders_iceberg/orders.parquet'
        GROUP BY customer_name;
    """
    
    result = con.sql(query).fetchall()
    print("\n--- Lakehouse Analytics Report ---")
    print(con.sql(query))
    
    con.close()

if __name__ == "__main__":
    query_local_lakehouse()