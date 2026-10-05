# services/authService.py
import secrets

from sqlalchemy import text

from database.db import engine

GET_USER = text("""
    SELECT id, username, name, password, email, mobile, is_active,
           access_token, token_expiry
    FROM "data".user_auth
    WHERE username = :username
""")

SAVE_SESSION = text("""
    UPDATE "data".user_auth
    SET access_token  = :access_token,
        refresh_token = :refresh_token,
        token_expiry  = :token_expiry,
        last_login    = :last_login
    WHERE id = :user_id
""")


def authenticate_user(username: str, password: str) -> dict | None:
    """Return user dict if username/password are correct, else None."""
    with engine.connect() as conn:
        user = conn.execute(GET_USER, {"username": username}).mappings().first()

    if not user:
        return None
    if not secrets.compare_digest(password.encode(), user["password"].encode()):
        return None

    return dict(user)


def save_session(user_id: int, access_token: str, refresh_token: str,
                 token_expiry, last_login) -> None:
    """Write the user's one active session into their row."""
    with engine.begin() as conn:      # begin() commits automatically
        conn.execute(SAVE_SESSION, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": token_expiry,
            "last_login": last_login,
            "user_id": user_id,
        })
        
        
IS_SESSION_VALID = text("""
    SELECT access_token, is_active
    FROM "data".user_auth
    WHERE username = :username
""")


def is_session_valid(username: str, token: str) -> bool:
    """True only if the user is active and this token is the one saved in their row."""
    with engine.connect() as conn:
        row = conn.execute(IS_SESSION_VALID, {"username": username}).mappings().first()

    if not row or not row["is_active"] or not row["access_token"]:
        return False

    return secrets.compare_digest(token.encode(), row["access_token"].encode())





GET_REFRESH_USER = text("""
    SELECT id, username, name, email, mobile, is_active, refresh_token
    FROM "data".user_auth
    WHERE username = :username
""")

UPDATE_TOKENS = text("""
    UPDATE "data".user_auth
    SET access_token  = :access_token,
        refresh_token = :refresh_token,
        token_expiry  = :token_expiry
    WHERE id = :user_id
""")


def get_user_for_refresh(username: str, refresh_token: str) -> dict | None:
    """Return the user only if active and refresh_token is the one stored in their row."""
    with engine.connect() as conn:
        user = conn.execute(GET_REFRESH_USER, {"username": username}).mappings().first()

    if not user or not user["is_active"] or not user["refresh_token"]:
        return None
    if not secrets.compare_digest(refresh_token.encode(), user["refresh_token"].encode()):
        return None

    return dict(user)


def update_tokens(user_id: int, access_token: str, refresh_token: str, token_expiry) -> None:
    """Replace the saved tokens. Does not touch last_login."""
    with engine.begin() as conn:
        conn.execute(UPDATE_TOKENS, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": token_expiry,
            "user_id": user_id,
        })
        
        
        
        
        
CLEAR_SESSION = text("""
    UPDATE "data".user_auth
    SET access_token  = NULL,
        refresh_token = NULL,
        token_expiry  = NULL
    WHERE username = :username
""")


def clear_session(username: str) -> None:
    """End the user's session by emptying their token slot."""
    with engine.begin() as conn:
        conn.execute(CLEAR_SESSION, {"username": username})
        
        
        
        
IS_ADMIN = text("""
    SELECT is_admin FROM "data".user_auth WHERE username = :username
""")

FORCE_CLEAR = text("""
    UPDATE "data".user_auth
    SET access_token  = NULL,
        refresh_token = NULL,
        token_expiry  = NULL
    WHERE username = :username
""")


def is_admin(username: str) -> bool:
    with engine.connect() as conn:
        row = conn.execute(IS_ADMIN, {"username": username}).mappings().first()
    return bool(row and row["is_admin"])


def force_logout_user(username: str) -> bool:
    """Clear the target user's session. Returns False if the user doesn't exist."""
    with engine.begin() as conn:
        result = conn.execute(FORCE_CLEAR, {"username": username})
    return result.rowcount > 0