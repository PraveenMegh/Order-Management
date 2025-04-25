import streamlit as st
import pandas as pd
from header import show_header
from utils.auth import check_login
import sqlite3  # or your database connection method
import plotly.express as px  # recommended for nice charts

# ✅ Correct page config
st.set_page_config(page_title="Demand Analysis - Shree Sai Industries", layout="wide")

# ✅ Session check
if "role" not in st.session_state:
    st.markdown("<h3>Please open this page from the main dashboard.</h3>", unsafe_allow_html=True)
    st.stop()

# ✅ Authentication check
check_login()

# ✅ Display header and logo
show_header()
st.image("./assets/logo.png", width=200)

# ✅ Role-based access
allowed_roles = ["Admin", "Dispatch", "Accounts"]
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.title("📊 Demand Analysis")

# ✅ Connect to your database
conn = sqlite3.connect("orders.db")
query = "SELECT product_name, quantity, order_date FROM orders"
df = pd.read_sql(query, conn)
conn.close()

# ✅ Basic filters (date range, product search)
with st.sidebar:
    st.header("Filter Demand Data")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    product_filter = st.text_input("Search Product")

filtered_df = df.copy()
filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])

# Apply filters
if start_date and end_date:
    filtered_df = filtered_df[
        (filtered_df["order_date"] >= pd.to_datetime(start_date))
        & (filtered_df["order_date"] <= pd.to_datetime(end_date))
    ]

if product_filter:
    filtered_df = filtered_df[filtered_df["product_name"].str.contains(product_filter, case=False)]

# ✅ Demand summary table
st.subheader("Demand Summary")
st.dataframe(filtered_df.groupby("product_name").agg(
    total_quantity=pd.NamedAgg(column="quantity", aggfunc="sum"),
    frequency=pd.NamedAgg(column="quantity", aggfunc="count")
).reset_index().sort_values(by="total_quantity", ascending=False))

# ✅ Demand Chart
st.subheader("Demand Chart")
chart_data = filtered_df.groupby("product_name").sum().reset_index()
fig = px.bar(chart_data, x="product_name", y="quantity", title="Demand by Product")
st.plotly_chart(fig, use_container_width=True)

# ✅ Export as PDF (to be implemented)
st.button("Export Report as PDF", key="export_pdf_btn")
