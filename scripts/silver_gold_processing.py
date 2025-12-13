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

df = pd.read_sql("SELECT * FROM credit_card_transactions", engine)

# =========================
# TRANSFORMAÇÕES (SILVER)
# =========================
df = df.drop_duplicates()
df = df.dropna()

silver_df = df.copy()

print(f"Silver DataFrame criado com {len(silver_df)} registros")

# =========================
# GOLD (SQLite)
# =========================
sqlite_engine = create_engine("sqlite:///data/gold.db")

silver_df.to_sql(
    "credit_card_gold",
    sqlite_engine,
    if_exists="replace",
    index=False
)

print("Gold Layer salva em SQLite")
