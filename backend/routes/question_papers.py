import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, request, jsonify

from security.rbac import require_roles
from security.audit import log_event
from services.encryption import encrypt_data
from services.shamir import split_secret, serialize_share
from services.mongodb import papers_collection, shares_collection
from services.backblaze import upload_bytes


question_papers_bp = Blueprint("question_papers", __name__)

# -------------------------------------------------
# Indian Standard Time
# -------------------------------------------------
IST = ZoneInfo("Asia/Kolkata")


@question_papers_bp.post("/upload")
@require_roles("admin", "setter")
def upload_question_paper(user):

    try:

        # -----------------------------------------
        # 1. Validate uploaded file
        # -----------------------------------------
        if "file" not in request.files:
            return jsonify({
                "error": "No question-paper file supplied."
            }), 400

        file = request.files["file"]

        if not file.filename:
            return jsonify({
                "error": "Empty filename."
            }), 400

        # -----------------------------------------
        # 2. Get examination metadata
        # -----------------------------------------
        exam_name = request.form.get(
            "exam_name",
            ""
        ).strip()

        release_at_raw = request.form.get(
            "release_at",
            ""
        ).strip()

        if not exam_name:
            return jsonify({
                "error": "Exam name is required."
            }), 400

        if not release_at_raw:
            return jsonify({
                "error": "Release date and time are required."
            }), 400

        # -----------------------------------------
        # 3. Validate release time
        #    IMPORTANT:
        #    Time is treated as IST.
        # -----------------------------------------
        try:

            # Frontend sends:
            # YYYY-MM-DDTHH:MM
            #
            # Example:
            # 2026-09-14T14:30
            #
            # This means:
            # 14 September 2026, 2:30 PM IST

            release_at = datetime.fromisoformat(
                release_at_raw
            )

            # If no timezone is supplied, explicitly
            # treat the selected time as IST.
            if release_at.tzinfo is None:
                release_at = release_at.replace(
                    tzinfo=IST
                )
            else:
                # If a timezone is supplied, convert it
                # to IST.
                release_at = release_at.astimezone(
                    IST
                )

        except ValueError:
            return jsonify({
                "error": (
                    "Invalid release_at format. "
                    "Use YYYY-MM-DDTHH:MM."
                )
            }), 400

        # -----------------------------------------
        # 4. Check release time is in the future
        # -----------------------------------------
        current_time_ist = datetime.now(IST)

        if release_at <= current_time_ist:
            return jsonify({
                "error": (
                    "Release date and time must "
                    "be in the future."
                ),
                "current_ist_time": current_time_ist.isoformat(),
                "release_ist_time": release_at.isoformat()
            }), 400

        # -----------------------------------------
        # 5. Read PDF into memory
        # -----------------------------------------
        data = file.read()

        if not data:
            return jsonify({
                "error": "Uploaded file is empty."
            }), 400

        # -----------------------------------------
        # 6. AES-256-GCM encryption
        # -----------------------------------------
        encrypted, aes_key, nonce = encrypt_data(data)

        # -----------------------------------------
        # 7. Shamir Secret Sharing
        #    3-of-5 threshold
        # -----------------------------------------
        shares = split_secret(
            aes_key,
            threshold=3,
            shares=5
        )

        # -----------------------------------------
        # 8. Generate unique paper ID
        # -----------------------------------------
        paper_id = str(uuid.uuid4())

        # -----------------------------------------
        # 9. Make filename safe
        # -----------------------------------------
        safe_name = (
            file.filename
            .replace("/", "_")
            .replace("\\", "_")
        )

        encrypted_name = (
            f"papers/{paper_id}/{safe_name}.enc"
        )

        # -----------------------------------------
        # 10. Store encrypted paper in Backblaze B2
        # -----------------------------------------
        upload_bytes(
            encrypted_name,
            encrypted,
            "application/octet-stream"
        )

        # -----------------------------------------
        # 11. Store Shamir shares 4 and 5
        #     in Backblaze B2
        # -----------------------------------------
        upload_bytes(
            f"shares/{paper_id}/share4.txt",
            serialize_share(
                shares[3]
            ).encode("utf-8"),
            "text/plain"
        )

        upload_bytes(
            f"shares/{paper_id}/share5.txt",
            serialize_share(
                shares[4]
            ).encode("utf-8"),
            "text/plain"
        )

        # -----------------------------------------
        # 12. Store shares 1, 2 and 3
        #     in MongoDB Atlas
        # -----------------------------------------
        shares_collection.insert_many([
            {
                "paper_id": paper_id,
                "share_number": 1,
                "share": serialize_share(
                    shares[0]
                ),
                "storage": "mongodb"
            },
            {
                "paper_id": paper_id,
                "share_number": 2,
                "share": serialize_share(
                    shares[1]
                ),
                "storage": "mongodb"
            },
            {
                "paper_id": paper_id,
                "share_number": 3,
                "share": serialize_share(
                    shares[2]
                ),
                "storage": "mongodb"
            }
        ])

        # -----------------------------------------
        # 13. Store complete paper metadata
        # -----------------------------------------
        paper_doc = {
            "paper_id": paper_id,

            "exam_name": exam_name,

            "original_filename": safe_name,

            # Backblaze encrypted object
            "encrypted_object": encrypted_name,

            # AES-GCM nonce
            "nonce": nonce.hex(),

            # Release time stored as IST
            "release_at": release_at,

            # Explicit timezone information
            "timezone": "Asia/Kolkata",

            # Ownership
            "uploaded_by": user["uid"],

            # Upload timestamp in IST
            "uploaded_at": datetime.now(IST),

            # Security configuration
            "encryption": "AES-256-GCM",

            "secret_sharing": "Shamir 3-of-5",

            # Current state
            "status": "locked"
        }

        papers_collection.insert_one(
            paper_doc
        )

        # -----------------------------------------
        # 14. Audit event
        # -----------------------------------------
        log_event(
            "QUESTION_PAPER_SECURED",
            user["uid"],
            paper_id,
            {
                "exam_name": exam_name,

                "release_at": release_at.isoformat(),

                "timezone": "Asia/Kolkata",

                "encryption": "AES-256-GCM",

                "secret_sharing": "Shamir 3-of-5"
            }
        )

        # -----------------------------------------
        # 15. Response
        # -----------------------------------------
        return jsonify({

            "message": (
                "Question paper encrypted "
                "and secured successfully."
            ),

            "paper_id": paper_id,

            "exam_name": exam_name,

            "release_at": release_at.isoformat(),

            "timezone": "IST",

            "status": "locked",

            "encryption": "AES-256-GCM",

            "secret_sharing": "Shamir 3-of-5"

        }), 201

    except Exception as exc:

        return jsonify({
            "error": "Failed to secure question paper.",
            "details": str(exc)
        }), 500