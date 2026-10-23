# services/objectionService.py

from fastapi.encoders import jsonable_encoder
from sqlalchemy import text

from database.db import engine



QUERY = text("""
    SELECT
        id,
        objection_id,
        code,
        area,
        bhucode,
        village,
        khasra_no,
        gov_kh,
        obj_type,
        apatti_gro,
        remark,
        vargikaran,
        upvargikar,
        geom
    FROM "data".objection1
    ORDER BY id
""")


def get_all_objection_data() -> dict:
    try:
        with engine.connect() as conn:
            rows = conn.execute(QUERY).mappings().all()

        data = jsonable_encoder([dict(r) for r in rows])

        return {
            "status": "success",
            "count": len(data),
            "data": data,
        }
    except Exception as e:
        print("Error :",e)