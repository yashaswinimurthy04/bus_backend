import sqlite3
import os

db_path = 'bus_tracking.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student;")
    print("Students Table Content:")
    for row in cursor.fetchall():
        print(row)
    
    cursor.execute("SELECT * FROM user WHERE username='bho';")
    print("\nUser 'bho' Content:")
    for row in cursor.fetchall():
        print(row)
    conn.close()
else:
    print(f"Database not found at {db_path}")
