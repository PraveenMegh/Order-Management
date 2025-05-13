import streamlit as st
import snowflake.connector
from dotenv import load_dotenv
import os
import pandas as pd
import sys
from datetime import datetime

# ✅ Load .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# ✅ Debug prints
print("SNOWFLAKE_ACCOUNT =", os.environ.get('SNOWFLAKE_ACCOUNT'))
print("SNOWFLAKE_USER =", os.environ.get('SNOWFLAKE_USER'))
print("SNOWFLAKE_PASSWORD =", os.environ.get('SNOWFLAKE_PASSWORD'))
print("SNOWFLAKE_WAREHOUSE =", os.environ.get('SNOWFLAKE_WAREHOUSE'))
print("SNOWFLAKE_DATABASE =", os.environ.get('SNOWFLAKE_DATABASE'))
print("SNOWFLAKE_SCHEMA =", os.environ.get('SNOWFLAKE_SCHEMA'))
print("SNOWFLAKE_ROLE =", os.environ.get('SNOWFLAKE_ROLE'))

# --- Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.header import show_header
from utils.auth import check_login

# --- Authentication ---
check_login()
if st.session_state.get("role") not in ["Admin", "Dispatch"]:
    st.error("⛔ You do not have permission to access this page.")
    st.stop()

# ✅ Connect using env vars (after authentication)
try:
    conn = snowflake.connector.connect(
        user=os.environ.get('SNOWFLAKE_USER'),
        password=os.environ.get('SNOWFLAKE_PASSWORD'),
        account=os.environ.get('SNOWFLAKE_ACCOUNT'),
        warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE'),
        database=os.environ.get('SNOWFLAKE_DATABASE'),
        schema=os.environ.get('SNOWFLAKE_SCHEMA'),
        role=os.environ.get('SNOWFLAKE_ROLE')
    )
    c = conn.cursor()
except Exception as e:
    st.error(f"❌ Failed to connect to Snowflake: {e}")
    st.stop()

# --- Page Header ---
show_header()
st.header("🚚 Dispatch Orders")
st.markdown(" ")

# --- Fetch Pending Products ---
sql_query = """
    SELECT 
        oi.id AS item_id,
        oi.order_id,
        o.order_code,
        o.customer_name,
        o.username AS salesperson,
        o.currency,
        o.urgent,
        o.created_at,
        oi.product_name,
        oi.ordered_qty,
        oi.unit,
        oi.price,
        oi.unit_type,
        oi.status
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Pending'
    ORDER BY o.created_at ASC
"""
c.execute(sql_query)
pending_products = pd.DataFrame(c.fetchall(), columns=[col[0] for col in c.description])

# --- Fetch Dispatched Products ---
dispatched_query = """
    SELECT
        oi.id AS item_id,
        oi.order_id,
        o.order_code,
        o.customer_name,
        o.username AS salesperson,
        o.currency,
        o.urgent,
        o.created_at,
        oi.product_name,
        oi.ordered_qty,
        oi.dispatched_qty,
        oi.unit,
        oi.price,
        oi.unit_type,
        oi.status,
        oi.dispatched_at,
        oi.dispatched_by
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Dispatched'
    ORDER BY oi.dispatched_at DESC
"""
c.execute(dispatched_query)
dispatched_products = pd.DataFrame(c.fetchall(), columns=[col[0] for col in c.description])

# --- Pending Orders Section ---
st.caption("⚡ Please dispatch orders in FIFO (First In, First Out) sequence. Oldest orders are shown first.")

if pending_products.empty:
    st.success("✅ No pending products for dispatch.")
else:
    st.subheader("📦 Pending Products for Dispatch")
    grouped = pending_products.groupby('order_id')

    for order_id, order_df in grouped:
        with st.expander(f"Order {order_df['order_code'].iloc[0]} - {order_df['customer_name'].iloc[0]}"):
            st.markdown(f"**Customer**: {order_df['customer_name'].iloc[0]}")
            st.markdown(f"**Salesperson**: {order_df['salesperson'].iloc[0]}")
            st.markdown(f"**Currency**: {order_df['currency'].iloc[0]}")
            st.markdown(f"**Urgent**: {'🔥 Yes' if order_df['urgent'].iloc[0] else 'No'}")
            try:
                created_at = pd.to_datetime(order_df['created_at'].iloc[0])
                st.markdown(f"**Created On**: {created_at.strftime('%d-%m-%Y %I:%M %p')}")
            except:
                st.markdown("**Created On**: Invalid timestamp")

            editable_df = order_df[['item_id', 'product_name', 'ordered_qty', 'unit']].copy()
            editable_df['dispatched_qty'] = editable_df['ordered_qty']

            editable_df = st.data_editor(
                editable_df,
                column_config={
                    "item_id": st.column_config.NumberColumn(disabled=True, label=""),  # hidden in UI
                    "product_name": st.column_config.TextColumn(disabled=True),
                    "ordered_qty": st.column_config.NumberColumn(disabled=True),
                    "unit": st.column_config.TextColumn(disabled=True),
                    "dispatched_qty": st.column_config.NumberColumn(help="Edit dispatched qty if sending less than ordered")
                },
                hide_index=True,
                use_container_width=True
            )

            if st.button(f"✅ Confirm Dispatch for Order #{order_id}", key=f"dispatch_btn_{order_id}"):
                now = datetime.now()
                dispatcher_name = st.session_state.username

                for idx, row in editable_df.iterrows():
                    item_id = row['item_id']
                    dispatched_qty = row['dispatched_qty']
                    st.write(f"DEBUG: Updating item_id={item_id}, dispatched_qty={dispatched_qty}")

                    c.execute("CALL dispatch_order(%s, %s, %s, %s)", (item_id, dispatched_qty, dispatcher_name, now))

                conn.commit()
                st.success(f"✅ Order #{order_id} dispatched!")
                st.rerun()

st.divider()

# --- Dispatched Orders Section ---
st.subheader("✅ Dispatched Orders")

if dispatched_products.empty:
    st.info("ℹ️ No dispatched orders yet.")
else:
    df = dispatched_products.copy()
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')
    if 'dispatched_at' in df.columns:
        df['dispatched_at'] = pd.to_datetime(df['dispatched_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')

    if st.session_state.role == "Dispatch":
        df = df[df["dispatched_by"] == st.session_state.username]

    st.dataframe(df, use_container_width=True)

    if st.session_state.role == "Admin":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="Dispatched_Orders.csv",
            mime="text/csv"
        )
    elif st.session_state.role == "Dispatch":
        st.info("Download available only for Admin.")

st.divider()

c.close()
conn.close()

if st.button("🔒 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")
