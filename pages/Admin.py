import streamlit as st
import sqlite3
from utils.header import show_header
from utils.auth import check_login

# --- Authentication and Access Control ---
check_login()
if st.session_state.get("role") != "Admin":
    st.error("⛔ You do not have permission to access this page.")
    st.stop()

# --- Page Header ---
show_header()
st.subheader("Shree Sai Industries - Admin Panel")  # 👈 optional, keep if needed (but without logo)

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Create Users Table if not exists ---
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')
conn.commit()

# --- Fetch Users Function ---
def fetch_users():
    return c.execute('SELECT id, username, role FROM users').fetchall()

# --- Functions for Users ---
def add_user(username, password, role):
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def update_user(user_id, password, role):
    c.execute('UPDATE users SET password = ?, role = ? WHERE id = ?', (password, role, user_id))
    conn.commit()

def delete_user(user_id):
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()

# --- UI Layout ---
st.subheader("👥 Existing Users")
users = fetch_users()

if users:
    for user in users:
        id, username, role = user
        with st.expander(f"🔹 {username} ({role})"):
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input("New Password", key=f"pass_{id}")
            with col2:
                new_role = st.selectbox("Role", ["Sales", "Dispatch", "Accounts", "Admin"], index=["Sales", "Dispatch", "Accounts", "Admin"].index(role), key=f"role_{id}")

            col3, col4 = st.columns(2)
            with col3:
                if st.button("✏️ Update User", key=f"update_{id}"):
                    if new_password:
                        update_user(id, new_password, new_role)
                        st.success(f"✅ Updated user {username} successfully!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Please enter a new password.")
            with col4:
                if st.button("🗑️ Delete User", key=f"delete_{id}"):
                    delete_user(id)
                    st.success(f"✅ Deleted user {username} successfully!")
                    st.rerun()
else:
    st.info("ℹ️ No users found.")

st.divider()

# --- Add New User Section ---
st.subheader("➕ Add New User")

with st.form("add_user_form"):
    new_username = st.text_input("Username").lower()
    new_password = st.text_input("Password")
    new_role = st.selectbox("Role", ["Sales", "Dispatch", "Accounts", "Admin"])
    submit_new_user = st.form_submit_button("✅ Add User")

    if submit_new_user:
        if new_username and new_password:
            success = add_user(new_username, new_password, new_role)
            if success:
                st.success(f"✅ User '{new_username}' added successfully!")
                st.rerun()
            else:
                st.error("🚫 Username already exists. Please choose another.")
        else:
            st.warning("⚠️ Please fill all fields.")

# --- Mobile-friendly Logout Button ---
st.divider()
if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")
