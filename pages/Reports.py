import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Demand Analysis Reports")

@st.cache_data
def load_data():
    df = pd.read_excel("data/sample_data.xlsx")
    return df

df = load_data()
if not df.empty:
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
    st.warning("No data found.")
