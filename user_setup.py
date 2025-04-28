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

# --- Insert Users (One-time) ---
users = [
    ('admin', 'admin123', 'Admin'),
    ('ajay.sharma', 'ajay123', 'Dispatch'),
    ('manish.srivastava', 'manish123', 'Sales'),
    ('vishal.sharma', 'vishal123', 'Sales')
]

# --- Optional: Clear old users ---
c.execute('DELETE FROM users')

# --- Insert new users ---
for username, password, role in users:
    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))

conn.commit()
conn.close()

print("✅ Users created successfully!")
