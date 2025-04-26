import streamlit as st
from header import show_header
from utils.auth import check_login

st.set_page_config(page_title="📄 Reports - Shree Sai Industries", layout="wide")

show_header()
st.image("./assets/logo.png", width=200)

check_login()

allowed_roles = ["Admin", "Accounts"]
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.title("📄 Reports Section")

st.info("Reports like dispatch summary, orders pending, high-demand products etc.")

























