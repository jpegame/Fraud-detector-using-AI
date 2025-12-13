from sqlalchemy import create_engine

sqlite_engine = create_engine("sqlite:///data/gold.db")

agg_df.to_sql(
    "credit_card_gold",
    sqlite_engine,
    if_exists="replace",
    index=False
)

print("Gold Layer salva em SQLite")
