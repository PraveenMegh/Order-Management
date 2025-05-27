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

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

    print(f"Email sent to {recipient} with {pdf_file}")

if __name__ == "__main__":
    from dispatch_report_pdf import generate_dispatch_pdf
    import os

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    recipient = os.getenv("RECIPIENT")

    pdf_file = generate_dispatch_pdf()

    if pdf_file:
        # If dispatch report exists, send it with attachment
        send_email_with_pdf(
            pdf_file=pdf_file,
            sender=sender,
            password=password,
            recipient=recipient,
            subject="✅ Daily Dispatch Summary",
            body="DearSir/Madam,\n\nPlease find attached today's dispatch summary report.\n\nRegards,\nTeam Admin,\nShree Sai Salt"
        )
    else:
        # If no dispatch, send text-only email
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText("Dear Sir/Madam,\n\n📭 No dispatches for today.\n\nRegards,\nAdmin Team,\nShree Sai Industries")
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = "📭 No Dispatch Today"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"📭 Email sent to {recipient} stating no dispatch today.")


