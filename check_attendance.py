import sqlite3
import os

db_path = os.path.join('instance', 'bus_tracking.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT username, is_absent FROM student")
    rows = cursor.fetchall()
    print("Student Attendance Status:")
    for row in rows:
        print(f"User: {row[0]}, Is Absent: {row[1]}")
    conn.close()
else:
    print(f"Database not found at {db_path}")
