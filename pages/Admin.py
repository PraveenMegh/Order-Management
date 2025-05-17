import streamlit as st
import sqlite3
import bcrypt
from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
if st.session_state.get("role") != "Admin":
    st.error("⛔ Access Denied.")
    st.stop()

# --- UI Header ---
show_header()
st.header("👥 Admin User Management")

# --- Connect to DB ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Ensure Users Table ---
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')
conn.commit()

# --- User Functions ---
def fetch_users():
    return c.execute('SELECT id, username, role FROM users').fetchall()

def add_user(username, password, role):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_pw, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def update_user(user_id, password, role):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute('UPDATE users SET password = ?, role = ? WHERE id = ?', (hashed_pw, role, user_id))
    conn.commit()

def delete_user(user_id):
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()

# --- Existing Users Section ---
st.subheader("📋 Existing Users")
users = fetch_users()

if users:
    for uid, uname, role in users:
        with st.expander(f"🔹 {uname} ({role})"):
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input("New Password", key=f"pass_{uid}")
            with col2:
                new_role = st.selectbox("Role", ["Sales", "Dispatch", "Admin"], index=["Sales", "Dispatch", "Admin"].index(role), key=f"role_{uid}")

            if st.button("✏️ Update User", key=f"update_{uid}"):
                if new_password:
                    update_user(uid, new_password, new_role)
                    st.success(f"✅ Updated user {uname}")
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a new password.")

            if st.button("🗑️ Delete User", key=f"delete_{uid}"):
                delete_user(uid)
                st.success(f"✅ Deleted user {uname}")
                st.rerun()
else:
    st.info("ℹ️ No users found.")

st.divider()

# --- Add User Section ---
st.subheader("➕ Add New User")

with st.form("add_user_form"):
    new_username = st.text_input("Username").lower()
    new_password = st.text_input("Password", type="password")
    new_role = st.selectbox("Role", ["Sales", "Dispatch", "Admin"])
    if st.form_submit_button("✅ Add User"):
        if new_username and new_password:
            if add_user(new_username, new_password, new_role):
                st.success(f"✅ User '{new_username}' added!")
                st.rerun()
            else:
                st.error("🚫 Username already exists.")
        else:
            st.warning("⚠️ Please fill all fields.")

st.divider()

# --- Logout ---
if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")
