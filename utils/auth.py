import streamlit as st

# Sample login credentials dictionary
USERS = {
    "sales": {"password": "sales123", "role": "Sales"},
    "dispatch": {"password": "dispatch123", "role": "Dispatch"},
    "admin": {"password": "admin123", "role": "Admin"},
    "accounts": {"password": "accounts123", "role": "Accounts"},
}

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("🔐 Login to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = USERS[username]["role"]
                st.success(f"Welcome, {username} ({st.session_state.role}) 👋")
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.stop()  # Stop app until login
    else:
        st.sidebar.markdown(f"👤 **{st.session_state.username}** ({st.session_state.role})")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.experimental_rerun()