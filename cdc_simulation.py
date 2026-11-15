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

def create_table_if_not_exists():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            customer_name VARCHAR(100),
            amount DECIMAL(10, 2),
            status VARCHAR(50),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def simulate_cdc_insert():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    customers = ["Zeliha Tutar", "Ahmet Yilmaz", "Elif Demir", "Can Kaya"]
    statuses = ["COMPLETED", "PENDING", "SHIPPED"]
    
    customer = random.choice(customers)
    amount = round(random.uniform(50.0, 1000.0), 2)
    status = random.choice(statuses)
    
    cur.execute("""
        INSERT INTO orders (customer_name, amount, status, updated_at)
        VALUES (%s, %s, %s, %s);
    """, (customer, amount, status, datetime.now()))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"[{datetime.now()}] CDC Event: New order added for {customer} ({amount} USD - {status})")

if __name__ == "__main__":
    create_table_if_not_exists()
    simulate_cdc_insert()