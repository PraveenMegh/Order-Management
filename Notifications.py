import streamlit as st
from utils.header import show_header
from utils.auth import check_login

st.set_page_config(page_title="🔔 Notifications - Shree Sai Industries", layout="wide")

# ✅ Display header and restrict access
show_header()
check_login()

# ✅ Optional: restrict to Admin role
if st.session_state.get("role") != "Admin":
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.title("🔔 Notifications Setup")
st.info("📤 Daily dispatch email is already scheduled at 9:30 AM using Streamlit Cloud.")
