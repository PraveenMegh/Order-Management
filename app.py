import streamlit as st
import sqlite3
from utils.auth import check_login, login_user
from utils.header import show_header

# --- Page Settings ---
st.set_page_config(page_title="Shree Sai Industries - Login", page_icon="📦", layout="wide")

# --- Logo and Title ---
show_header()
# --- Mobile Responsive Styling ---
st.markdown("""
    <style>
    /* Make input boxes and buttons bigger on mobile */
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
    /* Center the Login Form */
    div[data-testid="stForm"] {
        max-width: 400px;
        margin: auto;
    }
    /* Make headers centered */
    h2 {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>🔒 Please Login</h2>", unsafe_allow_html=True)

# --- DB Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Login Form ---
with st.form("login_form", clear_on_submit=False):
    st.markdown(" ")
    username = st.text_input("Username", placeholder="Enter your username", label_visibility="visible")
    password = st.text_input("Password", placeholder="Enter your password", type="password", label_visibility="visible")
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
