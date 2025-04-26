import streamlit as st
import sqlite3
import pandas as pd
from utils.header import show_header
from utils.auth import check_login
from datetime import datetime

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
    pending_orders['created_at'] = pd.to_datetime(pending_orders['created_at'])
    pending_orders['created_at_str'] = pending_orders['created_at'].dt.strftime('%d-%m-%Y %H:%M')

if not dispatched_orders.empty:
    dispatched_orders['created_at'] = pd.to_datetime(dispatched_orders['created_at']).dt.strftime('%d-%m-%Y %H:%M')
    dispatched_orders['dispatched_at'] = pd.to_datetime(dispatched_orders['dispatched_at']).dt.strftime('%d-%m-%Y %H:%M')

# --- Reports UI ---
st.title("📊 Orders Reports")

st.subheader("📦 Pending Orders")

if pending_orders.empty:
    st.success("✅ No pending orders!")
else:
    # Highlight urgent and pending > 10 days
    today = datetime.now()

    def highlight_rows(row):
        style = ''
        if row['urgent'] == 1:
            style = 'background-color: #FFCCCC'  # urgent
        if (today - row['created_at']).days > 10:
            style = 'background-color: #FFD580'  # pending >10 days
        return [style] * len(row)

    styled_pending = pending_orders.style.apply(highlight_rows, axis=1)

    st.dataframe(styled_pending, use_container_width=True)

st.divider()

st.subheader("✅ Dispatched Orders")

if dispatched_orders.empty:
    st.info("ℹ️ No dispatched orders yet.")
else:
    st.dataframe(dispatched_orders, use_container_width=True)

    if role == "Admin":
        csv = dispatched_orders.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Dispatched Orders (CSV)",
            data=csv,
            file_name='dispatched_orders.csv',
            mime='text/csv'
        )
