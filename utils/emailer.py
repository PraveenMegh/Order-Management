import streamlit as st
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

def send_dispatch_email():
    sender = "praveeenmeghkrish@gmail.com"
    receiver = "info@shreesaisalt.com"
    password = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEMultipart()
    msg['Subject'] = f"Daily Dispatch Summary - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = sender
    msg['To'] = receiver

    msg.attach(MIMEText("Attached is today's dispatch summary PDF."))

    with open("data/Dispatch_Summary_Today.pdf", "rb") as f:
        part = MIMEApplication(f.read(), Name="Dispatch_Summary.pdf")
        part['Content-Disposition'] = 'attachment; filename=\"Dispatch_Summary.pdf\"'
        msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=ssl.create_default_context())
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())