import streamlit as st
import sqlite3
from utils.header import show_header
from utils.auth import check_login
from datetime import datetime

# --- Auth and Header ---
check_login()
show_header()

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Create Table if Not Exists ---
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
    dispatched_at TEXT
)
''')
conn.commit()

# --- Functions ---
def insert_order(username, customer_name, product_name, quantity, unit, urgent):
    c.execute('''
        INSERT INTO orders (username, customer_name, product_name, quantity, unit, urgent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, customer_name, product_name, quantity, unit, urgent, datetime.now()))
    conn.commit()

def fetch_orders(username):
    c.execute('SELECT * FROM orders WHERE username = ?', (username,))
    return c.fetchall()

# --- UI Start ---

st.header("📦 Place a New Order")
st.markdown(" ")

# --- Order Form ---
with st.form("order_form"):
    customer_name = st.text_input("Customer Name")

    product_list = [""] + [row[0] for row in c.execute('SELECT DISTINCT product_name FROM orders').fetchall()]
    product_name = st.selectbox("Product Name", options=product_list)
    if product_name == "":
        product_name = st.text_input("New Product Name")

    col1, col2 = st.columns([2, 1])

    with col1:
        quantity = st.number_input("Quantity", min_value=1)

    with col2:
        unit = st.selectbox("Unit", ["kg", "grams", "units"])

    urgent = st.checkbox("Mark as Urgent")

    submit = st.form_submit_button("Submit Order")

    if submit:
        insert_order(
            st.session_state.username,
            customer_name,
            product_name,
            quantity,
            unit,
            int(urgent)
        )
        st.success("Order placed successfully!")
        st.rerun()

# --- Display Orders Section ---

st.header("📝 Your Orders (Editable Before Dispatch)")
st.markdown(" ")

orders = fetch_orders(st.session_state.username)

if orders:
    for order in orders:
        id, username, customer_name, product_name, quantity, unit, urgent, status, created_at, dispatched_quantity, dispatched_at = order

        with st.expander(f"Order #{id} - {product_name}"):
            new_customer = st.text_input("Customer Name", value=customer_name, key=f"cust_{id}")
            new_product = st.text_input("Product Name", value=product_name, key=f"prod_{id}")
            new_qty = st.number_input("Quantity", value=quantity, min_value=1, key=f"qty_{id}")
            new_unit = st.selectbox("Unit", ["kg", "grams", "units"], index=["kg", "grams", "units"].index(unit), key=f"unit_{id}")
            new_urgent = st.checkbox("Urgent", value=bool(urgent), key=f"urg_{id}")

            if st.button("Update Order", key=f"update_{id}"):
                c.execute('''
                    UPDATE orders
                    SET customer_name = ?, product_name = ?, quantity = ?, unit = ?, urgent = ?
                    WHERE id = ?
                ''', (new_customer, new_product, new_qty, new_unit, int(new_urgent), id))
                conn.commit()
                st.success("Order updated successfully!")
                st.rerun()
else:
    st.info("No orders placed yet.")
