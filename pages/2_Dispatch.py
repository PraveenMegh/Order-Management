import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login

check_login()
show_header()

st.header("🚚 Dispatch Orders")

conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# Fetch pending orders FIFO
c.execute('''
SELECT * FROM orders
WHERE status = 'Pending'
ORDER BY created_at ASC
''')
pending_orders = c.fetchall()

# Fetch dispatched orders
c.execute('''
SELECT * FROM orders
WHERE status = 'Dispatched'
ORDER BY dispatched_at DESC
''')
dispatched_orders = c.fetchall()

# --- Dispatch Section ---

if st.session_state.role == "Dispatch" or st.session_state.role == "Admin":

    if pending_orders:
        st.subheader("📦 Pending Orders (FIFO)")

        today = datetime.now()

        for order in pending_orders:
            id, username, customer_name, product_name, quantity, urgent, status, created_at, dispatched_quantity, dispatched_at = order

            created_fmt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f")
            created_fmt_str = created_fmt.strftime("%d-%m-%Y %I:%M %p")

            highlight_style = ""
            if (today - created_fmt).days > 10:
                highlight_style = "background-color: #FFCCCC; padding: 10px; border-radius: 5px;"  # Light red

            with st.container():
                st.markdown(
                    f"<div style='{highlight_style}'>"
                    f"<b>Order #{id} - {product_name}</b><br>"
                    f"📅 <b>Created On:</b> {created_fmt_str}<br>"
                    f"👤 <b>Customer:</b> {customer_name}<br>"
                    f"🧑‍💼 <b>Salesperson:</b> {username}<br>"
                    f"📦 <b>Original Quantity:</b> {quantity}<br>"
                    f"🚩 <b>Urgent:</b> {'🔥 Yes' if urgent else 'No'}<br><br>",
                    unsafe_allow_html=True
                )

                dispatch_qty = st.number_input(
                    "Dispatch Quantity",
                    min_value=0,
                    max_value=quantity,
                    value=quantity,
                    key=f"dispatch_qty_{id}"
                )

                if st.button("Confirm Dispatch", key=f"confirm_dispatch_{id}"):
                    now = datetime.now()
                    c.execute('''
                        UPDATE orders
                        SET status = 'Dispatched',
                            dispatched_quantity = ?,
                            dispatched_at = ?
                        WHERE id = ?
                    ''', (dispatch_qty, now, id))
                    conn.commit()
                    st.success(f"Order #{id} dispatched successfully!")
                    st.rerun()

    else:
        st.info("✅ No pending orders for dispatch.")

else:
    st.warning("🚫 Only Dispatch or Admin can process dispatches.")

# --- Dispatched Orders Section ---

st.subheader("✅ Dispatched Orders")

if dispatched_orders:
    data = []
    for order in dispatched_orders:
        id, username, customer_name, product_name, quantity, urgent, status, created_at, dispatched_quantity, dispatched_at = order

        created_fmt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")
        dispatched_fmt = datetime.strptime(dispatched_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")

        data.append({
            "Order ID": id,
            "Customer": customer_name,
            "Product": product_name,
            "Ordered Qty": quantity,
            "Dispatched Qty": dispatched_quantity,
            "Urgent": "Yes" if urgent else "No",
            "Created At": created_fmt,
            "Dispatched At": dispatched_fmt,
            "Salesperson": username
        })

    df = pd.DataFrame(data)

    # Filter view: Sales can see only their orders
    if st.session_state.role == "Sales":
        df = df[df["Salesperson"] == st.session_state.username]

    st.dataframe(df, use_container_width=True)

    if st.session_state.role == "Admin":
        # Admin can download Excel report
        buffer = pd.ExcelWriter('Dispatch_Summary.xlsx', engine='xlsxwriter')
        df.to_excel(buffer, index=False, sheet_name='Dispatch Summary')
        buffer.close()

        with open('Dispatch_Summary.xlsx', "rb") as file:
            btn = st.download_button(
                label="📥 Download Dispatch Report (Excel)",
                data=file,
                file_name=f"Dispatch_Summary_{datetime.now().date()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("🚚 No dispatched orders yet.")
