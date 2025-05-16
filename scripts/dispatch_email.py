import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import pytz
import snowflake.connector
from fpdf import FPDF
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib
from pathlib import Path

# --- Load .env dynamically from project root ---
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ .env loaded successfully.")
else:
    print("❌ .env file not found at expected location:", env_path)
    sys.exit(1)

# --- Read Snowflake credentials from env ---
sf_user = os.getenv('SNOWFLAKE_USER')
sf_password = os.getenv('SNOWFLAKE_PASSWORD')
sf_account = os.getenv('SNOWFLAKE_ACCOUNT')
sf_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
sf_database = os.getenv('SNOWFLAKE_DATABASE')
sf_schema = os.getenv('SNOWFLAKE_SCHEMA')
sf_role = os.getenv('SNOWFLAKE_ROLE')

# --- Read email credentials ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = "info@shreesaisalt.com"
BCC_EMAIL = "pkc05@yahoo.com"

# --- Timezone Handling ---
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
today_str = now_ist.strftime('%Y-%m-%d')

# --- Debug info ---
print(f"🔍 DEBUG INFO:")
print(f"SNOWFLAKE_ACCOUNT: {sf_account}")
print(f"SNOWFLAKE_USER: {sf_user}")
print(f"SNOWFLAKE_PASSWORD: {'SET' if sf_password else 'MISSING'}")
print(f"SNOWFLAKE_WAREHOUSE: {sf_warehouse}")
print(f"SNOWFLAKE_DATABASE: {sf_database}")
print(f"SNOWFLAKE_SCHEMA: {sf_schema}")
print(f"SNOWFLAKE_ROLE: {sf_role}")

# --- Connect to Snowflake ---
try:
    conn = snowflake.connector.connect(
        user=sf_user,
        password=sf_password,
        account=sf_account,
        warehouse=sf_warehouse,
        database=sf_database,
        schema=sf_schema,
        role=sf_role
    )
    print("✅ Connected to Snowflake")
    cur = conn.cursor()

    # --- Check if today is holiday ---
    query = f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.HOLIDAYS WHERE holiday_date = %s"
    cur.execute(query, (today_str,))
    if cur.fetchone()[0] > 0:
        print(f"❌ Today ({today_str}) is a holiday. No dispatch report sent.")
        sys.exit(0)

    # --- Fetch dispatched orders ---
    query = f"""
        SELECT
            o.customer_name,
            oi.product_name,
            oi.ordered_qty,
            oi.unit,
            oi.dispatched_qty,
            oi.dispatched_at,
            oi.dispatched_by
        FROM {sf_database}.{sf_schema}.ORDER_ITEMS oi
        JOIN {sf_database}.{sf_schema}.ORDERS o
            ON oi.order_id = o.id
        WHERE oi.status = 'Dispatched'
        AND CAST(oi.dispatched_at AS DATE) = %s
        ORDER BY oi.dispatched_at ASC
    """
    cur.execute(query, (today_str,))
    dispatched_orders = cur.fetchall()

    if not dispatched_orders:
        print(f"✅ No dispatched orders to report for {today_str}.")
        sys.exit(0)

    # --- Generate PDF ---
    pdf_filename = f"dispatch_summary_{today_str}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Dispatch Summary ({today_str})", ln=True)
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

    pdf.output(pdf_filename)
    print(f"✅ PDF report generated: {pdf_filename}")

    # --- Compose Email ---
    subject = f"Dispatch Summary - {today_str}"
    body = f"""
Dear Team,

Please find attached the dispatch summary for {today_str}.

Regards,
Shree Sai Industries
"""

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TO_EMAIL
    msg['Bcc'] = BCC_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with open(pdf_filename, 'rb') as file:
        part = MIMEApplication(file.read(), Name=pdf_filename)
        part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        msg.attach(part)

    # --- Send Email ---
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    print("✅ Dispatch summary email sent successfully.")

except Exception as e:
    print(f"❌ Dispatch Report Failed: {e}")
    sys.exit(1)

finally:
    try:
        cur.close()
        conn.close()
    except:
        pass
