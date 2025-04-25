import streamlit as st
from utils.header import show_header
from utils.auth import check_login

# ✅ Page config set correctly
st.set_page_config(page_title="Admin Panel - Shree Sai Industries", layout="wide")

# ✅ Prevent direct access without session
if "role" not in st.session_state:
    st.markdown("<h3>Please open this page from the main dashboard.</h3>", unsafe_allow_html=True)
    st.stop()

# ✅ Authentication check
check_login()

# ✅ Header is correctly called
show_header()

# ✅ Role-based access control is correct
allowed_roles = ["Admin"]
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

# ✅ UI and placeholders correct for user management
st.title("🛠 Admin - User Management")
st.write("Add/edit/delete department users here. (To be implemented)")

# ✅ Button setup correctly with unique key
st.button("Add User", key="add_user_btn")
