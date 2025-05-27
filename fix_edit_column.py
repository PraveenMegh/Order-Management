import sqlite3

conn = sqlite3.connect("orders.db")
c = conn.cursor()

# Try adding the column (ignore if already exists)
try:
    c.execute("ALTER TABLE order_products ADD COLUMN edit_count INTEGER DEFAULT 0")
    print("✅ Column 'edit_count' added.")
except sqlite3.OperationalError as e:
    print("⚠️ Column already exists or another issue:", e)

conn.commit()
conn.close()
