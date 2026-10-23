import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from schemas.pdf_schema import PdfReportRequest
from services.pdf_report_service import pdf_report_service

router = APIRouter()


@router.post("/pdf/report", response_class=FileResponse)
async def generate_pdf_report(
    payload: PdfReportRequest,
    background_tasks: BackgroundTasks,
):
    try:
        # print(payload)
        pdf_path = await pdf_report_service.generate_bhopal_report(
            markers=[m.model_dump() for m in payload.markers],
            map_image_data_url=payload.map_image,
            title=payload.title,
            subtitle=payload.subtitle,
            selectedVillage=payload.selectedVillage,
            selectedKhasra=payload.selectedKhasra,
            selectedApattiGroup=payload.selectedApattiGroup,
            selectedApattiNo=payload.selectedApattiNo,
            map_scale=payload.map_scale, # <--- ADD THIS
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="PDF generation failed unexpectedly",
        )

    pdf_path_obj = Path(pdf_path)
    background_tasks.add_task(pdf_report_service.cleanup, str(pdf_path_obj))

    return FileResponse(
        path=pdf_path_obj,
        media_type="application/pdf",
        filename=f"bhopal-masterplan-{pdf_path_obj.stem}.pdf",
    )