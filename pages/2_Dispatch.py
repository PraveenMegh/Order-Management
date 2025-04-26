import streamlit as st
import pandas as pd
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login
import io

st.set_page_config(page_title="🚚 Dispatch Orders - Shree Sai Industries", layout="wide")

show_header()
st.image("./assets/logo.png", width=200)

check_login()

allowed_roles = ["Admin", "Dispatch"]
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.title("🚚 Dispatch Orders")

orders = st.session_state.get("orders", [])

pending_orders = [o for o in orders if o["status"] == "Pending"]

if not pending_orders:
    st.info("No pending orders for dispatch.")
else:
    for order in pending_orders:
        with st.expander(f"Order #{order['id']} - {order['product']}"):
            st.markdown(f"**Customer**: {order['customer']}")
            st.markdown(f"**Original Quantity**: {order['quantity']}")
            st.markdown(f"**Urgent**: {'✅ Yes' if order['urgent'] else 'No'}")

            dispatched_qty = st.number_input(
                "Dispatch Quantity", min_value=0, max_value=order['quantity'], value=order['quantity'], key=f"dispatch_{order['id']}"
            )

            if st.button("Confirm Dispatch", key=f"confirm_{order['id']}"):
                order["status"] = "Dispatched"
                order["dispatched_quantity"] = dispatched_qty
                order["dispatched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success("Order dispatched!")

dispatched_orders = [o for o in orders if o["status"] == "Dispatched"]
if dispatched_orders:
    st.subheader("📦 Dispatched Orders Summary")
    df = pd.DataFrame(dispatched_orders)[["id", "customer", "product", "quantity", "dispatched_quantity", "urgent", "dispatched_at"]]
    df.columns = ["Order ID", "Customer", "Product", "Original Qty", "Dispatched Qty", "Urgent", "Dispatched At"]
    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Dispatch Summary")
    st.download_button(
        label="📥 Download Dispatch Summary as Excel",
        data=buffer.getvalue(),
        file_name=f"Dispatch_Summary_{datetime.now().date()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
