import streamlit as st
import sqlite3
from utils.header import show_header

# --- Streamlit Config ---
st.set_page_config(page_title="Shree Sai Industries - Login", page_icon="📦", layout="wide")

# --- Header (Logo & Title) ---
show_header()

# --- Mobile Responsive Styling ---
st.markdown("""
    <style>
    @media (max-width: 768px) {
        input, button, textarea { font-size: 18px !important; }
        .stButton button { padding: 10px 20px; border-radius: 10px; width: 100%; }
        .stTextInput>div>div>input { padding: 10px; border-radius: 8px; }
        .stTextArea>div>textarea { padding: 10px; border-radius: 8px; }
        div[data-testid="stForm"] { max-width: 400px; margin: auto; }
        h2 { text-align: center; font-size: 24px !important; }
    }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stDataFrameContainer { overflow-x: auto !important; }
        .block-container { padding: 0.5rem 1rem; }
        h1, h2, h3 { font-size: 20px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h2>🔒 Please Login</h2>", unsafe_allow_html=True)

# --- SQLite Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Create Users Table ---
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
    c.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    if result and password == result[1]:
        return {"username": result[0], "role": result[2]}
    return None

# --- Login Form ---
with st.form("login_form", clear_on_submit=False):
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
