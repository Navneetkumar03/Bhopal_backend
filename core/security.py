# core/security.py
from datetime import datetime, timedelta, timezone

import jwt

from config import setting




def _create_token(username: str, expires_delta: timedelta, token_type: str,
                  role: str | None = None) -> tuple[str, datetime]:
    expiry = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": username, "type": token_type, "exp": expiry}
    if role:
        payload["role"] = role
    token = jwt.encode(payload, setting.jwt_secret_key, algorithm=setting.jwt_algorithm)
    return token, expiry


def create_access_token(username: str, role: str) -> tuple[str, datetime]:
    return _create_token(username, timedelta(minutes=setting.access_token_expire_minutes), "access", role)


def create_refresh_token(username: str, role: str) -> tuple[str, datetime]:
    return _create_token(username, timedelta(days=setting.refresh_token_expire_days), "refresh", role)



def _decode_token(token: str, expected_type: str) -> dict | None:
    """Returns the payload if signature, expiry and token type are all valid."""
    try:
        payload = jwt.decode(token, setting.jwt_secret_key, algorithms=[setting.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload


def decode_access_token(token: str) -> dict | None:
    return _decode_token(token, "access")


def decode_refresh_token(token: str) -> dict | None:
    return _decode_token(token, "refresh")