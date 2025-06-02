import os
import sqlite3
import bcrypt

# Ensure 'data' directory exists
os.makedirs("data", exist_ok=True)

# Connect to the SQLite database inside 'data' folder
conn = sqlite3.connect("data/users.db")
c = conn.cursor()

# Drop and recreate users table
c.execute("DROP TABLE IF EXISTS users")
c.execute("""
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash BLOB NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL
    )
""")

# Define your users: (username, password, role, full_name)
users = [
    ("admin", "Securepas!83107", "Admin", "Praveen Chaudhary"),
    ("manish.srivastava", "321manish", "Sales", "Manish Srivastava"),
    ("vishal.sharma", "vishal245", "Sales", "Vishal Sharma"),
    ("madhu.sharma", "madhu798", "Sales", "Madhu Sharma"),
    ("vipin.dabas", "vipin123", "Sales", "Vipin Dabas"),
    ("delhi.team", "delhi@sales123", "Sales", "Deepak Aggarwal"),
    ("ahay.sharma", "ajay1976", "Dispatch", "Ajay Sharma"),
    ("amit.jawla", "amit0525", "Dispatch", "Amit Jawla"),
]

# Insert users with hashed passwords
for username, password, role, full_name in users:
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute(
        "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
        (username, hashed_pw, role, full_name)
    )

conn.commit()
conn.close()

print("✅ All users have been inserted successfully.")
