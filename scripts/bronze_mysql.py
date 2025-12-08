import json
import mysql.connector

# Ajuste esses dados:
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="SENHA_AQUI",
    database="NOME_DO_BANCO"
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM NOME_DA_TABELA")
rows = cursor.fetchall()

with open("../bronze/mysql_credit_card1.txt", "w", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row) + "\n")

cursor.close()
conn.close()

print(f"Gravou {len(rows)} linhas em bronze/mysql_credit_card1.txt")
