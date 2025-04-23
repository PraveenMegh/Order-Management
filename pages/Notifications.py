# ✅ Template for pages/Notifications.py
import streamlit as st
from utils.header import show_header
from utils.auth import check_login

if "role" not in st.session_state:
    st.set_page_config(page_title="Access Denied", layout="wide")
    st.markdown("<h3>Please open this page from the main dashboard.</h3>", unsafe_allow_html=True)
    st.stop()

show_header()
check_login()

allowed_roles = ["Admin"]  # or include others if needed
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.markdown("### 🔔 Notifications Setup")
st.info("Email is already scheduled at 9:30 AM using Streamlit Cloud.")
