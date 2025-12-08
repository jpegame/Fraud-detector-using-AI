from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Usar MongoDB local da VM
URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE = os.getenv('MONGO_DATABASE', 'frauddb')
COLLECTION = os.getenv('MONGO_COLLECTION', 'transactions')

print(f"Conectando ao MongoDB: {URI}")
client = MongoClient(URI)

db = client[DATABASE]
collection = db[COLLECTION]

# Caminho correto do arquivo JSON
json_file = os.path.join('data', 'credit-card2.json')

print(f"Carregando arquivo: {json_file}")
with open(json_file, "r") as f:
    docs = json.load(f)

print(f"Inserindo {len(docs)} documentos no MongoDB...")
result = collection.insert_many(docs)
print(f"✅ Inseridos {len(result.inserted_ids)} documentos no MongoDB!")

# Validar
count = collection.count_documents({})
print(f"✅ Total de documentos na collection: {count}")
