import sqlite3

db_path = "hargatani.db"
conn = sqlite3.connect(db_path)
try:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prices WHERE price <= 0 OR price IS NULL")
    count = cursor.rowcount
    conn.commit()
    print(f"Deleted {count} rows")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
