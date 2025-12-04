import os
import csv
import time
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

CSV_FILE = os.getenv("CSV_FILE")
RETRY_COUNT = int(os.getenv("DB_RETRY_COUNT", 10))
RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", 3))

print("Starting importer using environment config...")

for attempt in range(RETRY_COUNT):
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        print("Connected to database.")
        break
    except Exception:
        print(f"DB not ready, retrying ({attempt+1}/{RETRY_COUNT})...")
        time.sleep(RETRY_DELAY)
else:
    raise Exception("Could not connect to MySQL after multiple retries.")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    department VARCHAR(100)
);
""")

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

with open(CSV_FILE) as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute(
            "INSERT INTO employees (name, age, department) VALUES (%s, %s, %s)",
            (row["name"], row["age"], row["department"])
        )

conn.commit()
cursor.close()
conn.close()

print("CSV import completed successfully!")
