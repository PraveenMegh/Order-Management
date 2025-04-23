import streamlit as st
import pandas as pd
from datetime import datetime
from utils.header import show_header

from utils.auth import check_login    # ✅ Optional: enforce login if used

st.set_page_config(page_title="Orders - Shree Sai Industries", layout="wide")  # ✅ Must be first Streamlit command

show_header()  # ✅ Show logo + header text
check_login()  # ✅ Optional: comment out if login not enforced here

# Initialize session state for orders if not present
if "orders" not in st.session_state:
    st.session_state.orders = []

st.title("📦 New Orders")

# ---- New Order Form ---- #
with st.form("order_form"):
    customer_name = st.text_input("Customer Name")
    product = st.text_input("Product")
    quantity = st.number_input("Quantity", min_value=1)
    urgent = st.checkbox("Mark as Urgent")
    submitted = st.form_submit_button("Submit Order")

    if submitted:
        order = {
            "id": len(st.session_state.orders) + 1,
            "customer": customer_name,
            "product": product,
            "quantity": quantity,
            "urgent": urgent,
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dispatched_quantity": None
        }
        st.session_state.orders.append(order)
        st.success("Order submitted successfully!")

# ---- Editable Table for Un-dispatched Orders ---- #
st.subheader("📝 Edit Orders (Before Dispatch)")

for order in st.session_state.orders:
    if order["status"] == "Pending":
        with st.expander(f"Order #{order['id']} - {order['product']}"):
            new_customer = st.text_input("Customer", value=order["customer"], key=f"cust_{order['id']}")
            new_product = st.text_input("Product", value=order["product"], key=f"prod_{order['id']}")
            new_quantity = st.number_input("Quantity", value=order["quantity"], min_value=1, key=f"qty_{order['id']}")
            new_urgent = st.checkbox("Urgent", value=order["urgent"], key=f"urg_{order['id']}")
            if st.button("Update Order", key=f"update_{order['id']}"):
                order.update({
                    "customer": new_customer,
                    "product": new_product,
                    "quantity": new_quantity,
                    "urgent": new_urgent
                })
                st.success("Order updated.")
