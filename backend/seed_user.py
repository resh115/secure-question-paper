"""
Run once after Firebase Authentication is configured.

Usage:
    python seed_user.py FIREBASE_UID setter

Supported roles:
    admin
    setter
    examiner
"""
import sys
from services.mongodb import users_collection

if len(sys.argv) != 3:
    print("Usage: python seed_user.py FIREBASE_UID ROLE")
    raise SystemExit(1)

uid = sys.argv[1]
role = sys.argv[2]

if role not in {"admin", "setter", "examiner"}:
    print("Invalid role.")
    raise SystemExit(1)

users_collection.update_one(
    {"firebase_uid": uid},
    {"$set": {"firebase_uid": uid, "role": role}},
    upsert=True
)

print(f"User {uid} assigned role: {role}")
