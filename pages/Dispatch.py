import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
if st.session_state.get("role") not in ["Admin", "Dispatch"]:
    st.error("⛔ You do not have permission to access this page.")
    st.stop()

# --- Connect to SQLite DB ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- UI Header ---
show_header()
st.header("🚚 Dispatch Orders")

# --- Pending Orders ---
pending = pd.read_sql_query("""
    SELECT 
        oi.id AS item_id,
        oi.order_id,
        o.customer_name,
        o.username AS salesperson,
        o.currency,
        o.urgent,
        o.created_at,
        oi.product_name,
        oi.ordered_qty,
        oi.unit,
        oi.price,
        oi.unit_type,
        oi.status
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Pending'
    ORDER BY o.created_at ASC
""", conn)

if pending.empty:
    st.success("✅ No pending products for dispatch.")
else:
    st.caption("⚡ FIFO Dispatch Mode: Oldest orders shown first.")
    grouped = pending.groupby('order_id')

    for order_id, df in grouped:
        with st.expander(f"Order #{order_id} - {df['customer_name'].iloc[0]}"):
            editable_df = df[['item_id', 'product_name', 'ordered_qty', 'unit']].copy()
            editable_df['dispatched_qty'] = editable_df['ordered_qty']

            editable_df = st.data_editor(editable_df, hide_index=True, use_container_width=True)

            if st.button(f"✅ Confirm Dispatch for Order #{order_id}", key=f"btn_{order_id}"):
                now = datetime.now().isoformat()
                dispatcher = st.session_state.username

                try:
                    for _, row in editable_df.iterrows():
                        c.execute("""
                            UPDATE order_items
                            SET dispatched_qty = ?, status = 'Dispatched', dispatched_at = ?, dispatched_by = ?
                            WHERE id = ?
                        """, (row['dispatched_qty'], now, dispatcher, row['item_id']))
                    conn.commit()
                    st.success(f"✅ Order #{order_id} dispatched successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to dispatch: {e}")

st.divider()

# --- Dispatched Orders ---
dispatched = pd.read_sql_query("""
    SELECT
        oi.id AS item_id,
        oi.order_id,
        o.customer_name,
        o.username AS salesperson,
        o.currency,
        o.urgent,
        o.created_at,
        oi.product_name,
        oi.ordered_qty,
        oi.dispatched_qty,
        oi.unit,
        oi.price,
        oi.unit_type,
        oi.status,
        oi.dispatched_at,
        oi.dispatched_by
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Dispatched'
    ORDER BY oi.dispatched_at DESC
""", conn)

if dispatched.empty:
    st.info("ℹ️ No dispatched orders yet.")
else:
    dispatched['created_at'] = pd.to_datetime(dispatched['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')
    dispatched['dispatched_at'] = pd.to_datetime(dispatched['dispatched_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')

    if st.session_state.role == "Dispatch":
        dispatched = dispatched[dispatched["dispatched_by"] == st.session_state.username]

    st.dataframe(dispatched, use_container_width=True)

st.divider()

# --- Logout ---
if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")
