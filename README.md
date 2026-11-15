# 🚀 Local Real-Time Lakehouse & CDC Pipeline

A lightweight, modern, and pragmatic Local Lakehouse architecture demonstrating Change Data Capture (CDC), modular Python engineering, and high-performance analytical querying using **DuckDB** and **Parquet/Iceberg-compliant storage**.

## 🏛️ Architecture & Tech Stack

```text
[ PostgreSQL (Source DB) ] 
       │ (CDC Simulation / New Events)
       ▼
[ Python Ingestion & Incremental Writer ] 
       │ (Transform & Append)
       ▼
[ Local Lakehouse Layer (Parquet / Iceberg Format) ] 
       │ (High-Performance SQL Compute)
       ▼
[ DuckDB Analytics Engine & Reports ]
Source Database: PostgreSQL 15 (Dockerized)

CDC & Ingestion: Python (psycopg2)

Lakehouse Format: Apache Iceberg concepts / Apache Parquet

Compute Engine: DuckDB

Orchestration: Python Orchestrator (run_pipeline.py)

🛠️ Project Structure
Plaintext
local-lakehouse-cdc/
│
├── docker-compose.yml       # PostgreSQL infrastructure
├── cdc_simulation.py        # Simulates operational database changes (CDC)
├── iceberg_writer.py        # Incremental loader into Lakehouse storage
├── query_lakehouse.py       # Analytical querying with DuckDB
├── run_pipeline.py          # End-to-end pipeline orchestrator
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
⚙️ Getting Started
1. Clone & Setup Environment
Bash
git clone [https://github.com/your-username/local-lakehouse-cdc.git](https://github.com/your-username/local-lakehouse-cdc.git)
cd local-lakehouse-cdc
pip install -r requirements.txt
2. Start Source Infrastructure
Bash
docker compose up -d
3. Run the End-to-End Pipeline
Bash
python run_pipeline.py
💡 Key Highlights
Pragmatic Lakehouse Design: Avoids heavy cloud costs by leveraging DuckDB and local columnar storage.

Incremental Processing: Handles delta updates efficiently rather than full table rewrites.

Senior-Level Engineering: Modular, containerized, and clean codebase suitable for modern Data Engineering standards.