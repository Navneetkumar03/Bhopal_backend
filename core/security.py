# core/security.py
from datetime import datetime, timedelta, timezone

import jwt

from config import setting


def _create_token(username: str, expires_delta: timedelta, token_type: str) -> tuple[str, datetime]:
    expiry = datetime.now(timezone.utc) + expires_delta
    token = jwt.encode(
        {"sub": username, "type": token_type, "exp": expiry},
        setting.jwt_secret_key,
        algorithm=setting.jwt_algorithm,
    )
    return token, expiry


def create_access_token(username: str) -> tuple[str, datetime]:
    return _create_token(username, timedelta(minutes=setting.access_token_expire_minutes), "access")


def create_refresh_token(username: str) -> tuple[str, datetime]:
    return _create_token(username, timedelta(days=setting.refresh_token_expire_days), "refresh")


def _decode_token(token: str, expected_type: str) -> str | None:
    """Returns username if signature, expiry and token type are all valid."""
    try:
        payload = jwt.decode(token, setting.jwt_secret_key, algorithms=[setting.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload.get("sub")


def decode_access_token(token: str) -> str | None:
    return _decode_token(token, "access")


def decode_refresh_token(token: str) -> str | None:
    return _decode_token(token, "refresh")