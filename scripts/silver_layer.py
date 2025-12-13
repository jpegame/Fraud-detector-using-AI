import pandas as pd
import os
from sqlalchemy import create_engine

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_DB = os.getenv("MYSQL_DATABASE")
MYSQL_USER = "root"
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

engine = create_engine(
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)

query = "SELECT * FROM credit_card_transactions"
df = pd.read_sql(query, engine)

df = df.drop_duplicates()

df = df.dropna()

silver_df = df[
    [
        "amount",
        "transaction_type",
        "merchant",
        "timestamp"
    ]
]

# Exemplo de agregação
agg_df = silver_df.groupby("transaction_type")["amount"].sum().reset_index()

print("Silver DataFrame criado com sucesso")
