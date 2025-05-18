import sqlite3
from datetime import datetime

conn = sqlite3.connect('orders.db')
c = conn.cursor()

# Clear old data (optional during testing)
c.execute('DELETE FROM orders')
c.execute('DELETE FROM order_products')

# --- Sample Orders by sales1 ---
orders = [
    ('sales1', 'Customer A', 'ORD1001', '2025-05-17', 0),
    ('sales1', 'Customer B', 'ORD1002', '2025-05-16', 1),
]

for created_by, customer_name, order_no, order_date, urgent_flag in orders:
    c.execute('INSERT INTO orders (created_by, customer_name, order_no, order_date, urgent_flag) VALUES (?, ?, ?, ?, ?)',
              (created_by, customer_name, order_no, order_date, urgent_flag))
    order_id = c.lastrowid
    c.execute('INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (order_id, 'Product X', 100, 'Kg', 5000, 60, 'Original'))
    c.execute('INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (order_id, 'Product Y', 50, 'Nos', 2500, 30, 'Original'))

# --- Sample Orders by sales2 ---
c.execute('INSERT INTO orders (created_by, customer_name, order_no, order_date, urgent_flag) VALUES (?, ?, ?, ?, ?)',
          ('sales2', 'Customer C', 'ORD1003', '2025-05-15', 0))
order_id = c.lastrowid
c.execute('INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
          (order_id, 'Product Z', 200, 'Kg', 10000, 120, 'Original'))

# --- Sample Dispatches by dispatch1 and dispatch2 ---
c.execute('INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status, modified_by, modified_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
          (1, 'Product X', 80, 'Kg', 0, 0, 'Dispatched', 'dispatch1', str(datetime.now())))

c.execute('INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status, modified_by, modified_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
          (2, 'Product X', 100, 'Kg', 0, 0, 'Dispatched', 'dispatch2', str(datetime.now())))

c.execute('INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status, modified_by, modified_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
          (3, 'Product Z', 150, 'Kg', 0, 0, 'Dispatched', 'dispatch1', str(datetime.now())))

conn.commit()
conn.close()
print("Sample data created successfully.")

