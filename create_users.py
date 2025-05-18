import sqlite3
import bcrypt

# Reset and recreate user table with full_name
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS users')
c.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL
    )
''')

# Define users: (username, password, role, full_name)
users = [
    # Admin
    ('admin', '1234', 'Admin', 'Praveen'),

    # Sales Team
    ('sales1', '1234', 'Sales', 'Manish'),
    ('sales2', '1234', 'Sales', 'Vishal'),
    ('sales3', '1234', 'Sales', 'Delhi Team'),
    ('sales4', '1234', 'Sales', 'Sumit'),
    ('sales5', '1234', 'Sales', 'Madhu'),

    # Dispatch Team
    ('dispatch1', '1234', 'Dispatch', 'Amit'),
    ('dispatch2', '1234', 'Dispatch', 'Ajay'),
    ('dispatch3', '1234', 'Dispatch', 'Rahul'),
    ('dispatch4', '1234', 'Dispatch', 'Pradeep'),
]

# Insert all users
for username, password, role, full_name in users:
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute(
        'INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)',
        (username, hashed_pw, role, full_name)
    )

conn.commit()
conn.close()

print("✅ All users created successfully with full names.")
