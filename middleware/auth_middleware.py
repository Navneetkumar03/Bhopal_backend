# middleware/auth_middleware.py
# Runs on EVERY request. Checks the token, blocks or lets the request through.

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from core.security import decode_access_token
from services.authService import is_session_valid

# Routes that do NOT need an access token
PUBLIC_PATHS = {"/", "/auth/login", "/auth/refresh", "/auth/force_logout", "/docs", "/redoc", "/openapi.json"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Let CORS preflight and public routes through
        if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Check 1: header is present and well formed
        auth_header = request.headers.get("Authorization", "")
        scheme, _, token = auth_header.partition(" ")

        if scheme.lower() != "bearer" or not token:
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})

        # Check 2: signature, expiry and token type are valid
        username = decode_access_token(token)
        if not username:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        # Check 3: this token is the active session stored in the database
        if not await run_in_threadpool(is_session_valid, username, token):
            return JSONResponse(status_code=401, content={"detail": "Session is not active. Please log in again."})

        request.state.username = username   # available in any route
        return await call_next(request)