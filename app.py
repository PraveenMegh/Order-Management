import streamlit as st
from utils.auth import login

st.set_page_config(page_title="Order Management - Shree Sai Industries", layout="wide")

# Logo and Title
st.image("assets/logo.jpg", width=150)
st.title("Shree Sai Industries - Order Management System")

# If already logged in
if "username" in st.session_state:
    st.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
else:
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            role = login(username, password)
            if role:
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid username or password.")

# Routing based on role
if "role" in st.session_state:
    role = st.session_state.role

    if role == "Sales":
        st.page_link("pages/1_Orders.py", label="Go to Orders Page ➡️")
    elif role == "Dispatch":
        st.page_link("pages/2_Dispatch.py", label="Go to Dispatch Page ➡️")
    elif role == "Admin":
        st.page_link("pages/3_Admin.py", label="Go to Admin Page ➡️")
    elif role == "Accounts":
        st.page_link("pages/4_Reports.py", label="Go to Reports Page ➡️")
