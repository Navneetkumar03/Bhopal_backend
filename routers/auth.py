from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from core.time_utils import now_ist, to_ist
from core.security import create_access_token, create_refresh_token, decode_refresh_token
from services.authService import (
    authenticate_user, save_session, get_user_for_refresh, update_tokens, clear_session,
)


router = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    username: str
    password: str





@router.post("/login")
async def login(body: LoginRequest):
    user = authenticate_user(body.username, body.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")

    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User is inactive")

    now = now_ist()

    # One device only: block if an unexpired session already exists
    if user["access_token"] and user["token_expiry"] and user["token_expiry"] > now:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="user_logged_in_another_device")

    access_token, access_expiry = create_access_token(user["username"])
    refresh_token, _ = create_refresh_token(user["username"])
    token_expiry = to_ist(access_expiry)

    save_session(user["id"], access_token, refresh_token, token_expiry, now)

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "token_expiry": token_expiry,
        "user": {"id": user["id"], "username": user["username"], "name": user["name"],
                 "email": user["email"], "mobile": user["mobile"]},
    }
    
    
    


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh(body: RefreshRequest):
    # Check 1: signature, expiry and type
    username = decode_refresh_token(body.refresh_token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token expired or invalid")

    # Check 2 and 3: user is active and this is the stored refresh token
    user = get_user_for_refresh(username, body.refresh_token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token does not match an active session")

    access_token, access_expiry = create_access_token(user["username"])
    new_refresh_token, _ = create_refresh_token(user["username"])
    token_expiry = to_ist(access_expiry)

    update_tokens(user["id"], access_token, new_refresh_token, token_expiry)

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "token_expiry": token_expiry,
    }
    
    

@router.post("/logout")
async def logout(request: Request):
    username = request.state.username   # set by the middleware after validating the token
    clear_session(username)

    return {
        "status": "success",
        "message": "Successfully logged out",
        "username": username,
        "logout_time": now_ist(),
    }
    
    
    
    
    
class ForceLogoutRequest(BaseModel):
    username: str
    password: str


@router.post("/force_logout")
async def force_logout(body: ForceLogoutRequest):
    # The password proves the caller owns this ID
    user = authenticate_user(body.username, body.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")

    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User is inactive")

    clear_session(user["username"])

    return {
        "status": "success",
        "message": "Successfully force logged out",
        "username": user["username"],
        "logout_time": now_ist(),
    }