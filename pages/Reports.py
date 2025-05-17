import streamlit as st
import sqlite3
import pandas as pd
from utils.header import show_header
from utils.auth import check_login
from fpdf import FPDF
import matplotlib.pyplot as plt

# --- Authentication ---
check_login()
if st.session_state.get("role") != "Admin":
    st.error("🚫 You do not have permission to access this page.")
    st.stop()

# --- UI Header ---
show_header()
st.title("📊 Order Reports")

# --- DB Connection ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)

# --- Fetch Data ---
pending_products = pd.read_sql_query("""
    SELECT oi.order_id, o.customer_name, oi.product_name, oi.ordered_qty, oi.unit, oi.price, oi.unit_type,
           o.currency, o.urgent, o.created_at
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Pending'
""", conn)

dispatched_products = pd.read_sql_query("""
    SELECT oi.order_id, o.customer_name, oi.product_name, oi.ordered_qty, oi.dispatched_qty, oi.unit,
           oi.price, oi.unit_type, o.currency, o.urgent, o.created_at, oi.dispatched_at, oi.dispatched_by
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Dispatched'
""", conn)

# --- Format Dates ---
if not pending_products.empty:
    pending_products['created_at'] = pd.to_datetime(pending_products['created_at'], errors='coerce').dt.strftime('%d-%m-%Y %I:%M %p')

if not dispatched_products.empty:
    dispatched_products['created_at'] = pd.to_datetime(dispatched_products['created_at'], errors='coerce')
    dispatched_products['dispatched_at'] = pd.to_datetime(dispatched_products['dispatched_at'], errors='coerce')
    dispatched_products['shortfall'] = dispatched_products['ordered_qty'] - dispatched_products['dispatched_qty']

# --- Pending Orders ---
st.subheader("📦 Pending Products")
if pending_products.empty:
    st.success("✅ No pending products!")
else:
    def highlight_urgent(val):
        return 'background-color: #FFD1D1' if val == 1 else ''
    st.dataframe(pending_products.style.applymap(highlight_urgent, subset=["urgent"]), use_container_width=True)

st.divider()

# --- Dispatched Orders ---
st.subheader("✅ Dispatched Products")
if dispatched_products.empty:
    st.info("ℹ️ No dispatched products yet.")
else:
    st.dataframe(dispatched_products, use_container_width=True)
    csv = dispatched_products.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Dispatched Products (CSV)", data=csv, file_name="dispatched_products.csv", mime="text/csv")

    # --- Charts ---
    st.subheader("📈 Product Demand Analysis")

    demand_df = dispatched_products.groupby('product_name')['dispatched_qty'].sum().reset_index()

    st.write("### 🔥 High-Demand Products")
    fig, ax = plt.subplots()
    demand_df.sort_values(by='dispatched_qty', ascending=False).plot.bar(x='product_name', y='dispatched_qty', ax=ax)
    ax.set_ylabel('Total Dispatched Quantity')
    st.pyplot(fig)

    st.write("### 💤 Low-Demand Products (<=5)")
    low_demand = demand_df[demand_df['dispatched_qty'] <= 5]
    if not low_demand.empty:
        fig2, ax2 = plt.subplots()
        low_demand.sort_values(by='dispatched_qty').plot.bar(x='product_name', y='dispatched_qty', ax=ax2, color='orange')
        ax2.set_ylabel('Total Dispatched Quantity')
        st.pyplot(fig2)
    else:
        st.info("✅ No low-demand products.")

    st.write("### 📅 Dispatch Trend Over Time")
    trend_df = dispatched_products.copy()
    trend_df['dispatch_date'] = trend_df['dispatched_at'].dt.date
    trend_summary = trend_df.groupby('dispatch_date')['dispatched_qty'].sum().reset_index()
    if not trend_summary.empty:
        fig3, ax3 = plt.subplots()
        trend_summary.plot(x='dispatch_date', y='dispatched_qty', ax=ax3, marker='o')
        ax3.set_ylabel('Total Dispatched Qty')
        st.pyplot(fig3)
    else:
        st.info("ℹ️ No dispatch trend data yet.")

    # --- PDF Report ---
    st.write("### 📄 Download Full Dispatch Report (PDF)")

    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Dispatched Products Report", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        for _, row in dispatched_products.iterrows():
            dispatched_at = row['dispatched_at'].strftime('%d-%m-%Y %I:%M %p') if pd.notnull(row['dispatched_at']) else 'N/A'
            pdf.multi_cell(0, 8,
                f"Order ID: {row['order_id']}, Customer: {row['customer_name']}, Product: {row['product_name']}, "
                f"Qty: {row['ordered_qty']}, Dispatched: {row['dispatched_qty']}, Unit: {row['unit']}, "
                f"Dispatched At: {dispatched_at}, By: {row['dispatched_by']}"
            )
            pdf.ln(2)
        return pdf.output(dest='S').encode('latin-1')

    pdf_bytes = generate_pdf()
    st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="dispatched_products_report.pdf", mime="application/pdf")

conn.close()
