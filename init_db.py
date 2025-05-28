import sqlite3

conn = sqlite3.connect("orders.db")
c = conn.cursor()

# Create orders table
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_by TEXT,
    customer_name TEXT,
    address TEXT,
    gstin TEXT,
    order_date TEXT,
    urgent_flag INTEGER
)
""")

# Create order_products table
c.execute("""
CREATE TABLE IF NOT EXISTS order_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    unit TEXT,
    price_inr REAL,
    price_usd REAL,
    status TEXT,
    modified_by TEXT,
    modified_date TEXT,
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
)
""")

conn.commit()
conn.close()
print("✅ orders.db created successfully.")
