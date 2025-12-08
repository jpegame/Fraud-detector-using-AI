from pymongo import MongoClient

URI = "mongodb+srv://Aluno:aluno123@clusterlineu.b5nhvya.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(URI)
print(client.list_database_names())
