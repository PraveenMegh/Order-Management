import streamlit as st
import sqlite3
import bcrypt
utils.auth import check_login

# Connect to database
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

def login(username, password):
    c.execute('SELECT password, role FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    if result:
        hashed_password, role = result
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return role
    return None

def check_login():
    if "username" not in st.session_state:
        st.error("🚫 Please login first from the main page.")
        st.stop()
