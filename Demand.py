import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from utils.header import show_header
from utils.auth import check_login

st.set_page_config(page_title="📊 Demand Analysis - Shree Sai Industries", layout="wide")

show_header()
check_login()

st.title("📊 Product Demand Analysis")

# Load orders from session or show warning
orders = st.session_state.get("orders", [])
if not orders:
    st.warning("No orders found to analyze.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(orders)
df["created_at"] = pd.to_datetime(df["created_at"])

# Date range filter
date_range = st.date_input("Select date range", [datetime.now() - timedelta(days=90), datetime.now()])
if st.button("Last 7 Days"):
    date_range = [datetime.now() - timedelta(days=7), datetime.now()]
elif st.button("Last 30 Days"):
    date_range = [datetime.now() - timedelta(days=30), datetime.now()]
elif st.button("Last 90 Days"):
    date_range = [datetime.now() - timedelta(days=90), datetime.now()]
filtered_df = df[(df["created_at"] >= pd.to_datetime(date_range[0])) & (df["created_at"] <= pd.to_datetime(date_range[1]))]

# Group by product and aggregate
grouped = filtered_df.groupby("product").agg(
    total_quantity=pd.NamedAgg(column="quantity", aggfunc="sum"),
    order_count=pd.NamedAgg(column="product", aggfunc="count"),
    last_order=pd.NamedAgg(column="created_at", aggfunc="max")
).reset_index()

# Sort by quantity (descending)
st.subheader("🔥 Trending Products")
st.dataframe(grouped.sort_values("total_quantity", ascending=False), use_container_width=True)

# 📊 Bar Chart: Top 5 Products
st.subheader("📈 Top 5 Products (by Quantity)")
top5 = grouped.sort_values("total_quantity", ascending=False).head(5)
fig, ax = plt.subplots()
fig.tight_layout()
ax.bar(top5["product"], top5["total_quantity"])
ax.set_xlabel("Product")
ax.set_ylabel("Total Quantity")
ax.set_title("Top 5 Products")
st.pyplot(fig)

# 📉 Low selling (bottom 10)
st.subheader("📉 Low-Selling Products")
low_selling = grouped.sort_values("total_quantity").head(10)
st.dataframe(low_selling, use_container_width=True)

# 📊 Bar Chart: Bottom 5 Products
st.subheader("📈 Bottom 5 Products (by Quantity)")
fig2, ax2 = plt.subplots()
fig2.tight_layout()
ax2.bar(low_selling["product"], low_selling["total_quantity"])
ax2.set_xlabel("Product")
ax2.set_ylabel("Total Quantity")
ax2.set_title("Bottom 5 Products")
st.pyplot(fig2)

# Products with no orders in last 3 months
st.subheader("🛑 Products with No Demand in Last 3 Months")
all_products = df["product"].unique()
active_products = filtered_df["product"].unique()
no_demand = set(all_products) - set(active_products)

if no_demand:
    st.write(", ".join(no_demand))
else:
    st.success("All products had some demand in the selected period.")
