from fpdf import FPDF
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pytz
import snowflake.connector
import sys

# --- Load environment variables ---
load_dotenv(dotenv_path='./.env')

EMAIL_USER = os.getenv("EMAIL_USER")  # Gmail ID
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Gmail App Password
TO_EMAIL = "info@shreesaisalt.com"
BCC_EMAIL = "pkc05@yahoo.com"

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")

# --- Time Handling ---
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
today_str = now_ist.strftime('%Y-%m-%d')
weekday = now_ist.weekday()

try:
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE
    )
    cur = conn.cursor()
    print("✅ Connected to Snowflake")

    # --- Holiday Check ---
    cur.execute(f"SELECT COUNT(*) FROM holidays WHERE holiday_date = '{today_str}'")
    if cur.fetchone()[0] > 0:
        print(f"❌ Today ({today_str}) is a holiday. No dispatch report sent.")
        sys.exit(0)

    # --- Dates to include ---
    if weekday == 6:  # Sunday
        report_dates = [(now_ist - timedelta(days=1)).strftime('%Y-%m-%d')]
    elif weekday == 0:  # Monday
        report_dates = [
            (now_ist - timedelta(days=1)).strftime('%Y-%m-%d'),
            today_str
        ]
    else:
        report_dates = [today_str]

    report_dates_sql = "', '".join(report_dates)
    print(f"📊 Generating dispatch report for: {report_dates_sql}")

    # --- Fetch Dispatched Orders ---
    query = f"""
    SELECT 
        o.customer_name,
        oi.product_name,
        oi.ordered_qty,
        oi.unit,
        oi.dispatched_qty,
        oi.dispatched_at,
        oi.dispatched_by
    FROM {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.order_items oi
    JOIN {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.orders o
        ON oi.order_id = o.id
    WHERE oi.status = 'Dispatched'
    AND CAST(oi.dispatched_at AS DATE) IN ('{report_dates_sql}')
    ORDER BY oi.dispatched_at ASC
    """

    cur.execute(query)
    dispatched_orders = cur.fetchall()

    if dispatched_orders:
        # --- Generate PDF Report ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Dispatch Summary ({', '.join(report_dates)})", ln=True)
        pdf.ln(5)

        headers = ["#", "Customer", "Product", "Ordered Qty", "Unit", "Dispatched Qty", "By"]
        col_widths = [10, 30, 40, 25, 20, 25, 40]

        pdf.set_font("Arial", size=10)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1)
        pdf.ln()

        for idx, row in enumerate(dispatched_orders, start=1):
            customer, product, ordered_qty, unit, dispatched_qty, dispatched_at, dispatched_by = row
            values = [str(idx), customer, product, str(ordered_qty), unit, str(dispatched_qty), dispatched_by]
            for i, val in enumerate(values):
                pdf.cell(col_widths[i], 10, str(val), border=1)
            pdf.ln()

        # --- Save PDF ---
        pdf_filename = f"dispatch_summary_{today_str}.pdf"
        pdf.output(pdf_filename)
    else:
        print("✅ No dispatches today. Sending info email.")

    # --- Compose Email ---
    subject = f"Dispatch Summary - {', '.join(report_dates)}"
    body = f"""
Dear Team,

Please find attached the dispatch summary for {', '.join(report_dates)}.

- Urgent orders (if any) were prioritized.
- FIFO order followed for normal dispatches.
- This is an automated daily report.

Regards,
Shree Sai Industries
"""

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TO_EMAIL
    msg['Bcc'] = BCC_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # --- Attach PDF only if exists ---
    if dispatched_orders:
        with open(pdf_filename, 'rb') as file:
            part = MIMEApplication(file.read(), Name=pdf_filename)
            part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            msg.attach(part)

    # --- Send Email ---
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    print("✅ Dispatch report email sent successfully.")

    # After email sent successfully:
    print("✅ Dispatch summary email sent!")
    sys.exit(0)  # ✅ Explicitly tell GitHub Actions → SUCCESS exit

except Exception as e:
    print(f"❌ Dispatch Report Failed: {e}")
    sys.exit(1)

finally:
    try:
        cur.close()
        conn.close()
    except:
        pass

sys.exit(0)
