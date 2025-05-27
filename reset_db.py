import sqlite3

conn = sqlite3.connect("orders.db")
c = conn.cursor()

# Drop old tables
c.execute("DROP TABLE IF EXISTS order_products")
c.execute("DROP TABLE IF EXISTS orders")

# Recreate orders table with correct structure
c.execute('''
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        address TEXT,
        gstin TEXT,
        order_no TEXT,
        order_date TEXT,
        urgent_flag INTEGER,
        created_by TEXT
    )
''')

# Recreate order_products table with correct structure
c.execute('''
    CREATE TABLE order_products (
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
''')

conn.commit()
conn.close()

print("✅ Database reset successfully.")
