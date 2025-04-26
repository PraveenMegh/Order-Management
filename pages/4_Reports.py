import streamlit as st
import sqlite3
import pandas as pd
from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
show_header()

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Get logged-in user's info ---
username = st.session_state.get("username")
role = st.session_state.get("role")

# --- Fetch Data ---
if role == "Admin" or role == "Dispatch":
    pending_orders = pd.read_sql_query("SELECT * FROM orders WHERE status = 'Pending'", conn)
    dispatched_orders = pd.read_sql_query("SELECT * FROM orders WHERE status = 'Dispatched'", conn)
else:
    pending_orders = pd.read_sql_query("SELECT * FROM orders WHERE status = 'Pending' AND username = ?", conn, params=(username,))
    dispatched_orders = pd.read_sql_query("SELECT * FROM orders WHERE status = 'Dispatched' AND username = ?", conn, params=(username,))

# --- Format Date Columns ---
if not pending_orders.empty:
    pending_orders['created_at'] = pd.to_datetime(pending_orders['created_at']).dt.strftime('%d-%m-%Y %H:%M')

if not dispatched_orders.empty:
    dispatched_orders['created_at'] = pd.to_datetime(dispatched_orders['created_at']).dt.strftime('%d-%m-%Y %H:%M')
    dispatched_orders['dispatched_at'] = pd.to_datetime(dispatched_orders['dispatched_at']).dt.strftime('%d-%m-%Y %H:%M')

# --- Reports UI ---
st.title("📊 Orders Reports")

st.subheader("📦 Pending Orders")

if pending_orders.empty:
    st.success("✅ No pending orders!")
else:
    # Highlight urgent orders
    def highlight_urgent(val):
        return 'background-color: #FFCCCC' if val == 1 else ''

    st.dataframe(pending_orders.style.applymap(highlight_urgent, subset=['urgent']), use_container_width=True)

st.divider()

st.subheader("✅ Dispatched Orders")

if dispatched_orders.empty:
    st.info("ℹ️ No dispatched orders yet.")
else:
    st.dataframe(dispatched_orders, use_container_width=True)

    # Admin can download
    if role == "Admin":
        csv = dispatched_orders.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Dispatched Orders (CSV)",
            data=csv,
            file_name='dispatched_orders.csv',
            mime='text/csv'
        )
