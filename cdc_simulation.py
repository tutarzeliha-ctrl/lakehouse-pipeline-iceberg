import psycopg2
from datetime import datetime
import random

DB_CONFIG = {
    "dbname": "source_db",
    "user": "admin",
    "password": "password123",
    "host": "localhost",
    "port": "5432"
}

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Automatically drop existing table and its dependencies, then recreate with the latest schema
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

def simulate_events():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    customers = ["Zeliha Tutar", "Ahmet Yilmaz", "Elif Demir", "Can Kaya"]
    statuses = ["COMPLETED", "PENDING", "SHIPPED"]
    
    # 1. Insert a new valid order (INSERT)
    customer = random.choice(customers)
    amount = round(random.uniform(50.0, 1000.0), 2)
    status = random.choice(statuses)
    cur.execute("""
        INSERT INTO orders (customer_name, amount, status, is_deleted, updated_at)
        VALUES (%s, %s, %s, FALSE, %s);
    """, (customer, amount, status, datetime.now()))
    print(f"[CDC-INSERT] {customer} - {amount} USD ({status})")

    # 2. Occasionally generate bad data (for Data Quality / Quarantine test)
    if random.random() < 0.3:
        cur.execute("""
            INSERT INTO orders (customer_name, amount, status, is_deleted, updated_at)
            VALUES (%s, %s, %s, FALSE, %s);
        """, ("Invalid User", -50.00, "ERROR", datetime.now()))
        print("[CDC-BAD-DATA] Inserted invalid record (negative amount) for quarantine test.")

    # 3. Update an existing order (UPDATE)
    cur.execute("SELECT order_id FROM orders WHERE is_deleted = FALSE ORDER BY RANDOM() LIMIT 1;")
    row = cur.fetchone()
    if row:
        target_id = row[0]
        cur.execute("""
            UPDATE orders 
            SET status = 'DELIVERED', updated_at = %s 
            WHERE order_id = %s;
        """, (datetime.now(), target_id))
        print(f"[CDC-UPDATE] Order ID {target_id} updated to DELIVERED.")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
    simulate_events()