from pymongo import MongoClient
import json

URI = "mongodb+srv://Aluno:aluno123@clusterlineu.b5nhvya.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"

client = MongoClient(URI, tls=True, tlsAllowInvalidCertificates=True)

db = client["meuBdTeste"]
collection = db["transacoes"]

with open("../data/credit-card2.json", "r") as f:
    docs = json.load(f)

result = collection.insert_many(docs)
print(f"Inseridos {len(result.inserted_ids)} documentos")
