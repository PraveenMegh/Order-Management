import streamlit as st
import sqlite3
import bcrypt
import os

# Connect to database
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'orders.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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