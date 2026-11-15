import os
import sys
import shutil
import pytest
import duckdb
import psycopg2
from datetime import datetime

# Add root directory to python path to import modules from parent folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import ingestion functions
from iceberg_writer import run_ingestion, load_checkpoint

DB_CONFIG = {
    "dbname": "source_db",
    "user": "admin",
    "password": "password123",
    "host": "localhost",
    "port": "5432"
}

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Clean state before each test
    if os.path.exists("lakehouse"):
        shutil.rmtree("lakehouse")
    if os.path.exists("state"):
        shutil.rmtree("state")
    
    # Recreate source database table
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS orders CASCADE;")
    cur.execute("""
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            customer_name VARCHAR(100),
            amount DECIMAL(10, 2),
            status VARCHAR(50),
            is_deleted BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    yield
    # Cleanup after test
    if os.path.exists("lakehouse"):
        shutil.rmtree("lakehouse")
    if os.path.exists("state"):
        shutil.rmtree("state")

def test_incremental_and_idempotency():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (customer_name, amount, status, is_deleted, updated_at)
        VALUES ('Zeliha Tutar', 500.00, 'COMPLETED', FALSE, %s);
    """, (datetime.now(),))
    conn.commit()
    cur.close()
    conn.close()

    # 1. Run pipeline first time
    run_ingestion()
    
    # Check Silver layer count
    con = duckdb.connect()
    count_1 = con.sql("SELECT COUNT(*) FROM 'lakehouse/silver/orders.parquet'").fetchone()[0]
    con.close()
    assert count_1 == 1, "Should have exactly 1 record in Silver layer"

    # 2. Run pipeline second time (Idempotency check - running same batch again)
    run_ingestion()
    con = duckdb.connect()
    count_2 = con.sql("SELECT COUNT(*) FROM 'lakehouse/silver/orders.parquet'").fetchone()[0]
    con.close()
    
    assert count_2 == 1, "Idempotency violation: Duplicate rows found after re-running the same batch!"

def test_crash_recovery():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (customer_name, amount, status, is_deleted, updated_at)
        VALUES ('Crash Test User', 250.00, 'PENDING', FALSE, %s);
    """, (datetime.now(),))
    conn.commit()
    cur.close()
    conn.close()

    # Simulate crash before checkpoint is saved
    with pytest.raises(RuntimeError, match="SIMULATED CRASH"):
        run_ingestion(simulate_crash_before_checkpoint=True)

    # Checkpoint should still be at initial state because it crashed before saving
    assert load_checkpoint() == "1970-01-01 00:00:00", "Checkpoint should not advance on crash"

    # Recover by running pipeline normally
    run_ingestion()
    
    con = duckdb.connect()
    count = con.sql("SELECT COUNT(*) FROM 'lakehouse/silver/orders.parquet' WHERE customer_name = 'Crash Test User'").fetchone()[0]
    con.close()
    
    assert count == 1, "Data should be successfully recovered and written after restart"