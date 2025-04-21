import streamlit as st
from utils.header import show_header
show_header()
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Demand Analysis Reports")

uploaded_file = st.file_uploader("Upload your Orders Excel file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    top_products = df['Product'].value_counts().head(10)
    low_products = df['Product'].value_counts().tail(10)
    qty_group = df.groupby('Product')['Quantity'].sum().sort_values(ascending=False).head(10)

    st.subheader("🔼 Top 10 Most Ordered Products (by frequency)")
    st.bar_chart(top_products)

    st.subheader("🔽 Least Ordered Products")
    st.bar_chart(low_products)

    st.subheader("📦 Top Products by Total Quantity")
    st.bar_chart(qty_group)
else:
    st.warning("Please upload an Excel file to see demand charts.")

from utils.header import show_header
show_header()