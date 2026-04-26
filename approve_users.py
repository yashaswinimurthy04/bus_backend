import sqlite3

def approve_all():
    conn = sqlite3.connect('bus_tracking.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET approved = 1")
    conn.commit()
    conn.close()
    print("All users approved")

if __name__ == "__main__":
    approve_all()
