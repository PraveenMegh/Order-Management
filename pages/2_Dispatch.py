import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
show_header()

# --- Database Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Role Detection ---
role = st.session_state.get("role")
username = st.session_state.get("username")

st.title("🚚 Dispatch Management")

# --- Section: Pending Orders ---

st.subheader("📦 Pending Orders")

if role == "Dispatch" or role == "Admin":
    # Dispatch and Admin can see all pending
    c.execute('''
    SELECT id, username, customer_name, product_name, quantity, urgent, created_at
    FROM orders
    WHERE status = 'Pending'
    ORDER BY urgent DESC, created_at ASC
    ''')
else:
    # Salesperson sees only their own pending
    c.execute('''
    SELECT id, username, customer_name, product_name, quantity, urgent, created_at
    FROM orders
    WHERE status = 'Pending' AND username = ?
    ORDER BY urgent DESC, created_at ASC
    ''', (username,))
    
pending_orders = c.fetchall()

if pending_orders:
    for order in pending_orders:
        id, user, customer, product, qty, urgent, created_at = order
        
        expander_label = f"🔥 Order #{id} - {product}" if urgent else f"Order #{id} - {product}"
        with st.expander(expander_label):
            st.markdown(f"**Customer:** {customer}")
            st.markdown(f"**Salesperson:** {user}")
            st.markdown(f"**Quantity Ordered:** {qty}")
            st.markdown(f"**Created At:** {datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f').strftime('%d-%b-%Y %I:%M %p')}")
            if urgent:
                st.markdown("**Urgent:** 🔥 Yes")
            else:
                st.markdown("**Urgent:** No")

            if role == "Dispatch" or role == "Admin":
                dispatched_qty = st.number_input(
                    "Enter Dispatch Quantity",
                    min_value=0,
                    max_value=qty,
                    value=qty,
                    key=f"dispatch_qty_{id}"
                )

                if st.button(f"✅ Confirm Dispatch for Order #{id}", key=f"confirm_dispatch_{id}"):
                    dispatched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute('''
                        UPDATE orders
                        SET status = 'Dispatched',
                            dispatched_quantity = ?,
                            dispatched_at = ?
                        WHERE id = ?
                    ''', (dispatched_qty, dispatched_at, id))
                    conn.commit()
                    st.success(f"Order #{id} dispatched successfully!")
                    st.rerun()
else:
    st.info("✅ No pending orders.")

# --- Section: Dispatched Orders ---

st.subheader("✅ Dispatched Orders")

if role == "Dispatch" or role == "Admin":
    dispatched_df = pd.read_sql_query('''
    SELECT id, username, customer_name, product_name, quantity, dispatched_quantity, urgent, created_at, dispatched_at
    FROM orders
    WHERE status = 'Dispatched'
    ORDER BY dispatched_at DESC
    ''', conn)
else:
    # Sales: only their own dispatched
    dispatched_df = pd.read_sql_query('''
    SELECT id, username, customer_name, product_name, quantity, dispatched_quantity, urgent, created_at, dispatched_at
    FROM orders
    WHERE status = 'Dispatched' AND username = ?
    ORDER BY dispatched_at DESC
    ''', conn, params=(username,))

if not dispatched_df.empty:
    dispatched_df['Created At'] = pd.to_datetime(dispatched_df['created_at']).dt.strftime("%d-%b-%Y %I:%M %p")
    dispatched_df['Dispatched At'] = pd.to_datetime(dispatched_df['dispatched_at']).dt.strftime("%d-%b-%Y %I:%M %p")

    display_df = dispatched_df[['id', 'username', 'customer_name', 'product_name', 'quantity', 'dispatched_quantity', 'urgent', 'Created At', 'Dispatched At']]
    display_df.rename(columns={
        'id': 'Order ID',
        'username': 'Sales Person',
        'customer_name': 'Customer',
        'product_name': 'Product',
        'quantity': 'Ordered Qty',
        'dispatched_quantity': 'Dispatched Qty',
        'urgent': 'Urgent'
    }, inplace=True)

    st.dataframe(display_df, use_container_width=True)

    # Only Admin can download the report
    if role == "Admin":
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Dispatch Report (CSV)",
            data=csv,
            file_name=f"Dispatch_Report_{datetime.now().strftime('%d-%b-%Y')}.csv",
            mime="text/csv"
        )
else:
    st.info("No dispatched orders yet.")
