import streamlit as st
import sqlite3
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
if st.session_state.get("role") not in ["Admin", "Dispatch"]:
    st.error("⛔ You do not have permission to access this page.")
    st.stop()

# --- Page Header ---
show_header()
st.header("🚚 Dispatch Orders")
st.markdown(" ")

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Fetch Pending Products ---
pending_products = pd.read_sql_query("""
    SELECT oi.id, oi.order_id, o.customer_name, o.username as salesperson,
           oi.product_name, oi.ordered_qty, oi.unit, oi.price, oi.unit_type,
           o.currency, o.urgent, o.created_at
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Pending'
    ORDER BY o.created_at ASC
""", conn)

# --- Fetch Dispatched Products ---
dispatched_products = pd.read_sql_query("""
    SELECT oi.id, oi.order_id, o.customer_name, o.username as salesperson,
           oi.product_name, oi.ordered_qty, oi.dispatched_qty, oi.unit,
           oi.price, oi.unit_type, o.currency, o.urgent,
           o.created_at, oi.dispatched_at, oi.dispatched_by
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Dispatched'
    ORDER BY oi.dispatched_at DESC
""", conn)

# --- Pending Orders Section ---
st.caption("⚡ Please dispatch orders in FIFO (First In, First Out) sequence. Oldest orders are shown first.")

if pending_products.empty:
    st.success("✅ No pending products for dispatch.")
else:
    st.subheader("📦 Pending Products for Dispatch")
    grouped = pending_products.groupby('order_id')

    for order_id, order_df in grouped:
        with st.expander(f"Order #{order_id} - {order_df['customer_name'].iloc[0]}"):
            st.markdown(f"**Customer**: {order_df['customer_name'].iloc[0]}")
            st.markdown(f"**Salesperson**: {order_df['salesperson'].iloc[0]}")
            st.markdown(f"**Currency**: {order_df['currency'].iloc[0]}")
            st.markdown(f"**Urgent**: {'🔥 Yes' if order_df['urgent'].iloc[0] else 'No'}")
            try:
                created_at = datetime.strptime(order_df['created_at'].iloc[0], '%Y-%m-%d %H:%M:%S.%f')
                st.markdown(f"**Created On**: {created_at.strftime('%d-%m-%Y %I:%M %p')}")
            except:
                st.markdown("**Created On**: Invalid timestamp")

            editable_df = order_df[['product_name', 'ordered_qty', 'unit']].copy()
            editable_df['dispatched_qty'] = editable_df['ordered_qty']

            editable_df = st.data_editor(
                editable_df,
                column_config={
                    "product_name": st.column_config.TextColumn(disabled=True),
                    "ordered_qty": st.column_config.NumberColumn(disabled=True),
                    "unit": st.column_config.TextColumn(disabled=True),
                    "dispatched_qty": st.column_config.NumberColumn(help="Edit dispatched qty if sending less than ordered")
                },
                use_container_width=True
            )

            if st.button(f"✅ Confirm Dispatch for Order #{order_id}"):
                now = datetime.now()
                for _, row in editable_df.iterrows():
                    c.execute("""
                        UPDATE order_items
                        SET dispatched_qty = ?, dispatched_at = ?, dispatched_by = ?, status = 'Dispatched'
                        WHERE order_id = ? AND product_name = ?
                    """, (row['dispatched_qty'], now, st.session_state.username, order_id, row['product_name']))
                conn.commit()
                st.success(f"✅ Order #{order_id} dispatched!")
                st.rerun()

st.divider()

# --- Dispatched Orders Section ---
st.subheader("✅ Dispatched Orders")

if dispatched_products.empty:
    st.info("ℹ️ No dispatched orders yet.")
else:
    df = dispatched_products.copy()
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')
    if 'dispatched_at' in df.columns:
        df['dispatched_at'] = pd.to_datetime(df['dispatched_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')

    # Dispatch users view only their dispatched entries
    if st.session_state.role == "Dispatch":
        df = df[df["dispatched_by"] == st.session_state.username]

    st.dataframe(df, use_container_width=True)

    if st.session_state.role == "Admin":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="Dispatched_Orders.csv",
            mime="text/csv"
        )
    elif st.session_state.role == "Dispatch":
        st.info("Download available only for Admin.")

st.divider()

if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")
