from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel
from core.time_utils import now_ist
from services.activityService import save_activity, get_activities


router = APIRouter(prefix="/activity")


class ActivityRequest(BaseModel):
    activity: str                         # required: what the user did
    tab: Optional[str] = None
    tehsil: Optional[str] = None
    village: Optional[str] = None
    khasra_no: Optional[str] = None
    detail_view: Optional[str] = None
    pop_feature: Optional[str] = None
    details: Optional[str] = None


@router.post("/log")
async def log_activity(body: ActivityRequest, request: Request):
    data = body.model_dump()
    data["username"] = request.state.username   # from the token, can't be faked
    data["role"] = request.state.role           # from the token, can't be faked
    data["activity_time"] = now_ist()           # set by the server, in IST

    try:
        saved = save_activity(data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to save activity: {str(e)}")

    return {
        "status": "success",
        "activity_log": saved,
    }


@router.get("/history")
async def activity_history(
    request: Request,
    username: Optional[str] = None,                 # optional: filter by one user
    limit: int = Query(50, ge=1, le=500),           # rows per page
    offset: int = Query(0, ge=0),                   # rows to skip
):
    # Only admins can view the activity log
    if request.state.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only Admin is allowed")

    try:
        rows = get_activities(username, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to fetch activity: {str(e)}")

    return {
        "status": "success",
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "activity_logs": rows,
    }