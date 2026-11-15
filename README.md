# Local Real-Time Lakehouse & CDC Pipeline

A lightweight, robust, and production-grade local Lakehouse architecture demonstrating Change Data Capture (CDC) simulation, incremental ingestion, idempotent upserts, data quality quarantine handling, and automated crash recovery testing using Python, PostgreSQL, DuckDB, and Parquet.

## 🏗️ Architecture & Tech Stack

```text
[ PostgreSQL (Source DB) ]
       │ (CDC Simulation: INSERT, UPDATE, DELETE & Bad Data)
       ▼
[ Python Ingestion & Checkpointing Module (`iceberg_writer.py`) ]
       │ (Data Quality Filtering & Idempotent Upsert)
       ├─────────────────────────┬─────────────────────────┐
       ▼                         ▼                         ▼
[ Silver Layer ]         [ Quarantine Layer ]      [ State Checkpoint ]
 (`orders.parquet`)       (`bad_orders.parquet`)     (`checkpoint.json`)
       │
       ▼
[ DuckDB Analytics Engine & Reports (`query_lakehouse.py`) ]
Source Database: PostgreSQL 15 (Dockerized)

Ingestion & Orchestration: Python (psycopg2, duckdb)

Storage Format: Local Apache Parquet (Columnar Storage)

Testing: Pytest (tests/test_pipeline.py)

🚀 Key Engineering Features
Idempotency (Deduplication / Upsert): Re-running the same batch multiple times does not produce duplicate records in the Silver layer. It uses primary-key based deduplication logic via DuckDB.

Incremental Loading & Checkpointing: Tracks processing state using a persistent checkpoint.json file, ensuring the pipeline picks up precisely where it left off.

Crash Recovery & Fault Tolerance: Validated via automated tests. If the pipeline crashes after writing data but before saving the checkpoint, state consistency is maintained and recovered safely upon restart.

Data Quality & Quarantine Layer: Filters out invalid records (e.g., negative amounts or missing customer names) and safely isolates them in a dedicated Quarantine Parquet layer instead of dropping them silently.

CDC Simulation: Simulates operational database changes including INSERT, UPDATE, and DELETE events.

📁 Project Structure
Plaintext
local-lakehouse-cdc/
│
├── cdc_simulation.py      # Simulates operational database changes & bad data injection
├── iceberg_writer.py      # Core incremental ingestion, upsert, checkpoint & quarantine logic
├── query_lakehouse.py     # Analytical reporting script using DuckDB
├── run_pipeline.py        # End-to-end pipeline orchestrator
├── docker-compose.yml     # PostgreSQL infrastructure setup
├── requirements.txt       # Python dependencies
├── state/
│   └── checkpoint.json    # Incremental state tracking
├── lakehouse/
│   ├── silver/            # Clean, validated Parquet storage
│   └── quarantine/        # Isolated invalid records storage
└── tests/
    └── test_pipeline.py   # Automated pytest suite (Idempotency & Crash Recovery)
🛠️ Getting Started
1. Clone & Setup Environment
Bash
git clone [https://github.com/tutarzeliha-ctrl/lakehouse-pipeline-iceberg.git](https://github.com/tutarzeliha-ctrl/lakehouse-pipeline-iceberg.git)
cd lakehouse-pipeline-iceberg
pip install -r requirements.txt
2. Start Source Infrastructure
Bash
docker compose up -d
3. Run the End-to-End Pipeline
Bash
python run_pipeline.py
4. Run Automated Test Suite
To execute idempotency and crash recovery tests:

Bash
pytest -v
📊 Sample Execution & Metrics
Every pipeline execution outputs clear operational metrics:

Plaintext
[METRICS] Read: 1 | Valid Written/Updated: 1 | Quarantined: 0 | Checkpoint: 2026-11-15 23:09:20.749046 | Duration: 24.24s