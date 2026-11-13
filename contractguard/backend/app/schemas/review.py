from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel


class SuggestionResponse(BaseModel):
    id: str
    finding_id: str
    clause_id: Optional[str] = None
    clause_no: Optional[str] = None
    original_text: str
    proposed_text: str
    rationale: str
    status: str  # pending, approved, edited, rejected
    final_text: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None

    class Config:
        from_attributes = True


class DecisionItem(BaseModel):
    status: str  # 'approved', 'edited', 'rejected'
    final_text: Optional[str] = None


class ReviewDecisionsRequest(BaseModel):
    decisions: Dict[str, DecisionItem]  # suggestion_id -> DecisionItem


class ReviewStartResponse(BaseModel):
    run_id: str
    thread_id: str
    status: str
    message: str


class ReviewStatusResponse(BaseModel):
    run_id: str
    thread_id: str
    status: str  # 'running', 'awaiting_review', 'completed', 'failed'
    suggestions: List[SuggestionResponse]
    decisions_count: int
    pending_count: int
    total_count: int
    progress_percentage: float
    message: Optional[str] = None
