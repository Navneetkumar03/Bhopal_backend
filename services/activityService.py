# services/activityService.py
# Only database logic for activity tracking.

from sqlalchemy import text

from database.db import engine

INSERT_ACTIVITY = text("""
    INSERT INTO "data".user_activity_log
        (username, tehsil, village, khasra_no, detail_view, pop_feature,
         tab, activity, details, activity_time)
    VALUES
        (:username, :tehsil, :village, :khasra_no, :detail_view, :pop_feature,
         :tab, :activity, :details, :activity_time)
    RETURNING id, username, tehsil, village, khasra_no, detail_view, pop_feature,
              tab, activity, details, activity_time
""")


def save_activity(data: dict) -> dict:
    """Insert one activity row and return it. `data` must hold every column key."""
    with engine.begin() as conn:
        row = conn.execute(INSERT_ACTIVITY, data).mappings().first()
    return dict(row)