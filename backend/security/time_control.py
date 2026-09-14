from datetime import datetime, timezone
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")
UTC = timezone.utc


def normalize_to_utc(dt):
    """
    Convert any datetime to timezone-aware UTC.

    IMPORTANT:
    MongoDB/BSON stores datetime values internally as UTC.

    PyMongo normally returns them as naive UTC datetimes
    unless tz_aware=True is configured.

    Therefore:
        naive MongoDB datetime = UTC
        NOT IST
    """

    if dt is None:
        return None

    # MongoDB/PyMongo may return naive UTC.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return dt.astimezone(UTC)


def normalize_to_ist(dt):
    """
    Convert a datetime to IST for display.
    """

    if dt is None:
        return None

    utc_time = normalize_to_utc(dt)

    return utc_time.astimezone(IST)


def can_release(release_at):
    """
    Return True only when the current instant has reached
    the configured release instant.

    Comparison is performed entirely in UTC.
    """

    if release_at is None:
        return False

    release_at_utc = normalize_to_utc(release_at)

    current_time_utc = datetime.now(UTC)

    return current_time_utc >= release_at_utc


def release_status(release_at):
    """
    Return detailed timing information.

    IST values are provided for human-readable debugging.
    """

    current_time_utc = datetime.now(UTC)
    current_time_ist = current_time_utc.astimezone(IST)

    if release_at is None:
        return {
            "locked": True,
            "release_at_utc": None,
            "release_at_ist": None,
            "current_time_utc": current_time_utc.isoformat(),
            "current_time_ist": current_time_ist.isoformat(),
        }

    release_at_utc = normalize_to_utc(release_at)
    release_at_ist = release_at_utc.astimezone(IST)

    locked = current_time_utc < release_at_utc

    return {
        "locked": locked,
        "release_at_utc": release_at_utc.isoformat(),
        "release_at_ist": release_at_ist.isoformat(),
        "current_time_utc": current_time_utc.isoformat(),
        "current_time_ist": current_time_ist.isoformat(),
    }