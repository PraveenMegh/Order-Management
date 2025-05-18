import sqlite3
import bcrypt

# Connect to your existing users.db
conn = sqlite3.connect('users.db')
c = conn.cursor()

username = 'dispatch2'
password = '1234'
role = 'Dispatch'

# Check if exists
c.execute('SELECT * FROM users WHERE username = ?', (username,))
if c.fetchone():
    print(f"User {username} already exists.")
else:
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', (username, hashed_pw, role))
    conn.commit()
    print(f"User {username} added successfully.")

conn.close()
