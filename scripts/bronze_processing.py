import os
import pandas as pd
from pymongo import MongoClient
from db import get_mysql_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

def run_bronze():
    os.makedirs("data/bronze", exist_ok=True)
    
    engine = get_mysql_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM `credit-card`"))
        rows = result.fetchall()
        columns = result.keys()
    df_mysql = pd.DataFrame(rows, columns=columns)
    
    bronze_path1 = "data/bronze/bronze-credit-card1.txt"
    df_mysql.to_csv(bronze_path1, sep="\t", index=False)
    print(f"[BRONZE] MySQL -> {bronze_path1} ({len(df_mysql)} registros)")
    
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "creditcard")
    mongo_collection = os.getenv("MONGO_COLLECTION", "transactions")
    
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    collection = db[mongo_collection]
    
    docs = list(collection.find({}, {"_id": 0}))
    df_mongo = pd.DataFrame(docs)
    
    bronze_path2 = "data/bronze/bronze-credit-card2.txt"
    df_mongo.to_csv(bronze_path2, sep="\t", index=False)
    print(f"[BRONZE] MongoDB -> {bronze_path2} ({len(df_mongo)} registros)")
    
    return bronze_path1, bronze_path2

if __name__ == "__main__":
    run_bronze()
