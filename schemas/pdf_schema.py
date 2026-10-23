from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MarkerItem(BaseModel):
    # Allow extra fields like 'geom' and 'remark' to be ignored instead of causing a 422
    model_config = ConfigDict(extra="ignore")

    id: str
    objection_id: Optional[str] = ""
    apatti_no: Optional[str] = ""
    apattiNo: Optional[str] = ""
    object_type: Optional[str] = ""
    
    # Location
    village: Optional[str] = ""
    khasra_no: Optional[str] = ""
    
    # Classification & Grouping
    vargikaran: Optional[str] = ""
    upvargikar: Optional[str] = ""
    apatti_gro: Optional[str] = ""
    apatti_group: Optional[str] = ""
    group: Optional[str] = ""
    
    # Cadastral Details
    area: Optional[float] = None
    bhucode: Optional[str] = ""
    code: Optional[str] = ""
    gov_kh: Optional[str] = ""

class PdfReportRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = "Bhopal Development Plan - 2047 (Draft)"
    subtitle: str = "Objections & Suggestions on the Draft Development Plan"
    map_image: str
    markers: List[MarkerItem]
    selectedVillage: Optional[str] = ""
    selectedKhasra: Optional[str] = ""
    selectedApattiGroup: Optional[str | int] = None
    selectedApattiNo: Optional[str | int] = None
    map_scale: Optional[float] = None  # <--- ADD THIS