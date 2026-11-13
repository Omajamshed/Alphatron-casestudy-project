from typing import List, Optional, Dict
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    top_k: int = 4


class CitationItem(BaseModel):
    file: Optional[str] = "contract.pdf"
    clause: str
    page: int
    clause_id: Optional[str] = None
    heading: Optional[str] = None


class ChatTokens(BaseModel):
    # Field names 'in' and 'out' using alias or direct dict
    tokens_in: int = 0
    tokens_out: int = 0


class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem]
    tokens: Dict[str, int]  # {"in": 1820, "out": 96}
    seconds: float
