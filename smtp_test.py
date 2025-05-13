import smtplib
from email.mime.text import MIMEText
import os

EMAIL_USER = os.getenv("EMAIL_USER")  # Your Gmail ID
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Gmail App Password
TO_EMAIL = "info@shreesaisalt.com"

subject = "Test Email - Dispatch SMTP"
body = "✅ This is a test email from SMTP Gmail setup."

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = EMAIL_USER
msg['To'] = TO_EMAIL

try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
    print("✅ Test email sent successfully!")
except Exception as e:
    print(f"❌ Failed to send test email: {e}")

