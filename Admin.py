import streamlit as st
from utils.header import show_header
from utils.auth import check_login

# ✅ Set config FIRST!
st.set_page_config(page_title="Admin Panel - Shree Sai Industries", layout="wide")

# ✅ Redirect if accessed directly without session
if "role" not in st.session_state:
    st.markdown("<h3>Please open this page from the main dashboard.</h3>", unsafe_allow_html=True)
    st.stop()

check_login()
show_header()

# ✅ Access control
allowed_roles = ["Admin"]
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.title("🛠 Admin - User Management")
st.write("Add/edit/delete department users here. (To be implemented)")

st.button("Add User", key="add_user_btn")
