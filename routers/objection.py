from fastapi import APIRouter, HTTPException

from services.objectionService import get_all_objection_data

# ---------------------------------------------------------
# APIRouter is essentially a mini FastAPI app. It has the same decorators
# (@router.get, @router.post, etc.), the same dependency injection, the same 
# everything — but it doesn't run on its own. It has to be plugged into the main app.
# ---------------------------------------------------------

router = APIRouter()   # ← create a mini-app


@router.get("/objection/history")     # ← register route on the mini-app
async def get_objection_data():
    """
    Fetch all objection records from the database.
    No parameters required.
    Returns all data available in JSON format.
    """
    try:
        result = get_all_objection_data()
        if not result:
            raise HTTPException(status_code=404, detail="No objection data found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))