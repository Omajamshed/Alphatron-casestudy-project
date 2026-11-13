from typing import Optional
from pydantic import BaseModel


class ClauseResponse(BaseModel):
    id: str
    version_id: str
    clause_no: Optional[str] = None
    heading: Optional[str] = None
    text: str
    page_start: int = 1
    page_end: int = 1
    clause_type: Optional[str] = None
    summary: Optional[str] = None
    risk_level: Optional[str] = "low"  # low, medium, high, critical

    class Config:
        from_attributes = True
