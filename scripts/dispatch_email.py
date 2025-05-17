import sqlite3
from datetime import datetime
from fpdf import FPDF
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.smtp_utils import send_email  # ✅ Using reusable SMTP module

# --- Today's Date ---
today_str = datetime.now().strftime('%Y-%m-%d')

# --- Connect to SQLite ---
conn = sqlite3.connect('data/orders.db', check_same_thread=False)
c = conn.cursor()

# --- Fetch today's dispatched orders ---
c.execute("""
    SELECT 
        o.customer_name,
        oi.product_name,
        oi.ordered_qty,
        oi.unit,
        oi.dispatched_qty,
        oi.dispatched_at,
        oi.dispatched_by
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.id
    WHERE oi.status = 'Dispatched'
    AND DATE(oi.dispatched_at) = ?
    ORDER BY oi.dispatched_at ASC
""", (today_str,))
dispatched_orders = c.fetchall()

if not dispatched_orders:
    print(f"✅ No dispatched orders to report for {today_str}.")
    exit(0)

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

# --- Compose and Send Email ---
subject = f"Dispatch Summary - {today_str}"
body = f"""
Dear Team,

Please find attached the dispatch summary for {today_str}.

Regards,
Shree Sai Industries
"""

# --- Call reusable email function ---
send_email(subject, body, "info@shreesaisalt.com", attachment=pdf_filename)

conn.close()
