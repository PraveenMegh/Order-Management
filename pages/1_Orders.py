import streamlit as st
import sqlite3
from utils.header import show_header
from utils.auth import check_login
from datetime import datetime

# --- Page Access Control ---
check_login()
if st.session_state.get("role") not in ["Admin", "Sales"]:
    st.error("🚫 You do not have permission to access this page.")
    st.stop()

# --- Page Header ---
show_header()
st.header("📦 Place a New Order")

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Create Table if not exists ---
c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        customer_name TEXT,
        product_name TEXT,
        quantity INTEGER,
        unit TEXT,
        urgent BOOLEAN,
        status TEXT DEFAULT 'Pending',
        created_at TEXT,
        dispatched_quantity INTEGER,
        dispatched_at TEXT,
        price REAL,
        currency TEXT,
        unit_type TEXT,
        dispatched_by TEXT
    )
''')
conn.commit()

# --- Insert Order Function ---
def insert_order(username, customer_name, product_name, quantity, unit, urgent, price, currency, unit_type):
    c.execute('''
        INSERT INTO orders (username, customer_name, product_name, quantity, unit, urgent, created_at, price, currency, unit_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, customer_name, product_name, quantity, unit, urgent, datetime.now(), price, currency, unit_type))
    conn.commit()

# --- Fetch Orders Function ---
def fetch_orders(username):
    if st.session_state.role == "Admin":
        c.execute('SELECT * FROM orders')
    else:
        c.execute('SELECT * FROM orders WHERE username = ?', (username,))
    return c.fetchall()

# --- Place New Order Form ---
st.subheader("➕ New Order Entry")
with st.container():
    with st.form("order_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name")
            product_name = st.text_input("Product Name")
            quantity = st.number_input("Quantity", min_value=1)
            unit = st.selectbox("Unit", ["KG", "Grams", "Nos", "Units"])
        with col2:
            urgent = st.checkbox("Mark as Urgent")
            price = st.number_input("Price per unit", min_value=0.0)
            currency = st.selectbox("Currency", ["INR", "USD"])
            unit_type = st.selectbox("Unit Type", ["Per KG", "Per Gram", "Per Unit", "Per Nos"])

        submit = st.form_submit_button("Submit Order")
        if submit:
            insert_order(
                st.session_state.username,
                customer_name,
                product_name,
                quantity,
                unit,
                int(urgent),
                price,
                currency,
                unit_type
            )
            st.success("✅ Order placed successfully!")
            st.rerun()

st.divider()

# --- Show Orders Section ---
st.subheader("📜 Your Orders (Editable Before Dispatch)")
orders = fetch_orders(st.session_state.username)

if orders:
    for order in orders:
        id, username, customer_name, product_name, quantity, unit, urgent, status, created_at, dispatched_quantity, dispatched_at, price, currency, unit_type, dispatched_by = order

        with st.expander(f"Order #{id} - {product_name} ({quantity} {unit})"):
            col1, col2 = st.columns(2)
            with col1:
                new_customer = st.text_input("Customer Name", value=customer_name, key=f"cust_{id}")
                new_product = st.text_input("Product Name", value=product_name, key=f"prod_{id}")
                new_qty = st.number_input("Quantity", value=quantity, min_value=1, key=f"qty_{id}")
                new_unit = st.selectbox("Unit", ["KG", "Grams", "Nos", "Units"], index=["KG", "Grams", "Nos", "Units"].index(unit), key=f"unit_{id}")
            with col2:
                new_urgent = st.checkbox("Urgent", value=bool(urgent), key=f"urg_{id}")
                new_price = st.number_input("Price", value=price if price else 0.0, key=f"price_{id}")
                new_currency = st.selectbox("Currency", ["INR", "USD"], index=0 if currency == "INR" else 1, key=f"currency_{id}")
                new_unit_type = st.selectbox("Unit Type", ["Per KG", "Per Gram", "Per Unit", "Per Nos"], index=0, key=f"unit_type_{id}")

            if st.button("Update Order", key=f"update_{id}"):
                c.execute('''
                    UPDATE orders
                    SET customer_name = ?, product_name = ?, quantity = ?, unit = ?, urgent = ?, price = ?, currency = ?, unit_type = ?
                    WHERE id = ?
                ''', (new_customer, new_product, new_qty, new_unit, int(new_urgent), new_price, new_currency, new_unit_type, id))
                conn.commit()
                st.success(f"✅ Order #{id} updated successfully!")
                st.rerun()
else:
    st.info("ℹ️ No orders placed yet.")

st.divider()
if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

