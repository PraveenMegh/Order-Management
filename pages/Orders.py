import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
if st.session_state.get("role") not in ["Admin", "Sales"]:
    st.error("⛔ You do not have permission to access this page.")
    st.stop()

# --- UI Header ---
show_header()
st.title("📜 Your Orders")

# --- DB Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Get current user ---
username = st.session_state.get("username")

# --- Order Creation Form ---
with st.form("new_order_form"):
    st.subheader("📝 Create New Order")
    customer_name = st.text_input("Customer Name")
    urgent = st.checkbox("Mark as Urgent")
    currency = st.selectbox("Currency", ["INR", "USD", "EUR"])

    num_products = st.number_input("How many products?", min_value=1, max_value=10, value=1)
    products = []

    for i in range(num_products):
        st.markdown(f"### Product {i+1}")
        pname = st.text_input(f"Product Name {i+1}", key=f"pname_{i}")
        qty = st.number_input(f"Quantity {i+1}", min_value=1, key=f"qty_{i}")
        unit = st.selectbox(f"Unit {i+1}", ["KG", "Nos"], key=f"unit_{i}")
        price = st.number_input(f"Price {i+1}", min_value=0.0, key=f"price_{i}")
        utype = st.text_input(f"Unit Type {i+1}", key=f"utype_{i}")
        products.append((pname, qty, unit, price, utype))

    submitted = st.form_submit_button("✅ Create Order")

    if submitted:
        if customer_name and all(p[0] for p in products):
            c.execute("""
                INSERT INTO orders (customer_name, username, created_at, urgent, currency)
                VALUES (?, ?, datetime('now'), ?, ?)
            """, (customer_name, username, int(urgent), currency))
            order_id = c.lastrowid

            for p in products:
                c.execute("""
                    INSERT INTO order_items (order_id, product_name, ordered_qty, unit, price, unit_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Pending')
                """, (order_id, p[0], p[1], p[2], p[3], p[4]))
            conn.commit()

            st.success(f"✅ Order #{order_id} created with {len(products)} products.")
            st.rerun()
        else:
            st.error("⚠️ Please fill customer name and all product names.")

st.divider()

# --- View Orders ---
orders_df = pd.read_sql_query("""
    SELECT 
        o.id AS order_id,
        o.customer_name,
        o.currency,
        o.urgent,
        o.created_at,
        oi.product_name,
        oi.ordered_qty,
        oi.unit,
        oi.price,
        oi.unit_type,
        oi.status,
        oi.dispatched_qty,
        oi.dispatched_at,
        oi.dispatched_by
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE o.username = ?
    ORDER BY o.created_at ASC
""", conn, params=(username,))

# Format dates
if not orders_df.empty:
    orders_df['created_at'] = pd.to_datetime(orders_df['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')
    orders_df['dispatched_at'] = pd.to_datetime(orders_df['dispatched_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')

if orders_df.empty:
    st.info("ℹ️ You have no orders yet.")
else:
    grouped = orders_df.groupby('order_id')
    for order_id, df in grouped:
        with st.expander(f"Order #{order_id} - {df['customer_name'].iloc[0]}"):
            st.write(f"Created On: {df['created_at'].iloc[0]}")
            st.write(f"Currency: {df['currency'].iloc[0]}")
            st.write(f"Urgent: {'🔥 Yes' if df['urgent'].iloc[0] else 'No'}")
            for _, row in df.iterrows():
                st.write(f"### Product: {row['product_name']}")
                st.write(f"- Ordered Qty: {row['ordered_qty']} {row['unit']}")
                st.write(f"- Unit Price: {row['price']} {df['currency'].iloc[0]}")
                st.write(f"- Unit Type: {row['unit_type']}")
                st.write(f"- Status: {row['status']}")
                if row['dispatched_qty']:
                    st.write(f"- Dispatched Qty: {row['dispatched_qty']}")
                    st.write(f"- Dispatched On: {row['dispatched_at']}")
                    st.write(f"- Dispatched By: {row['dispatched_by']}")
                else:
                    st.write("✅ Pending dispatch.")

st.divider()

# --- Logout ---
if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")
