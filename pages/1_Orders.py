import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
if st.session_state.get("role") not in ["Admin", "Sales"]:
    st.error("⛔ You do not have permission to access this page.")
    st.stop()

show_header()

st.write("Using database path:", os.path.abspath('data/orders.db'))

# --- Connect to DB ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Get current user ---
username = st.session_state.get("username")
role = st.session_state.get("role")

# --- FORM FOR NEW ORDER ---
with st.form("new_order_form"):
    st.subheader("📝 Create New Order")
    customer_name = st.text_input("Customer Name")
    urgent = st.checkbox("Mark as Urgent")
    currency = st.selectbox("Currency", ["INR", "USD", "EUR"])
    
    num_products = st.number_input("How many products?", min_value=1, max_value=10, value=1)
    
    product_inputs = []
    for i in range(num_products):
        st.markdown(f"### Product {i+1}")
        product_name = st.text_input(f"Product Name {i+1}", key=f"pname_{i}")
        ordered_qty = st.number_input(f"Quantity {i+1}", min_value=1, key=f"pqty_{i}")
        unit = st.selectbox(f"Unit {i+1}", ["KG", "Nos"], key=f"unit_{i}")
        price = st.number_input(f"Price {i+1}", min_value=0.0, key=f"price_{i}")
        unit_type = st.text_input(f"Unit Type {i+1}", key=f"utype_{i}")
        product_inputs.append((product_name, ordered_qty, unit, price, unit_type))
    
    submitted = st.form_submit_button("Create Order")

    if submitted:
        if customer_name and all(p[0] for p in product_inputs):
            c.execute("""
                INSERT INTO orders (customer_name, username, created_at, urgent, currency)
                VALUES (?, ?, datetime('now'), ?, ?)
            """, (customer_name, username, int(urgent), currency))
            conn.commit()
            order_id = c.lastrowid
            
            for p in product_inputs:
                c.execute("""
                    INSERT INTO order_items (order_id, product_name, ordered_qty, unit, price, unit_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Pending')
                """, (order_id, p[0], p[1], p[2], p[3], p[4]))
            conn.commit()
            
            st.success(f"✅ Order {order_id} created with {len(product_inputs)} products!")
            st.rerun()
        else:
            st.error("Please fill customer name and all product names.")

# --- Query user’s pending orders ---
orders_df = pd.read_sql_query("""
    SELECT 
        o.id AS order_id,
        o.order_code,
        o.customer_name,
        o.username AS salesperson,
        o.currency,
        o.urgent,
        o.created_at,
        oi.id AS item_id,
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

# --- Format dates ---
if not orders_df.empty:
    orders_df['created_at'] = pd.to_datetime(orders_df['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')
    orders_df['dispatched_at'] = pd.to_datetime(orders_df['dispatched_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')

    pending_items = orders_df[orders_df['status'] == 'Pending'].copy()

    if pending_items.empty:
        st.info("✅ No editable pending orders.")
    else:
        st.subheader("📋 Edit Pending Orders Before Dispatch")

        # Prepare editable dataframe with item_id as index
        editable_df = pending_items[['item_id', 'product_name', 'ordered_qty', 'price', 'unit']].set_index('item_id')

        # Show editor
        edited_df = st.data_editor(
            editable_df,
            column_config={
                'product_name': st.column_config.TextColumn(disabled=True),
                'ordered_qty': st.column_config.NumberColumn(min_value=1),
                'price': st.column_config.NumberColumn(min_value=0.0),
                'unit': st.column_config.SelectboxColumn(options=['KG', 'Nos'])
            },
            use_container_width=True,
            hide_index=True
        )

        # ✅ Reset index to bring back item_id as a column
        edited_df_reset = edited_df.reset_index()

        if st.button("💾 Save Changes"):
            for _, row in edited_df_reset.iterrows():
                item_id = row['item_id']
                updated_qty = row['ordered_qty']
                updated_price = row['price']
                updated_unit = row['unit']

                c.execute("""
                    UPDATE order_items
                    SET ordered_qty = ?, price = ?, unit = ?
                    WHERE id = ?
                """, (updated_qty, updated_price, updated_unit, item_id))
            conn.commit()
            st.success("✅ Changes saved!")
            st.rerun()
    else:
    st.info("ℹ️ You have no orders yet.")

# --- Orders Summary View ---
st.title("📜 Your Orders (Editable Before Dispatch)")
st.markdown(" ")

if orders_df.empty:
    st.info("ℹ️ You have no pending or dispatched orders.")
else:
    grouped = orders_df.groupby('order_id')

    for order_id, order_items in grouped:
        order_code = order_items['order_code'].iloc[0]
        customer_name = order_items['customer_name'].iloc[0]
        created_on = order_items['created_at'].iloc[0]
        urgent = '🔥 Yes' if order_items['urgent'].iloc[0] else 'No'
        currency = order_items['currency'].iloc[0]

        with st.expander(f"Order {order_code} - {customer_name}"):
            st.markdown(f"**Created On**: {created_on}")
            st.markdown(f"**Salesperson**: {order_items['salesperson'].iloc[0]}")
            st.markdown(f"**Currency**: {currency}")
            st.markdown(f"**Urgent**: {urgent}")

            for idx, row in order_items.iterrows():
                st.markdown(f"### Product: {row['product_name']}")
                st.markdown(f"- Ordered Qty: {row['ordered_qty']} {row['unit']}")
                st.markdown(f"- Unit Price: {row['price']} {currency}")
                st.markdown(f"- Unit Type: {row['unit_type']}")
                st.markdown(f"- Status: {row['status']}")
                if row['dispatched_qty']:
                    st.markdown(f"- Dispatched Qty: {row['dispatched_qty']}")
                    st.markdown(f"- Dispatched On: {row['dispatched_at']}")
                    st.markdown(f"- Dispatched By: {row['dispatched_by']}")
                else:
                    st.markdown("✅ Pending dispatch.")

st.divider()

if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")
