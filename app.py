import streamlit as st
import sqlite3
from utils.header import show_header

# --- Page Settings ---
st.set_page_config(page_title="Shree Sai Industries - Login", page_icon="📦", layout="wide")

# --- Logo and Title ---
show_header()

# --- Mobile Responsive Styling ---
st.markdown("""
    <style>
    input, button, textarea {
        font-size: 18px !important;
    }
    .stButton button {
        padding: 10px 20px;
        border-radius: 10px;
    }
    .stTextInput>div>div>input {
        padding: 8px 10px;
        border-radius: 8px;
    }
    .stTextArea>div>textarea {
        padding: 8px 10px;
        border-radius: 8px;
    }
    div[data-testid="stForm"] {
        max-width: 400px;
        margin: auto;
    }
    h2 {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>🔒 Please Login</h2>", unsafe_allow_html=True)

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Create Users Table if Not Exists ---
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')
conn.commit()

# --- Login Function ---
def login_user(username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        db_username, db_password, db_role = result
        if password == db_password:
            return {"username": db_username, "role": db_role}
    return None

# --- Login Form ---
with st.form("login_form", clear_on_submit=False):
    st.markdown(" ")
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    login_button = st.form_submit_button("Login")

# --- Login Logic ---
if login_button:
    user = login_user(username, password)
    if user:
        st.session_state["username"] = user["username"]
        st.session_state["role"] = user["role"]
        st.success(f"✅ Welcome, {user['username']}! Redirecting...")
        st.switch_page("pages/1_Orders.py")
    else:
        st.error("❌ Invalid username or password. Please try again.")
