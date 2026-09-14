from itertools import combinations
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify

from security.rbac import require_roles
from security.time_control import (
    can_release,
    normalize_to_ist,
    release_status,
)
from security.audit import log_event

from services.mongodb import (
    papers_collection,
    shares_collection,
)

from services.backblaze import download_bytes

from services.shamir import (
    deserialize_share,
    reconstruct_secret,
)

from services.encryption import decrypt_data


release_bp = Blueprint("release", __name__)

IST = ZoneInfo("Asia/Kolkata")
UTC = timezone.utc


@release_bp.post("/<paper_id>")
@require_roles("admin", "examiner")
def release_paper(user, paper_id):

    # =========================================================
    # 1. FIND PAPER
    # =========================================================

    paper = papers_collection.find_one({
        "paper_id": paper_id
    })

    if not paper:
        return jsonify({
            "error": "Question paper not found."
        }), 404

    # =========================================================
    # 2. GET RELEASE TIME
    # =========================================================

    release_at = paper.get("release_at")

    if not release_at:
        return jsonify({
            "error": (
                "Question paper does not have "
                "a configured release time."
            )
        }), 500

    # =========================================================
    # 3. NORMALIZE MONGODB TIME
    # =========================================================

    try:

        release_at_utc = release_at

        # MongoDB/PyMongo may return a naive UTC datetime.
        if release_at_utc.tzinfo is None:
            release_at_utc = release_at_utc.replace(
                tzinfo=UTC
            )

        release_at_utc = release_at_utc.astimezone(UTC)

        current_time_utc = datetime.now(UTC)

        release_at_ist = release_at_utc.astimezone(IST)
        current_time_ist = current_time_utc.astimezone(IST)

    except Exception as exc:

        log_event(
            "QUESTION_PAPER_RELEASE_FAILED",
            user["uid"],
            paper_id,
            {
                "reason": "Invalid release timestamp.",
                "details": str(exc),
            }
        )

        return jsonify({
            "error": "Invalid question-paper release timestamp."
        }), 500

    # =========================================================
    # 4. HARD RELEASE-TIME LOCK
    # =========================================================

    # IMPORTANT:
    #
    # Example:
    #
    # release_at_ist = 15:30 IST
    # current_time_ist = 14:47 IST
    #
    # 14:47 < 15:30
    #
    # Therefore release MUST be denied.
    #
    # Comparison is done using UTC instants.

    if current_time_utc < release_at_utc:

        log_event(
            "QUESTION_PAPER_RELEASE_BLOCKED",
            user["uid"],
            paper_id,
            {
                "reason": "Release attempted before scheduled time.",
                "release_at_ist": release_at_ist.isoformat(),
                "current_time_ist": current_time_ist.isoformat(),
            }
        )

        return jsonify({
            "error": "Question paper is still locked.",
            "status": "locked",
            "release_at_ist": release_at_ist.isoformat(),
            "current_time_ist": current_time_ist.isoformat(),
            "release_at_utc": release_at_utc.isoformat(),
            "current_time_utc": current_time_utc.isoformat(),
        }), 403

    # =========================================================
    # 5. GET MONGODB SHARES
    # =========================================================

    db_share_docs = list(
        shares_collection
        .find({
            "paper_id": paper_id
        })
        .sort(
            "share_number",
            1
        )
    )

    if len(db_share_docs) < 3:

        log_event(
            "QUESTION_PAPER_RELEASE_FAILED",
            user["uid"],
            paper_id,
            {
                "reason": (
                    "Required MongoDB shares unavailable."
                )
            }
        )

        return jsonify({
            "error": (
                "Required database shares are unavailable."
            )
        }), 500

    # =========================================================
    # 6. PARSE MONGODB SHARES
    # =========================================================

    try:

        shares = [
            deserialize_share(
                doc["share"]
            )
            for doc in db_share_docs[:3]
        ]

    except Exception as exc:

        log_event(
            "QUESTION_PAPER_RELEASE_FAILED",
            user["uid"],
            paper_id,
            {
                "reason": "Invalid MongoDB share format.",
                "details": str(exc),
            }
        )

        return jsonify({
            "error": (
                "Stored database shares are invalid."
            )
        }), 500

    # =========================================================
    # 7. DOWNLOAD BACKBLAZE SHARES 4 AND 5
    # =========================================================

    try:

        share4_data = download_bytes(
            f"shares/{paper_id}/share4.txt"
        )

        share5_data = download_bytes(
            f"shares/{paper_id}/share5.txt"
        )

        share4 = deserialize_share(
            share4_data.decode("utf-8")
        )

        share5 = deserialize_share(
            share5_data.decode("utf-8")
        )

        shares.extend([
            share4,
            share5
        ])

    except Exception as exc:

        log_event(
            "QUESTION_PAPER_RELEASE_FAILED",
            user["uid"],
            paper_id,
            {
                "reason": (
                    "Backblaze shares unavailable."
                ),
                "details": str(exc),
            }
        )

        return jsonify({
            "error": (
                "Required cloud shares are unavailable."
            )
        }), 500

    # =========================================================
    # 8. RECONSTRUCT AES KEY
    # =========================================================

    reconstructed_key = None
    plaintext = None
    last_error = None

    try:

        # First try MongoDB shares 1, 2, 3.
        reconstructed_key = reconstruct_secret(
            shares[:3]
        )

        # =====================================================
        # 9. DOWNLOAD ENCRYPTED QUESTION PAPER
        # =====================================================

        encrypted = download_bytes(
            paper["encrypted_object"]
        )

        nonce = bytes.fromhex(
            paper["nonce"]
        )

        # =====================================================
        # 10. DECRYPT IN MEMORY
        # =====================================================

        plaintext = decrypt_data(
            encrypted,
            reconstructed_key,
            nonce
        )

    except Exception as first_error:

        last_error = first_error

        # =====================================================
        # FALLBACK: TRY EVERY 3-OF-5 COMBINATION
        # =====================================================

        try:

            encrypted = download_bytes(
                paper["encrypted_object"]
            )

            nonce = bytes.fromhex(
                paper["nonce"]
            )

            for combo in combinations(
                shares,
                3
            ):

                try:

                    candidate_key = reconstruct_secret(
                        list(combo)
                    )

                    candidate_plaintext = decrypt_data(
                        encrypted,
                        candidate_key,
                        nonce
                    )

                    reconstructed_key = candidate_key
                    plaintext = candidate_plaintext

                    break

                except Exception as combo_error:

                    last_error = combo_error

        except Exception as download_error:

            last_error = download_error

    # =========================================================
    # 11. DECRYPTION FAILURE
    # =========================================================

    if plaintext is None:

        log_event(
            "QUESTION_PAPER_RELEASE_FAILED",
            user["uid"],
            paper_id,
            {
                "reason": "AES decryption failed.",
                "details": str(last_error),
            }
        )

        return jsonify({
            "error": (
                "Question paper decryption failed."
            )
        }), 500

    # =========================================================
    # 12. AUDIT SUCCESSFUL RELEASE
    # =========================================================

    log_event(
        "QUESTION_PAPER_RELEASED",
        user["uid"],
        paper_id,
        {
            "release_time_ist": (
                datetime.now(IST).isoformat()
            ),
            "scheduled_release_time_ist": (
                release_at_ist.isoformat()
            ),
            "role": user.get("role"),
            "threshold": "3-of-5",
            "decryption": "in-memory",
        }
    )

    # =========================================================
    # 13. RETURN PDF
    # =========================================================

    return plaintext, 200, {
        "Content-Type": "application/pdf",

        "Content-Disposition": (
            f'inline; '
            f'filename="{paper["original_filename"]}"'
        ),

        "Cache-Control": (
            "no-store, no-cache, "
            "must-revalidate"
        ),

        "Pragma": "no-cache",

        "Expires": "0",
    }