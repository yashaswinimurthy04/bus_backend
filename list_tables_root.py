import sqlite3
import os

db_path = 'bus_tracking.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(table[0])
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
else:
    print(f"Database not found at {db_path}")
