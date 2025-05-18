import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

def generate_dispatch_pdf(filename='dispatch_report.pdf'):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()

    # Fetch today's dispatched orders
    today = datetime.today().strftime('%Y-%m-%d')
    c.execute('''
        SELECT o.order_no, o.customer_name, p.product_name, p.quantity, p.unit, p.status, p.modified_by, p.modified_date
        FROM orders o
        JOIN order_products p ON o.order_id = p.order_id
        WHERE p.status = 'Dispatched'
        AND DATE(p.modified_date) = ?
        ORDER BY o.order_no ASC
    ''', (today,))
    data = c.fetchall()

    if not data:
        print("No dispatched orders for today.")
        return None

    df = pd.DataFrame(data, columns=['Order No', 'Customer Name', 'Product Name', 'Quantity', 'Unit', 'Status', 'Dispatched By', 'Dispatched Date'])

    # Generate PDF using FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"Dispatch Summary - {today}", ln=True, align='C')
    pdf.set_font("Arial", '', 10)

    col_width = pdf.w / 7
    row_height = 8
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)

    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)

    pdf.output(filename)
    print(f"PDF generated: {filename}")
    return filename

# Optional test run
if __name__ == "__main__":
    generate_dispatch_pdf()
