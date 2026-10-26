# services/activityService.py
# Only database logic for activity tracking.

from sqlalchemy import text

from database.db import engine

INSERT_ACTIVITY = text("""
    INSERT INTO "data".user_activity_log
        (username, role, tehsil, village, khasra_no, detail_view, pop_feature,
         tab, activity, details, activity_time)
    VALUES
        (:username, :role, :tehsil, :village, :khasra_no, :detail_view, :pop_feature,
         :tab, :activity, :details, :activity_time)
    RETURNING id, username, role, tehsil, village, khasra_no, detail_view, pop_feature,
              tab, activity, details, activity_time
""")

SELECT_ACTIVITIES = text("""
    SELECT id, username, role, tehsil, village, khasra_no, detail_view, pop_feature,
           tab, activity, details, activity_time
    FROM "data".user_activity_log
    WHERE (CAST(:username AS varchar) IS NULL OR username = :username)
    ORDER BY activity_time DESC
    LIMIT :limit OFFSET :offset
""")


def save_activity(data: dict) -> dict:
    """Insert one activity row and return it. `data` must hold every column key."""
    with engine.begin() as conn:
        row = conn.execute(INSERT_ACTIVITY, data).mappings().first()
    return dict(row)


def get_activities(username: str | None, limit: int, offset: int) -> list[dict]:
    """Return activity rows, newest first. Optionally only for one username."""
    with engine.connect() as conn:
        rows = conn.execute(
            SELECT_ACTIVITIES,
            {"username": username, "limit": limit, "offset": offset},
        ).mappings().all()
    return [dict(r) for r in rows]

