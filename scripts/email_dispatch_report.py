import sqlite3
import pandas as pd
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import os

# Email Config
SENDER_EMAIL = "praveeenmeghkrish@gmail.com"
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App password stored as environment variable
RECEIVER_EMAIL = "info@shreesaisalt.com"

# Connect to database
conn = sqlite3.connect('data/orders.db')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Fetch yesterday's dispatched orders
query = '''
SELECT id, customer_name, product_name, dispatched_quantity, urgent, username, dispatched_at
FROM orders
WHERE status = 'Dispatched' 
AND DATE(dispatched_at) = ?
ORDER BY dispatched_at ASC
'''

df = pd.read_sql_query(query, conn, params=(yesterday,))
conn.close()

if df.empty:
    print("❌ No dispatched orders found for yesterday. Email not sent.")
    exit()

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, f"Daily Dispatch Report - {yesterday}", ln=True, align="C")
pdf.ln(10)

# Table Header
pdf.set_font("Arial", "B", 12)
headers = ["Order ID", "Customer", "Product", "Qty", "Urgent", "Salesperson", "Dispatched At"]
for header in headers:
    pdf.cell(28, 8, header, border=1, align='C')
pdf.ln()

# Table Rows
pdf.set_font("Arial", "", 11)
for _, row in df.iterrows():
    pdf.cell(28, 8, str(row['id']), border=1)
    pdf.cell(28, 8, row['customer_name'][:10], border=1)
    pdf.cell(28, 8, row['product_name'][:10], border=1)
    pdf.cell(28, 8, str(row['dispatched_quantity']), border=1)
    pdf.cell(28, 8, "Yes" if row['urgent'] else "No", border=1)
    pdf.cell(28, 8, row['username'][:10], border=1)
    dispatched_time = pd.to_datetime(row['dispatched_at']).strftime('%H:%M')
    pdf.cell(28, 8, dispatched_time, border=1)
    pdf.ln()

# Save PDF
pdf_path = f"Dispatch_Report_{yesterday}.pdf"
pdf.output(pdf_path)

# Send Email
msg = EmailMessage()
msg['Subject'] = f"Daily Dispatch Report - {yesterday}"
msg['From'] = SENDER_EMAIL
msg['To'] = RECEIVER_EMAIL

msg.set_content(f"Hello,\n\nPlease find attached the Dispatch Report for {yesterday}.\n\nRegards,\nShree Sai Industries")

# Attach PDF
with open(pdf_path, "rb") as f:
    file_data = f.read()
    file_name = f.name
msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

# Connect to SMTP Server
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
    smtp.send_message(msg)

print(f"✅ Email sent successfully with {pdf_path}")
