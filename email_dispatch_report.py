import sqlite3
from datetime import datetime, timedelta
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os

# Email credentials
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Connect to database
conn = sqlite3.connect('data/orders.db')
c = conn.cursor()

# Get today and yesterday
today = datetime.now().date()
yesterday = today - timedelta(days=1)

# Fetch pending orders
pending_orders = c.execute("""
    SELECT id, customer_name, product_name, quantity, urgent, created_at
    FROM orders
    WHERE status = 'Pending'
    ORDER BY created_at ASC
""").fetchall()

# Fetch dispatched yesterday orders
dispatched_orders = c.execute("""
    SELECT id, customer_name, product_name, dispatched_quantity, dispatched_at
    FROM orders
    WHERE status = 'Dispatched' AND DATE(dispatched_at) = ?
    ORDER BY dispatched_at ASC
""", (yesterday,)).fetchall()

# If no pending and no dispatched, skip sending
if not pending_orders and not dispatched_orders:
    print("❌ No pending or dispatched orders found. Email not sent.")
    exit()

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Pending Orders for Dispatch Today", ln=True)

pdf.ln(5)

# Pending orders section
if pending_orders:
    pdf.set_font("Arial", size=12)
    for order in pending_orders:
        id, customer, product, qty, urgent, created_at = order
        created_at_fmt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")
        urgent_mark = "✅ Urgent" if urgent else "Normal"
        
        if urgent:
            pdf.set_text_color(255, 0, 0)  # Red color for urgent
        else:
            pdf.set_text_color(0, 0, 0)
        
        pdf.cell(0, 10, f"#{id} | {customer} | {product} | {qty} | {urgent_mark} | {created_at_fmt}", ln=True)

pdf.ln(10)
pdf.set_font("Arial", "B", 16)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 10, "✅ Orders Dispatched Yesterday", ln=True)

pdf.ln(5)

# Dispatched orders section
if dispatched_orders:
    pdf.set_font("Arial", size=12)
    for order in dispatched_orders:
        id, customer, product, dispatched_qty, dispatched_at = order
        dispatched_at_fmt = datetime.strptime(dispatched_at, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %I:%M %p")
        pdf.cell(0, 10, f"#{id} | {customer} | {product} | {dispatched_qty} | {dispatched_at_fmt}", ln=True)

# Save PDF
pdf_output_path = "dispatch_report.pdf"
pdf.output(pdf_output_path)

# Prepare Email
msg = EmailMessage()
msg["Subject"] = "📦 Daily Dispatch Report - Shree Sai Industries"
msg["From"] = EMAIL_USER
msg["To"] = "info@shreesaisalt.com"
msg.set_content("Hello Team,\n\nAttached is the dispatch plan for today along with yesterday's completed dispatch summary.\n\nRegards,\nShree Sai Industries System")

# Attach PDF
with open(pdf_output_path, "rb") as f:
    file_data = f.read()
    file_name = f"Dispatch_Report_{today.strftime('%d-%m-%Y')}.pdf"
    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

# Send Email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_USER, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("✅ Dispatch report email sent successfully!")
