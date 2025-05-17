import sqlite3
import bcrypt

# --- Connect to database ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Create Users Table if not exists ---
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,   # 👈 BLOB to store bytes hash
        role TEXT NOT NULL
    )
''')
conn.commit()

# --- Optional: Clear old users ---
c.execute('DELETE FROM users')

# --- Insert Users with hashed passwords ---
users = [
    ('admin', 'admin123', 'Admin'),
    ('ajay.sharma', 'ajay123', 'Dispatch'),
    ('manish.srivastava', 'manish123', 'Sales'),
    ('vishal.sharma', 'vishal123', 'Sales')
]

for username, plain_password, role in users:
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))

conn.commit()
conn.close()

print("✅ Users created with hashed passwords!")
