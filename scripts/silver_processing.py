import pandas as pd
from db import get_mysql_engine

def run_silver():
    engine = get_mysql_engine()

    df = pd.read_sql(
        "SELECT * FROM credit_card_transactions",
        engine
    )

    df = df.drop_duplicates()
    df = df.dropna()

    print(f"[SILVER] DataFrame criado com {len(df)} registros")

    return df
