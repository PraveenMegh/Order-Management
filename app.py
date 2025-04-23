import streamlit as st
from utils.header import show_header
from utils.auth import check_login

st.set_page_config(page_title='Shree Sai Industries - Order Management', layout='wide')  # ✅ This must be first

# ✅ Clean UI styling for all devices
st.markdown("""
    <style>
        .stButton > button {
            font-size: 18px;
            padding: 12px 24px;
        }
        .stSelectbox > div {
            font-size: 18px !important;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Show logo and name
show_header()

# ✅ Role-based login
check_login()

# ✅ Display logged-in user's role
role = st.session_state.get("role", "")
st.markdown(f"### Welcome, **{role}** Team 👋")

# ✅ Role-based navigation
if role == "Sales":
    page = st.selectbox("📁 Navigate to", ["📦 Orders"])
elif role == "Dispatch":
    page = st.selectbox("📁 Navigate to", ["🚚 Dispatch"])
elif role == "Accounts":
    page = st.selectbox("📁 Navigate to", ["📊 Reports", "📊 Demand"])
elif role == "Admin":
    page = st.selectbox("📁 Navigate to", ["📦 Orders", "🚚 Dispatch", "📊 Reports", "📊 Demand", "🧑‍💼 Admin"])
else:
    page = None

# ✅ Dynamic routing
if page == "📦 Orders":
    st.switch_page("pages/Orders.py")
elif page == "🚚 Dispatch":
    st.switch_page("pages/Dispatch.py")
elif page == "📊 Reports":
    st.switch_page("pages/Reports.py")
elif page == "📊 Demand":
    st.switch_page("pages/Demand.py")
elif page == "🧑‍💼 Admin":
    st.switch_page("pages/Admin.py")
