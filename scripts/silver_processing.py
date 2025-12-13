import pandas as pd
from db import get_mysql_engine
from sqlalchemy import text

def run_silver():
    engine = get_mysql_engine()

    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM credit_card_transactions"))
        rows = result.fetchall()
        columns = result.keys()

    df = pd.DataFrame(rows, columns=columns)

    df = df.drop_duplicates()
    df = df.dropna()

    print(f"[SILVER] DataFrame criado com {len(df)} registros")
    return df
