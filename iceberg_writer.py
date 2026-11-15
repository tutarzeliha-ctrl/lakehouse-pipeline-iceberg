import duckdb
import os
import json
import time
from datetime import datetime

CHECKPOINT_FILE = "state/checkpoint.json"
SILVER_PARQUET = "lakehouse/silver/orders.parquet"
QUARANTINE_PARQUET = "lakehouse/quarantine/bad_orders.parquet"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f).get("last_updated_at", "1970-01-01 00:00:00")
    return "1970-01-01 00:00:00"

def save_checkpoint(timestamp_str):
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({
            "last_updated_at": timestamp_str, 
            "updated_at_utc": datetime.utcnow().isoformat()
        }, f, indent=2)

def run_ingestion(simulate_crash_before_checkpoint=False):
    start_time = time.time()
    last_cp = load_checkpoint()
    
    os.makedirs("lakehouse/silver", exist_ok=True)
    os.makedirs("lakehouse/quarantine", exist_ok=True)

    con = duckdb.connect()
    con.sql("INSTALL postgres; LOAD postgres;")
    con.sql("""
        ATTACH 'dbname=source_db user=admin password=password123 host=localhost port=5432' 
        AS source_db (TYPE POSTGRES);
    """)

    # 1. Read new/updated records since the last checkpoint
    batch_df = con.sql(f"""
        SELECT * FROM source_db.orders 
        WHERE updated_at >= CAST('{last_cp}' AS TIMESTAMP)
        ORDER BY updated_at ASC
    """).fetchdf()

    read_count = len(batch_df)
    if read_count == 0:
        print(f"[METRICS] Read: 0 | Written: 0 | Quarantined: 0 | Duration: {time.time() - start_time:.2f}s (No new data)")
        con.close()
        return

    con.register("batch_view", batch_df)

    # 2. Data Quality Check: Separate valid and invalid (quarantine) records
    valid_df = con.sql("SELECT * FROM batch_view WHERE amount > 0 AND customer_name IS NOT NULL").fetchdf()
    bad_df = con.sql("SELECT * FROM batch_view WHERE amount <= 0 OR customer_name IS NULL").fetchdf()

    quarantined_count = len(bad_df)
    written_count = len(valid_df)

    # Write bad records to quarantine layer (idempotently)
    if quarantined_count > 0:
        con.register("bad_view", bad_df)
        if os.path.exists(QUARANTINE_PARQUET):
            con.sql(f"""
                COPY (
                    SELECT * FROM '{QUARANTINE_PARQUET}'
                    WHERE order_id NOT IN (SELECT order_id FROM bad_view)
                    UNION ALL
                    SELECT * FROM bad_view
                ) TO '{QUARANTINE_PARQUET}' (FORMAT PARQUET);
            """)
        else:
            con.sql(f"COPY bad_view TO '{QUARANTINE_PARQUET}' (FORMAT PARQUET);")

    # 3. Write valid records to Silver layer using Idempotent Upsert (Merge)
    if written_count > 0:
        con.register("valid_view", valid_df)
        if os.path.exists(SILVER_PARQUET):
            con.sql(f"""
                COPY (
                    SELECT * FROM (
                        SELECT * FROM '{SILVER_PARQUET}'
                        WHERE order_id NOT IN (SELECT order_id FROM valid_view)
                        UNION ALL
                        SELECT * FROM valid_view
                    ) WHERE is_deleted = FALSE
                ) TO '{SILVER_PARQUET}' (FORMAT PARQUET);
            """)
        else:
            con.sql(f"""
                COPY (SELECT * FROM valid_view WHERE is_deleted = FALSE) 
                TO '{SILVER_PARQUET}' (FORMAT PARQUET);
            """)

    # Simulate crash before checkpoint (for crash recovery testing)
    if simulate_crash_before_checkpoint:
        con.close()
        raise RuntimeError("SIMULATED CRASH: Target written, but checkpoint was NOT saved!")

    # 4. Update checkpoint
    max_ts = str(batch_df["updated_at"].max())
    save_checkpoint(max_ts)

    duration = time.time() - start_time
    print(f"[METRICS] Read: {read_count} | Valid Written/Updated: {written_count} | Quarantined: {quarantined_count} | Checkpoint: {max_ts} | Duration: {duration:.2f}s")
    con.close()

if __name__ == "__main__":
    run_ingestion()