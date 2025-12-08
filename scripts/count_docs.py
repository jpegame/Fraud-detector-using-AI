from pymongo import MongoClient

URI = "mongodb://localhost:27017"  # ou sua URI do Atlas, se estiver usando Atlas

client = MongoClient(URI)
db = client["meuBdTeste"]
collection = db["transacoes"]

total = collection.count_documents({})
print("Total de documentos:", total)
