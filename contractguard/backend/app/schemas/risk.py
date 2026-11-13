from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel


class FindingResponse(BaseModel):
    id: str
    clause_id: str
    clause_no: Optional[str] = None
    heading: Optional[str] = None
    original_text: Optional[str] = None
    severity: str  # low, medium, high, critical
    category: str
    reason: str
    standard_term_ref: Optional[str] = None
    score: float

    class Config:
        from_attributes = True


class CategoryBreakdownItem(BaseModel):
    category: str
    count: int
    max_severity: str
    weight: float
    score_contribution: float


class RiskAnalysisResponse(BaseModel):
    version_id: str
    contract_id: str
    overall_score: float  # 0 to 100
    risk_level: str  # Low, Moderate, High, Critical
    findings: List[FindingResponse]
    category_breakdown: List[CategoryBreakdownItem]
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class RiskHistoryItem(BaseModel):
    version_id: str
    version: int
    filename: Optional[str] = None
    risk_score: Optional[float] = None
    uploaded_at: Optional[str] = None
