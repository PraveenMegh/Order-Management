from fpdf import FPDF
import sqlite3
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

# --- Setup Database
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Today's Pending Orders
today = datetime.now().date()

c.execute('''
SELECT customer_name, product_name, quantity, unit, created_at
FROM orders
WHERE status = 'Pending'
ORDER BY created_at ASC
''')
pending_orders = c.fetchall()

# --- If there are pending orders
if pending_orders:

    # --- Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Pending Orders for Dispatch Today", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    for idx, (customer, product, qty, unit, created_at) in enumerate(pending_orders, start=1):
        pdf.cell(0, 10, f"{idx}. {customer} - {product} ({qty} {unit})", new_x="LMARGIN", new_y="NEXT")

    # --- Save PDF
    pdf_filename = f"pending_dispatch_{today}.pdf"
    pdf.output(pdf_filename)

    # --- Send Email
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    to_email = "info@shreesaisalt.com"

    subject = "Daily Dispatch Pending Orders Report"
    body = f"Please find attached the pending dispatch orders for {today.strftime('%d-%m-%Y')}."

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_filename, 'rb') as file:
        part = MIMEApplication(file.read(), Name=pdf_filename)
        part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    print("✅ Email sent successfully!")

else:
    print("❌ No pending orders found. Email not sent.")
