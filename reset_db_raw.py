import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def reset_raw():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Dropping all tables with CASCADE...")
    cur.execute("DROP TABLE IF EXISTS student_profile CASCADE;")
    cur.execute("DROP TABLE IF EXISTS parent_profile CASCADE;")
    cur.execute("DROP TABLE IF EXISTS driver_profile CASCADE;")
    cur.execute("DROP TABLE IF EXISTS student CASCADE;")
    cur.execute("DROP TABLE IF EXISTS parent CASCADE;")
    cur.execute("DROP TABLE IF EXISTS driver CASCADE;")
    cur.execute("DROP TABLE IF EXISTS stop CASCADE;")
    cur.execute("DROP TABLE IF EXISTS notification CASCADE;")
    cur.execute("DROP TABLE IF EXISTS bus CASCADE;")
    cur.execute("DROP TABLE IF EXISTS \"user\" CASCADE;")
    
    print("Done.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    reset_raw()
