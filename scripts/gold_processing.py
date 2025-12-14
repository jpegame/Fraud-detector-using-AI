import os
import sqlite3

def run_gold(silver_df):
    os.makedirs("data/gold", exist_ok=True)
    
    conn = sqlite3.connect("data/gold/gold.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS credit_card_gold")

    columns = silver_df.columns
    col_defs = ", ".join([f"{col} TEXT" for col in columns])

    create_table_sql = f"""
    CREATE TABLE credit_card_gold (
        {col_defs}
    )
    """
    cursor.execute(create_table_sql)

    placeholders = ", ".join(["?"] * len(columns))
    insert_sql = f"""
    INSERT INTO credit_card_gold
    VALUES ({placeholders})
    """

    cursor.executemany(
        insert_sql,
        silver_df.astype(str).values.tolist()
    )

    conn.commit()
    conn.close()

    print(f"[GOLD] Dados persistidos em data/gold/gold.db ({len(silver_df)} registros)")

if __name__ == "__main__":
    import pandas as pd
    df = pd.read_pickle("data/silver/silver_data.pkl")
    run_gold(df)
