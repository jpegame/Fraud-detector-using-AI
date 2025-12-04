import os
import csv
import time
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

CSV_PATH = os.getenv("MYSQL_CSV_FILE")
RETRY_COUNT = int(os.getenv("DB_RETRY_COUNT", 10))
RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", 3))

print("Starting importer using environment config...")

for i in range(RETRY_COUNT):
    print(f"Variables: Host={MYSQL_HOST}, Password={MYSQL_PASSWORD} Database={MYSQL_DATABASE}")
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        break
    except:
        time.sleep(RETRY_DELAY)
else:
    raise Exception("Database connection failed.")

with open(CSV_PATH, "r") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames
    
cursor = conn.cursor()

table_name = "credit-card"
column_definitions = ", ".join([f"`{col}` FLOAT" for col in columns])
sql_create = f"""
CREATE TABLE IF NOT EXISTS `{table_name}` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    {column_definitions}
);
"""

cursor.execute(sql_create)

insert_query = f"""
INSERT INTO `{table_name}` ({", ".join([f"`{col}`" for col in columns])})
VALUES ({", ".join(['%s'] * len(columns))})
"""

with open(CSV_PATH, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute(insert_query, list(row.values()))

conn.commit()
cursor.close()
conn.close()

print("✅ Import completed successfully!")
