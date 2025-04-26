import streamlit as st
import pandas as pd
from utils.header import show_header
from utils.auth import check_login
import sqlite3
import plotly.express as px

st.set_page_config(page_title="📈 Demand Analysis - Shree Sai Industries", layout="wide")

show_header()
st.image("./assets/logo.png", width=200)

check_login()

allowed_roles = ["Admin", "Dispatch", "Accounts"]
if st.session_state.get("role") not in allowed_roles:
    st.error("🚫 You do not have permission to view this page.")
    st.stop()

st.title("📈 Demand Analysis")

conn = sqlite3.connect("data/orders.db")
df = pd.read_sql("SELECT * FROM orders", conn)
conn.close()

st.subheader("Demand Summary")
st.dataframe(df)

st.subheader("Demand Chart")
fig = px.bar(df, x="product", y="quantity", title="Product Demand")
st.plotly_chart(fig, use_container_width=True)
