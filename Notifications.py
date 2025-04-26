import streamlit as st
from utils.header import show_header
from utils.auth import check_login

st.set_page_config(page_title="🔔 Notifications - Shree Sai Industries", layout="wide")

show_header()
st.image("./assets/logo.png", width=200)

check_login()

allowed_roles = ["Admin"]
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.title("🔔 Notifications Setup")
st.info("📤 Daily dispatch email is scheduled at 9:30 AM.")















