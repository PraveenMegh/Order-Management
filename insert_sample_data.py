import sqlite3

conn = sqlite3.connect("data/orders.db")
cursor = conn.cursor()

sample_orders = [
    ("Salt", 50, "2025-04-20"),
    ("Salt", 20, "2025-04-21"),
    ("Powder", 30, "2025-04-20"),
    ("Crystal", 10, "2025-04-19"),
    ("Refined", 15, "2025-04-20")
]

cursor.executemany("INSERT INTO orders (product_name, order_quantity, order_date) VALUES (?, ?, ?)", sample_orders)

conn.commit()
conn.close()
print("✅ Sample orders inserted!")