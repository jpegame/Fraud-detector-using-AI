import csv
import time
import mysql.connector

MYSQL_HOST = "localhost"          # porque você mapeou -p 3306:3306
MYSQL_PASSWORD = "root123"        # mesma senha do MYSQL_ROOT_PASSWORD
MYSQL_DATABASE = "creditdb"       # mesmo nome do MYSQL_DATABASE
CSV_PATH = "data/credit-card1.csv"  # caminho do seu CSV na VM

RETRY_COUNT = 10
RETRY_DELAY = 3

print("Starting importer using direct config...")

for i in range(RETRY_COUNT):
    print(f"Trying: Host={MYSQL_HOST}, Password={MYSQL_PASSWORD}, Database={MYSQL_DATABASE}")
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user="root",
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        break
    except Exception as e:
        print("Connection failed:", e)
        time.sleep(RETRY_DELAY)
else:
    raise Exception("Database connection failed.")
