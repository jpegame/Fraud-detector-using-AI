import os
import json
import pandas as pd
from pymongo import MongoClient

CSV_FILE = os.getenv("MONGO_CSV_FILE", "/app/data/credit-card2.csv")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "creditcard")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "transactions")

df = pd.read_csv(CSV_FILE)

records = df.to_dict(orient="records")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

if records:
    collection.insert_many(records)
    print(f"{len(records)} documentos inseridos no MongoDB.")
else:
    print("Nenhum dado para inserir.")
