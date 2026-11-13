from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ContractCreate(BaseModel):
    title: str
    contract_type: str = "rental"  # 'rental', 'freelance', 'employment', 'other'
    party_role: Optional[str] = "tenant"  # 'tenant', 'freelancer', 'employee'
    jurisdiction: Optional[str] = "US"


class VersionResponse(BaseModel):
    id: str
    version: int
    filename: Optional[str] = None
    page_count: int = 1
    risk_score: Optional[float] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    id: str
    title: str
    contract_type: str
    party_role: Optional[str] = None
    jurisdiction: Optional[str] = None
    current_version: int = 1
    created_at: datetime
    latest_risk_score: Optional[float] = None
    next_deadline: Optional[str] = None
    versions_count: int = 1

    class Config:
        from_attributes = True


class KeyTermResponse(BaseModel):
    id: str
    clause_id: Optional[str] = None
    clause_no: Optional[str] = None
    kind: str
    raw_text: Optional[str] = None
    value_number: Optional[float] = None
    value_unit: Optional[str] = None
    value_date: Optional[date] = None
    computed: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ContractDetailResponse(BaseModel):
    contract: ContractResponse
    versions: List[VersionResponse]
    current_version_id: str
