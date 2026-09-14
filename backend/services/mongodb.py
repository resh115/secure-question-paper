from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is missing. Create .env from .env.example.")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DATABASE_NAME]

users_collection = db["users"]
papers_collection = db["question_papers"]
shares_collection = db["secret_shares"]
audit_collection = db["audit_logs"]
exams_collection = db["examinations"]

def ping():
    client.admin.command("ping")
    return True
