from pymongo import MongoClient
from pprint import pprint

URI = "mongodb://localhost:27017"  # ou sua URI do Atlas, se estiver usando Atlas

client = MongoClient(URI)
db = client["meuBdTeste"]
collection = db["transacoes"]

doc = collection.find_one()
pprint(doc)
