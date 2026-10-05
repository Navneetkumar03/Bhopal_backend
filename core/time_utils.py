# core/time_utils.py
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> datetime:
    """Current Indian time without timezone info (matches the TIMESTAMP columns)."""
    return datetime.now(IST).replace(tzinfo=None)


def to_ist(dt: datetime) -> datetime:
    """Convert a timezone-aware datetime to naive Indian time."""
    return dt.astimezone(IST).replace(tzinfo=None)