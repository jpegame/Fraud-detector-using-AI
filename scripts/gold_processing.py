from db import get_sqlite_engine

def run_gold(silver_df):
    engine = get_sqlite_engine()

    silver_df.to_sql(
        "credit_card_gold",
        engine,
        if_exists="replace",
        index=False
    )

    print("[GOLD] Dados persistidos em SQLite")
