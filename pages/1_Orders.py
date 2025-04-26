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

# ✅ Create orders table if not exists
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

# ✅ Create products table if not exists
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    unit TEXT
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

# Function to fetch all products
def fetch_all_products():
    c.execute('SELECT name FROM products')
    return [row[0] for row in c.fetchall()]

# Function to save new product
def save_new_product(name, unit):
    c.execute('INSERT OR IGNORE INTO products (name, unit) VALUES (?, ?)', (name, unit))
    conn.commit()

# Function to get unit of a product
def fetch_product_unit(name):
    c.execute('SELECT unit FROM products WHERE name = ?', (name,))
    result = c.fetchone()
    return result[0] if result else None

# --- UI ---

st.header("📦 Place a New Order")

with st.form("order_form"):
    customer_name = st.text_input("Customer Name")
    
    products = fetch_all_products()
    product_selection = st.selectbox("Select Product", options=products + ["➕ Add New Product"])

    new_product = None
    new_unit = None

    if product_selection == "➕ Add New Product":
        new_product = st.text_input("Enter New Product Name")
        new_unit = st.selectbox("Select Unit", ["Kg", "Grams", "Units"])

    quantity = st.number_input("Quantity", min_value=1)
    urgent = st.checkbox("Mark as Urgent")

    submit = st.form_submit_button("Submit Order")

    if submit:
        # Validation
        if product_selection == "➕ Add New Product":
            if not new_product or not new_unit:
                st.error("Please enter both Product Name and Unit.")
                st.stop()
            else:
                save_new_product(new_product, new_unit)
                product_name = new_product
        else:
            product_name = product_selection

        insert_order(
            st.session_state.username,
            customer_name,
            product_name,
            quantity,
            int(urgent)
        )
        st.success("Order placed successfully!")


st.header("📝 Your Orders (Editable Before Dispatch)")

orders = fetch_orders(st.session_state.username)

if orders:
    for order in orders:
        id, username, customer_name, product_name, quantity, urgent, status, created_at, dispatched_quantity, dispatched_at = order

        with st.expander(f"Order #{id} - {product_name}"):
            new_customer = st.text_input("Customer Name", value=customer_name, key=f"cust_{id}")
            new_product = st.text_input("Product Name", value=product_name, key=f"prod_{id}")
            new_qty = st.number_input("Quantity", value=quantity, min_value=1, key=f"qty_{id}")
            new_urgent = st.checkbox("Urgent", value=bool(urgent), key=f"urg_{id}")

            if st.button("Update Order", key=f"update_{id}"):
                c.execute('''
                    UPDATE orders
                    SET customer_name = ?, product_name = ?, quantity = ?, urgent = ?
                    WHERE id = ?
                ''', (new_customer, new_product, new_qty, int(new_urgent), id))
                conn.commit()
                st.success("Order updated successfully!")
                st.rerun()

else:
    st.info("No orders placed yet.")
