import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
show_header()

st.header("🚚 Dispatch Orders")
st.markdown(" ")

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Fetch Data ---
c.execute('''
SELECT * FROM orders
WHERE status = 'Pending'
ORDER BY created_at ASC
''')
pending_orders = c.fetchall()

c.execute('''
SELECT * FROM orders
WHERE status = 'Dispatched'
ORDER BY dispatched_at DESC
''')
dispatched_orders = c.fetchall()

# --- Pending Orders Section ---

if st.session_state.role in ["Dispatch", "Admin"]:

    st.subheader("📦 Pending Orders (FIFO)")
    st.markdown(" ")

    if pending_orders:
        for order in pending_orders:
            id, username, customer_name, product_name, quantity, unit, urgent, status, created_at, dispatched_quantity, dispatched_at = order

            created_fmt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")

            with st.expander(f"Order #{id} - {product_name} ({quantity} {unit})"):
                st.markdown(f"**Created On**: {created_fmt}")
                st.markdown(f"**Customer**: {customer_name}")
                st.markdown(f"**Salesperson**: {username}")
                st.markdown(f"**Original Quantity**: {quantity} {unit}")
                st.markdown(f"**Urgent**: {'🔥 Yes' if urgent else 'No'}")

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

st.divider()

# --- Dispatched Orders Section ---

st.subheader("✅ Dispatched Orders")
st.markdown(" ")

if dispatched_orders:
    data = []
    for order in dispatched_orders:
        id, username, customer_name, product_name, quantity, unit, urgent, status, created_at, dispatched_quantity, dispatched_at = order

        created_fmt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")
        dispatched_fmt = datetime.strptime(dispatched_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")

        data.append({
            "Order ID": id,
            "Customer": customer_name,
            "Product": product_name,
            "Ordered Qty": f"{quantity} {unit}",
            "Dispatched Qty": f"{dispatched_quantity} {unit}" if dispatched_quantity else "",
            "Urgent": "🔥 Yes" if urgent else "No",
            "Created At": created_fmt,
            "Dispatched At": dispatched_fmt,
            "Salesperson": username
        })

    df = pd.DataFrame(data)

    # Sales view their own dispatched orders
    if st.session_state.role == "Sales":
        df = df[df["Salesperson"] == st.session_state.username]

    st.dataframe(df, use_container_width=True)

    if st.session_state.role == "Admin":
        buffer = pd.ExcelWriter('Dispatch_Summary.xlsx', engine='xlsxwriter')
        df.to_excel(buffer, index=False, sheet_name='Dispatch Summary')
        buffer.close()

        with open('Dispatch_Summary.xlsx', "rb") as file:
            st.download_button(
                label="📥 Download Dispatch Report (Excel)",
                data=file,
                file_name=f"Dispatch_Summary_{datetime.now().date()}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

else:
    st.info("ℹ️ No dispatched orders yet.")
