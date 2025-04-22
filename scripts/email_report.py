import os
import pandas as pd
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Create report PDF
def generate_pdf(filepath, data):
    c = canvas.Canvas(str(filepath), pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Shree Sai Industries - Daily Dispatch Summary")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    y = 750
    c.setFont("Helvetica", 11)
    for i, row in enumerate(data.itertuples(index=False), 1):
        text = f"{i}. {row.product_name} - {row.order_quantity} units"
        c.drawString(60, y, text)
        y -= 18
        if y < 100:
            c.showPage()
            y = 800
    c.save()

# Simulated data
data = pd.DataFrame({
    'product_name': ['Salt', 'Powder', 'Crystal', 'Refined'],
    'order_quantity': [120, 80, 60, 45]
})

# File paths
report_path = Path("reports") / f"Dispatch_Summary_{datetime.now().strftime('%Y-%m-%d')}.pdf"
report_path.parent.mkdir(exist_ok=True)
generate_pdf(report_path, data)

# Email config
sender = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASSWORD")
receiver = "info@shreesaisalt.com"

msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = receiver
msg['Subject'] = f"🧾 Daily Dispatch Summary - {datetime.now().strftime('%Y-%m-%d')}"

msg.attach(MIMEText("Attached is the daily dispatch summary PDF.", "plain"))
with open(report_path, "rb") as f:
    part = MIMEApplication(f.read(), Name=report_path.name)
    part['Content-Disposition'] = f'attachment; filename="{report_path.name}"'
    msg.attach(part)

context = ssl.create_default_context()
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls(context=context)
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
