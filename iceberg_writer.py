import duckdb
import os

def write_to_lakehouse_incremental():
    con = duckdb.connect()
    
    con.sql("INSTALL postgres;")
    con.sql("LOAD postgres;")
    con.sql("INSTALL iceberg;")
    con.sql("LOAD iceberg;")
    
    print("DuckDB extensions loaded successfully.")
    
    con.sql("""
        ATTACH 'dbname=source_db user=admin password=password123 host=localhost port=5432' 
        AS source_db (TYPE POSTGRES);
    """)
    
    os.makedirs("lakehouse/silver/orders_iceberg", exist_ok=True)
    parquet_path = "lakehouse/silver/orders_iceberg/orders.parquet"
    
    # Read from PostgreSQL using corrected fetchdf()
    source_df = con.sql("SELECT * FROM source_db.orders").fetchdf()
    
    if os.path.exists(parquet_path):
        # Incremental append: read existing parquet, combine with new records and overwrite parquet file
        con.sql(f"""
            CREATE TABLE existing_data AS SELECT * FROM '{parquet_path}';
            CREATE TABLE combined_data AS 
                SELECT * FROM existing_data
                UNION
                SELECT * FROM source_db.orders;
            COPY combined_data TO '{parquet_path}' (FORMAT PARQUET);
        """)
        print("Incremental update: New CDC records appended to Lakehouse Parquet layer.")
    else:
        # Initial write
        con.sql(f"""
            COPY source_db.orders TO '{parquet_path}' (FORMAT PARQUET);
        """)
        print("Initial write: Lakehouse Parquet layer initialized.")
        
    con.close()

if __name__ == "__main__":
    write_to_lakehouse_incremental()