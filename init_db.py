import sqlite3
import os

# Ensure 'data' folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Connect to database (will create it inside 'data' folder)
conn = sqlite3.connect("data/orders.db")
cursor = conn.cursor()

# Create orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    order_quantity INTEGER,
    order_date TEXT
);
""")

conn.commit()
conn.close()

print("✅ orders.db created with 'orders' table inside /data/")