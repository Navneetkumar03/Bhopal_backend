from typing import List, Optional
from pydantic import BaseModel, Field


class MarkerItem(BaseModel):
    id: str
    objection_id: str
    category: str
    title: Optional[str] = ""
    status: Optional[str] = ""
    tehsil: Optional[str] = ""
    village: Optional[str] = ""
    khasra_no: Optional[str] = ""
    date: Optional[str] = ""
    description: Optional[str] = ""
    applicant_name: Optional[str] = None
    mobile: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class PdfReportRequest(BaseModel):
    title: str = Field(default="Bhopal Development Plan - 2047 (Draft)")
    subtitle: str = Field(
        default="Objections & Suggestions on the Draft Development Plan"
    )
    map_image: str = Field(
        ...,
        description="Base64 data URL of the map screenshot (data:image/...;base64,...)"
    )
    markers: List[MarkerItem]
    selectedTehsil: str = Field(default="All Tehsil")
    selectedVillage: str = Field(default="All Village")
    selectedKhasra: str = Field(default="")