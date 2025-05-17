import sqlite3

def add_column_if_not_exists(cursor, table_name, column_name, column_type):
    # Check if column exists
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"✅ Added column: {column_name} to table: {table_name}")
    else:
        print(f"ℹ️ Column already exists: {column_name}")

# --- Connect to database ---
conn = sqlite3.connect('data/orders.db')
c = conn.cursor()

# --- Update orders table safely ---
add_column_if_not_exists(c, 'orders', 'price', 'REAL')
add_column_if_not_exists(c, 'orders', 'currency', 'TEXT')
add_column_if_not_exists(c, 'orders', 'unit_type', 'TEXT')
add_column_if_not_exists(c, 'orders', 'dispatched_by', 'TEXT')

conn.commit()
conn.close()

print("✅ Database update script completed successfully!")
