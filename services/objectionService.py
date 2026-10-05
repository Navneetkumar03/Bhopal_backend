# services/objectionService.py

from fastapi.encoders import jsonable_encoder
from sqlalchemy import text

from database.db import engine



QUERY = text(f"""
    SELECT
        id,
        objection_id,
        name,
        mobile,
        latitude,
        longitude,
        obj_type,
        status,
        village,
        tehsil,
        khasra_no,
        description,
        date,
        document_link
    FROM "data".objection
    ORDER BY id
""")


def get_all_objection_data() -> dict:
    with engine.connect() as conn:
        rows = conn.execute(QUERY).mappings().all()

    data = jsonable_encoder([dict(r) for r in rows])

    return {
        "status": "success",
        "count": len(data),
        "data": data,
    }