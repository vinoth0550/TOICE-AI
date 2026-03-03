

# updated

# database.py

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["tce_database"]


prd_collection = db["oprds"]
task_collection = db["task_prds"]

task_chat_collection = db["task_chats"]

task_chat_collection.create_index("task_id")   # 



prd_collection.create_index("project_id")
task_collection.create_index("task_id")

def save_prd(data: dict):
    data["created_at"] = datetime.utcnow()
    result = prd_collection.insert_one(data)
    return str(result.inserted_id)

def save_task(data: dict):
    data["created_at"] = datetime.utcnow()
    result = task_collection.insert_one(data)
    return str(result.inserted_id)