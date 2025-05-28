import sqlite3

# Connect to orders.db (create if not exists)
conn = sqlite3.connect("orders.db")
c = conn.cursor()

# Drop existing tables (optional, only for clean reset)
c.execute("DROP TABLE IF EXISTS order_products")
c.execute("DROP TABLE IF EXISTS orders")

# Create orders table (with order_no!)
c.execute('''
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_by TEXT,
        customer_name TEXT,
        order_no TEXT,
        order_date TEXT,
        urgent_flag INTEGER,
        address TEXT,
        gstin TEXT
    )
''')

# Create order_products table
c.execute('''
    CREATE TABLE order_products (
        order_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

print("✅ orders.db created successfully with correct schema.")
