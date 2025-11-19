from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URI")
print("URI Loaded:", uri)

client = MongoClient(uri)
print(client.list_database_names())
