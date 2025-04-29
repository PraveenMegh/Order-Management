import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login

# --- Authentication and Access Control ---
check_login()
if st.session_state.get("role") not in ["Admin", "Dispatch"]:
    st.error("\ud83d\udeab You do not have permission to access this page.")
    st.stop()

# --- Page Header ---
show_header()
st.header("\ud83d\ude9a Dispatch Orders")
st.markdown(" ")

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Fetch Data ---
pending_orders = pd.read_sql_query("SELECT * FROM orders WHERE status = 'Pending' ORDER BY created_at ASC", conn)
dispatched_orders = pd.read_sql_query("SELECT * FROM orders WHERE status = 'Dispatched' ORDER BY dispatched_at DESC", conn)

# --- Pending Orders Section ---
st.caption("\u26a1\ufe0f Please dispatch orders in FIFO (First In, First Out) sequence. Oldest orders are shown first.")

if pending_orders.empty:
    st.success("✅ No pending orders for dispatch.")
else:
    st.subheader("\ud83d\udce6 Pending Orders")
    for idx, order in pending_orders.iterrows():
        with st.expander(f"Order #{order['id']} - {order['product_name']} ({order['quantity']} {order['unit']})"):
            st.markdown(f"**Customer**: {order['customer_name']}")
            st.markdown(f"**Salesperson**: {order['username']}")
            st.markdown(f"**Unit Price**: {order['price']} {order['currency']}")
            st.markdown(f"**Unit Type**: {order['unit_type']}")
            st.markdown(f"**Urgent**: {'🔥 Yes' if order['urgent'] else 'No'}")
            st.markdown(f"**Created On**: {datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%m-%Y %I:%M %p')}")

            dispatch_qty = st.number_input(
                "Dispatch Quantity",
                min_value=0,
                max_value=order['quantity'],
                value=order['quantity'],
                key=f"dispatch_qty_{order['id']}"
            )

            if st.button("Confirm Dispatch", key=f"confirm_dispatch_{order['id']}"):
                now = datetime.now()
                c.execute('''
                    UPDATE orders
                    SET status = 'Dispatched',
                        dispatched_quantity = ?,
                        dispatched_at = ?,
                        dispatched_by = ?
                    WHERE id = ?
                ''', (dispatch_qty, now, st.session_state.username, order['id']))
                conn.commit()
                st.success(f"✅ Order #{order['id']} dispatched successfully!")
                st.rerun()

st.divider()

# --- Dispatched Orders Section ---
st.subheader("✅ Dispatched Orders")

if dispatched_orders.empty:
    st.info("ℹ️ No dispatched orders yet.")
else:
    df = dispatched_orders.copy()
    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d-%m-%Y %I:%M %p')
    df['dispatched_at'] = pd.to_datetime(df['dispatched_at']).dt.strftime('%d-%m-%Y %I:%M %p')

    # Dispatch users view only their dispatched entries
    if st.session_state.role == "Dispatch":
        df = df[df["dispatched_by"] == st.session_state.username]

    st.dataframe(df, use_container_width=True)

    if st.session_state.role == "Admin":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="\ud83d\udcc5 Download Dispatched Orders (CSV)",
            data=csv,
            file_name=f"Dispatched_Orders_{datetime.now().date()}.csv",
            mime="text/csv"
        )

st.divider()
if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

