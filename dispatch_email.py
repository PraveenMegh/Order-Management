from fpdf import FPDF
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pytz
import snowflake.connector

# --- Environment Variables from GitHub Actions Secrets ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = "info@shreesaisalt.com"

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")

# --- Timezone Handling ---
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
today_str = now_ist.strftime('%Y-%m-%d')
weekday = now_ist.weekday()

# --- Connect to Snowflake ---
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
    holiday_count = cur.fetchone()[0]

    if holiday_count > 0:
        print(f"❌ Today ({today_str}) is a holiday. No dispatch email sent.")
        exit()

    # --- Report Dates Logic ---
    if weekday == 6:  # Sunday ➔ show Saturday
        report_dates = [(now_ist - timedelta(days=1)).strftime('%Y-%m-%d')]
    elif weekday == 0:  # Monday ➔ show Sunday + Monday
        report_dates = [
            (now_ist - timedelta(days=1)).strftime('%Y-%m-%d'),
            today_str
        ]
    else:
        report_dates = [today_str]

    # --- Fetch Dispatched Orders ---
    report_dates_sql = "', '".join(report_dates)
    print(f"📊 Fetching dispatched orders for: {report_dates_sql}")

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
        # --- Generate PDF ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Dispatch Summary ({', '.join(report_dates)})", ln=True)
        pdf.ln(5)

        headers = ["#", "Customer", "Product", "Ordered Qty", "Unit", "Dispatched Qty", "Dispatched By"]
        col_widths = [10, 30, 40, 25, 20, 25, 40]

        pdf.set_font("Arial", size=10)
        # Header Row
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1)
        pdf.ln()

        # Data Rows
        for idx, row in enumerate(dispatched_orders, start=1):
            customer, product, ordered_qty, unit, dispatched_qty, dispatched_at, dispatched_by = row
            values = [str(idx), customer, product, str(ordered_qty), unit, str(dispatched_qty), dispatched_by]
            for i, val in enumerate(values):
                pdf.cell(col_widths[i], 10, str(val), border=1)
            pdf.ln()

        # Save PDF
        pdf_filename = f"dispatch_summary_{today_str}.pdf"
        pdf.output(pdf_filename)

        # --- Send Email ---
        subject = f"Dispatch Summary - {', '.join(report_dates)}"
       body = f"""
        Dear Team,

       📦 Please find attached the **Dispatch Summary Report** for {', '.join(report_dates)}.

        🔑 **Key Highlights**:
        - Urgent orders (if any) were dispatched on priority.
        - Regular dispatches followed the FIFO (First-In-First-Out) basis.
        - This is an automated daily report from the Shree Sai Industries order management system.

        ✅ Kindly ensure all pending orders are addressed as per the dispatch schedule.

        Thank you,  
        **Shree Sai Industries**
    """


        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = TO_EMAIL
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

        print("✅ Dispatch summary email sent!")

    else:
        print(f"✅ No dispatched orders to report for {', '.join(report_dates)}.")

except snowflake.connector.errors.DatabaseError as e:
    print("❌ Snowflake connection error:", e)

finally:
    try:
        cur.close()
        conn.close()
    except:
        pass
