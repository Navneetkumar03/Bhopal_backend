import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from utils import render_html
from utils import export_pdf

logger = logging.getLogger(__name__)


class PdfReportService:
    async def generate_bhopal_report(
        self,
        markers: List[Dict[str, Any]],
        map_image_data_url: str,
        title: str = "Bhopal Development Plan - 2047 (Draft)",
        subtitle: str = "Objections & Suggestions on the Draft Development Plan",
        selectedVillage:str = "All Tehsil",
        selectedTehsil:str = "All Village",
        selectedKhasra:str = "",
    ) -> str:
        """
        Generate the PDF asynchronously and return its file path.
        """
        logger.info(
            "[PdfReportService] Generating report for %d markers",
            len(markers),
        )

        # 1. Render HTML (sync — fast, stays as-is)
        try:
            html_path = render_html.build(
                markers=markers,
                map_image=map_image_data_url,
                report_title=title,
                report_subtitle=subtitle,
                village= selectedVillage,
                tehsil=selectedTehsil,
                khasra=selectedKhasra,
            )
            logger.info("[PdfReportService] HTML rendered at %s", html_path)
        except Exception as exc:
            logger.exception("[PdfReportService] HTML render failed")
            raise RuntimeError(f"HTML render failed: {exc}") from exc

        # 2. Convert to PDF (async now — await it)
        try:
            pdf_path = await export_pdf.convert(html_path)
            logger.info("[PdfReportService] PDF generated at %s", pdf_path)
        except Exception as exc:
            logger.exception("[PdfReportService] PDF conversion failed")
            raise RuntimeError(f"PDF conversion failed: {exc}") from exc

        if not os.path.exists(pdf_path):
            raise RuntimeError("PDF file was not produced by the converter")

        return pdf_path

    @staticmethod
    def cleanup(file_path: str) -> None:
        try:
            p = Path(file_path)
            if p.exists():
                p.unlink()
        except Exception:
            logger.warning("[PdfReportService] Cleanup failed for %s", file_path)


pdf_report_service = PdfReportService()