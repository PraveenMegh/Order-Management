import sqlite3
import os

DB_PATH = os.path.join('data', 'orders.db')
os.makedirs('data', exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# --- Create orders table ---
c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    username TEXT,
    created_at TEXT,
    urgent BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'Pending',
    price REAL DEFAULT 0,
    currency TEXT DEFAULT 'INR',
    unit_type TEXT DEFAULT 'Per Nos',
    dispatched_by TEXT,
    order_code TEXT
)
''')

# --- Create order_items table ---
c.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    ordered_qty INTEGER NOT NULL,
    dispatched_qty INTEGER DEFAULT 0,
    unit TEXT DEFAULT 'Nos',
    price REAL DEFAULT 0,
    unit_type TEXT DEFAULT 'Per Nos',
    status TEXT DEFAULT 'Pending',
    dispatched_at TEXT,
    dispatched_by TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
)
''')

# --- Create users table ---
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print(f"✅ Fresh database created at: {DB_PATH}")
