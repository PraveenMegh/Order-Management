import streamlit as st
import sqlite3
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
show_header()

# --- Restrict access to Admin only ---
if st.session_state.get("role") != "Admin":
    st.error("🚫 You do not have permission to access this page.")
    st.stop()

# --- Database Connection ---
st.write("Using database path:", os.path.abspath('data/orders.db'))
conn = sqlite3.connect('data/orders.db', check_same_thread=False)

# --- Fetch Pending Products ---
pending_products = pd.read_sql_query("""
    SELECT oi.order_id, o.customer_name, oi.product_name, oi.ordered_qty, oi.unit, oi.price, oi.unit_type,
           o.currency, o.urgent, o.created_at
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Pending'
""", conn)

# --- Fetch Dispatched Products ---
dispatched_products = pd.read_sql_query("""
    SELECT oi.order_id, o.customer_name, oi.product_name, oi.ordered_qty, oi.dispatched_qty, oi.unit,
           oi.price, oi.unit_type, o.currency, o.urgent, o.created_at, oi.dispatched_at, oi.dispatched_by
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Dispatched'
""", conn)

# --- Format Dates ---
if not pending_products.empty:
    pending_products['created_at'] = pd.to_datetime(pending_products['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')

if not dispatched_products.empty:
    dispatched_products['created_at'] = pd.to_datetime(dispatched_products['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')
    dispatched_products['dispatched_at'] = pd.to_datetime(dispatched_products['dispatched_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')
    dispatched_products['shortfall'] = dispatched_products['ordered_qty'] - dispatched_products['dispatched_qty']

# --- UI ---
st.title("📊 Order Reports")
st.markdown(" ")

# --- Pending Orders Section ---
st.subheader("📦 Pending Products")

if pending_products.empty:
    st.success("✅ No pending products!")
else:
    def highlight_urgent(val):
        return 'background-color: #FFD1D1' if val == 1 else ''

    st.dataframe(
        pending_products.style.applymap(highlight_urgent, subset=["urgent"]),
        use_container_width=True
    )

# --- Divider ---
st.divider()

# --- Dispatched Orders Section ---
st.subheader("✅ Dispatched Products")

if dispatched_products.empty:
    st.info("ℹ️ No dispatched products yet.")
else:
    st.dataframe(dispatched_products, use_container_width=True)

    csv = dispatched_products.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Dispatched Products (CSV)",
        data=csv,
        file_name="dispatched_products.csv",
        mime="text/csv"
    )
