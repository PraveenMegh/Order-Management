import sqlite3

# Connect to your database
conn = sqlite3.connect('data/orders.db')
c = conn.cursor()

# Add columns if not already present
try:
    c.execute("ALTER TABLE orders ADD COLUMN price REAL")
except:
    pass

try:
    c.execute("ALTER TABLE orders ADD COLUMN currency TEXT")
except:
    pass

try:
    c.execute("ALTER TABLE orders ADD COLUMN unit_type TEXT")
except:
    pass

try:
    c.execute("ALTER TABLE orders ADD COLUMN dispatched_by TEXT")
except:
    pass

conn.commit()
conn.close()

print("✅ Database updated successfully!")
