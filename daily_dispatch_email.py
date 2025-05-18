import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os

def send_email_with_pdf(pdf_file, sender, password, recipient, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_file, "rb") as f:
    part = MIMEApplication(f.read(), Name=pdf_file)
    part['Content-Disposition'] = f'attachment; filename="{pdf_file}"'
    msg.attach(part)

    server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

    print(f"Email sent to {recipient} with {pdf_file}")

if __name__ == "__main__":
    from dispatch_report_pdf import generate_dispatch_pdf
    import os

    pdf_file = generate_dispatch_pdf()

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    recipient = os.getenv("RECIPIENT")

    if pdf_file:
        # If dispatch report exists, send it
        send_email_with_pdf(
            pdf_file=pdf_file,
            sender=sender,
            password=password,
            recipient=recipient,
            subject="Daily Dispatch Summary",
            body="""Hello,

Please find attached today's dispatch summary report.

Regards,
Shree Sai Industries
"""
        )
    else:
       # If no dispatches, send a no-dispatch email
       send_email_with_pdf(
           pdf_file=None,
           sender=sender,
           password=password,
           recipient=recipient,
           subject="No Dispatch Today",
           body="""Hello,

There are no dispatches for today or today is a holiday.

Regards,
Shree Sai Industries
"""
        )

