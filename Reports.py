import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Demand Reports", layout="wide")
st.title("📈 Demand Analysis Reports")

# Load data
conn = sqlite3.connect("data/orders.db")
df = pd.read_sql_query("SELECT * FROM orders", conn)
conn.close()

if df.empty:
    st.warning("No order data found.")
    st.stop()

df['order_quantity'] = pd.to_numeric(df['order_quantity'], errors='coerce')
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df.dropna(subset=['order_quantity', 'order_date'], inplace=True)

# Filters
with st.sidebar:
    st.subheader("🔎 Filters")
    product_filter = st.text_input("Search by product name")
    start_date = st.date_input("Start date", value=df['order_date'].min().date())
    end_date = st.date_input("End date", value=df['order_date'].max().date())

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

# Demand analysis
top = filtered_df.groupby('product_name')['order_quantity'].sum().sort_values(ascending=False).head(5)
low = filtered_df.groupby('product_name')['order_quantity'].sum().sort_values().head(5)

st.subheader("🔝 Top 5 High Demand Products (by Quantity)")
st.bar_chart(top)

st.subheader("📉 Bottom 5 Low Demand Products (by Quantity)")
st.bar_chart(low)

st.subheader("📆 Calendar-wise Demand Chart")
calendar_df = filtered_df.groupby('order_date')['order_quantity'].sum().reset_index()
fig = px.bar(calendar_df, x='order_date', y='order_quantity', title='Orders Over Time')
chart_path = "reports/calendar_chart.png"
fig.write_image(chart_path)
st.plotly_chart(fig, use_container_width=True)

# Generate PDF
def create_demand_pdf(filename, top_data, low_data, chart_path):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 50
    line_height = 16

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - margin, "Shree Sai Industries - Demand Summary")
    c.setFont("Helvetica", 12)
    c.drawString(margin, height - margin - 30, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    y = height - margin - 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Top 5 High Demand Products:")
    c.setFont("Helvetica", 11)
    for i, (name, qty) in enumerate(top_data.items()):
        y -= line_height
        c.drawString(margin + 20, y, f"{i+1}. {name}: {int(qty)} units")

    y -= line_height * 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Bottom 5 Low Demand Products:")
    c.setFont("Helvetica", 11)
    for i, (name, qty) in enumerate(low_data.items()):
        y -= line_height
        c.drawString(margin + 20, y, f"{i+1}. {name}: {int(qty)} units")

    if os.path.exists(chart_path):
        y -= 220
        c.drawImage(ImageReader(chart_path), margin, y, width=500, height=200)

    c.save()
    return filename

# Generate and Download Button
if st.button("📥 Download Demand Report (PDF)"):
    today = datetime.now().strftime("%Y-%m-%d")
    pdf_file = f"reports/Demand_Summary_{today}.pdf"
    create_demand_pdf(pdf_file, top, low, chart_path)
    with open(pdf_file, "rb") as f:
        st.download_button("Click to Download", f, file_name=os.path.basename(pdf_file))