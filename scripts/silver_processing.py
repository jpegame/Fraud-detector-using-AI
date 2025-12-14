import os
import pandas as pd

def run_silver():
    os.makedirs("data/silver", exist_ok=True)
    
    df1 = pd.read_csv("data/bronze/bronze-credit-card1.txt", sep="\t")
    df2 = pd.read_csv("data/bronze/bronze-credit-card2.txt", sep="\t")
    
    df = pd.concat([df1, df2], ignore_index=True)
    
    df = df.drop_duplicates()
    df = df.dropna()
    
    if "id" in df.columns:
        df = df.drop("id", axis=1)
    
    silver_path = "data/silver/silver_data.pkl"
    df.to_pickle(silver_path)
    
    print(f"[SILVER] DataFrame salvo em {silver_path} ({len(df)} registros)")
    return df

if __name__ == "__main__":
    run_silver()
