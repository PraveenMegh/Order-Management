import sqlite3

conn = sqlite3.connect('orders.db')
c = conn.cursor()

# Orders table
c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_by TEXT,
        customer_name TEXT,
        order_no TEXT,
        order_date TEXT,
        urgent_flag INTEGER
    )
''')

# Order products table
c.execute('''
    CREATE TABLE IF NOT EXISTS order_products (
        order_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_name TEXT,
        quantity INTEGER,
        unit TEXT,
        price_inr REAL,
        price_usd REAL,
        status TEXT,
        modified_by TEXT,
        modified_date TEXT
    )
''')

conn.commit()
conn.close()

print("orders.db with required tables created.")
