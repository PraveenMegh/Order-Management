import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Demand Reports", layout="wide")
st.title("📈 Demand Analysis Reports")

conn = sqlite3.connect("data/orders.db")
df = pd.read_sql_query("SELECT * FROM orders", conn)
conn.close()

if df.empty:
    st.warning("No order data found.")
    st.stop()

# Ensure numeric quantity
df['order_quantity'] = pd.to_numeric(df['order_quantity'], errors='coerce')
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df.dropna(subset=['order_quantity', 'order_date'], inplace=True)

# --- 🔍 Filters ---
with st.sidebar:
    st.subheader("🔎 Filters")
    product_filter = st.text_input("Search by product name")
    start_date = st.date_input("Start date", value=df['order_date'].min().date())
    end_date = st.date_input("End date", value=df['order_date'].max().date())

# Apply filters
filtered_df = df.copy()
if product_filter:
    filtered_df = filtered_df[filtered_df['product_name'].str.contains(product_filter, case=False)]
filtered_df = filtered_df[
    (filtered_df['order_date'] >= pd.to_datetime(start_date)) &
    (filtered_df['order_date'] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.info("No data matching the selected filters.")
    st.stop()

# --- 🔝 Top Products ---
st.subheader("🔝 Top 5 High Demand Products (by Quantity)")
top = filtered_df.groupby('product_name')['order_quantity'].sum().sort_values(ascending=False).head(5)
st.bar_chart(top)

# --- 🔽 Low Products ---
st.subheader("📉 Bottom 5 Low Demand Products (by Quantity)")
low = filtered_df.groupby('product_name')['order_quantity'].sum().sort_values().head(5)
st.bar_chart(low)

# --- 📆 Calendar-Wise Chart ---
st.subheader("📆 Calendar-wise Demand Chart")
calendar_df = filtered_df.groupby('order_date')['order_quantity'].sum().reset_index()
fig = px.bar(calendar_df, x='order_date', y='order_quantity', title='Orders Over Time')
st.plotly_chart(fig, use_container_width=True)