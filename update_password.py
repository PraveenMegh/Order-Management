import sqlite3
import bcrypt

# ✅ UPDATE THIS SECTION
username_to_update = "admin"  # Enter the username to update
new_password = "yourNewSecurePassword123"  # Enter the new password

# 🔗 Connect to your DB
conn = sqlite3.connect("data/users.db")
c = conn.cursor()

# 🔐 Hash the new password
hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

# 🔄 Update the user password in DB
c.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_pw, username_to_update))
conn.commit()
conn.close()

print(f"✅ Password for '{username_to_update}' has been updated successfully.")
