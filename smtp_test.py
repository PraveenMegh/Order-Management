import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# --- Load .env ---
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = "info@shreesaisalt.com"

# --- Safety check ---
if not EMAIL_USER or not EMAIL_PASSWORD:
    print("❌ EMAIL_USER or EMAIL_PASSWORD not set. Please check your .env file.")
    exit(1)

subject = "Test Email - Direct SMTP"
body = "✅ This is a test email using raw SMTP code."

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = EMAIL_USER
msg['To'] = TO_EMAIL

try:
    with smtplib.SMTP('smtp.mail.yahoo.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
    print(f"✅ Test email sent successfully to {TO_EMAIL}")
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ SMTP Authentication Error: {e}")
except Exception as e:
    print(f"❌ Failed to send test email: {e}")
