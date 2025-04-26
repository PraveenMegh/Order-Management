import streamlit as st

# Dummy users for now (later connected to database)
users = {
    "sales1": {"password": "sales123", "role": "Sales"},
    "sales2": {"password": "sales123", "role": "Sales"},
    "dispatch1": {"password": "dispatch123", "role": "Dispatch"},
    "accounts1": {"password": "accounts123", "role": "Accounts"},
    "admin1": {"password": "admin123", "role": "Admin"},
}

def login(username, password):
    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None

def check_login():
    if "username" not in st.session_state:
        st.error("Please login first from the main page.")
        st.stop()
