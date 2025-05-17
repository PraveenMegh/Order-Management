import sqlite3

# --- Connect to database ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Create Users Table if not exists ---
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')
conn.commit()

# --- Predefined users ---
users = [
    ('admin', 'admin123', 'Admin'),
    ('ajay.sharma', 'ajay123', 'Dispatch'),
    ('manish.srivastava', 'manish123', 'Sales'),
    ('vishal.sharma', 'vishal123', 'Sales')
]

# --- Insert users only if not exists (safe) ---
for username, password, role in users:
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        print(f"✅ User created: {username}")
    else:
        print(f"ℹ️ User already exists: {username}")

conn.commit()
conn.close()

print("✅ User setup completed successfully!")
