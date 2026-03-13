
# phase 2


# database.py

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["TOICE"]


prd_collection = db["oprds"]
task_collection = db["task_prds"]
task_chat_collection = db["task_chat_messages"]
task_report_collection = db["task_reports"]



###
ai_usage_collection = db["ai_usage_logs"]
###