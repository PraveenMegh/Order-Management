import streamlit as st
import sqlite3
from utils.header import show_header
from utils.auth import check_login
from datetime import datetime

check_login()
show_header()

# Connect to database
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# ✅ Create table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    customer_name TEXT,
    product_name TEXT,
    quantity INTEGER,
    urgent BOOLEAN,
    status TEXT DEFAULT 'Pending',
    created_at TEXT,
    dispatched_quantity INTEGER,
    dispatched_at TEXT
)
''')
conn.commit()

# Function to insert order
def insert_order(username, customer_name, product_name, quantity, urgent):
    c.execute('''
        INSERT INTO orders (username, customer_name, product_name, quantity, urgent, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, customer_name, product_name, quantity, urgent, datetime.now()))
    conn.commit()

# Function to fetch orders for current user
def fetch_orders(username):
    c.execute('SELECT * FROM orders WHERE username = ?', (username,))
    return c.fetchall()

# --- UI ---

st.header("📦 Place a New Order")

with st.form("order_form"):
    customer_name = st.text_input("Customer Name")
    product_name = st.text_input("Product Name")
    quantity = st.number_input("Quantity", min_value=1)
    urgent = st.checkbox("Mark as Urgent")
    submit = st.form_submit_button("Submit Order")

    if submit:
        insert_order(
            st.session_state.username,
            customer_name,
            product_name,
            quantity,
            int(urgent)
        )
        st.success("Order placed successfully!")
        st.rerun()

st.header("📝 Your Orders (Editable Before Dispatch)")

orders = fetch_orders(st.session_state.username)

if orders:
    for order in orders:
        id, username, customer_name, product_name, quantity, urgent, status, created_at, dispatched_quantity, dispatched_at = order

        with st.expander(f"Order #{id} - {product_name}"):
            created_at_fmt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")

            st.markdown(f"**Created On**: {created_at_fmt}")

            if status == "Pending":
                new_customer = st.text_input("Customer Name", value=customer_name, key=f"cust_{id}")
                new_product = st.text_input("Product Name", value=product_name, key=f"prod_{id}")
                new_qty = st.number_input("Quantity", value=quantity, min_value=1, key=f"qty_{id}")
                new_urgent = st.checkbox("Urgent", value=bool(urgent), key=f"urg_{id}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Order", key=f"update_{id}"):
                        c.execute('''
                            UPDATE orders
                            SET customer_name = ?, product_name = ?, quantity = ?, urgent = ?
                            WHERE id = ?
                        ''', (new_customer, new_product, new_qty, int(new_urgent), id))
                        conn.commit()
                        st.success("Order updated successfully!")
                        st.rerun()

                with col2:
                    if st.button("❌ Delete Order", key=f"delete_{id}"):
                        c.execute('DELETE FROM orders WHERE id = ?', (id,))
                        conn.commit()
                        st.success(f"Order #{id} deleted successfully!")
                        st.rerun()
            else:
                st.warning("🚚 Order already dispatched. Cannot modify or delete.")

else:
    st.info("No orders placed yet.")
