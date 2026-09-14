from datetime import datetime, timezone
from services.mongodb import audit_collection

def log_event(action, uid=None, paper_id=None, details=None):
    audit_collection.insert_one({
        "action": action,
        "uid": uid,
        "paper_id": paper_id,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc)
    })
