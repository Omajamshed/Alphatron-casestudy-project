from typing import TypedDict, List, Dict, Any, Optional


class ReviewState(TypedDict, total=False):
    version_id: str
    contract_id: str
    party_role: str  # tenant, freelancer, employee, other
    contract_type: str
    clauses: List[Dict[str, Any]]
    key_terms: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    standard_terms: Dict[str, Any]  # finding_id -> retrieved KB passages
    suggestions: List[Dict[str, Any]]
    attempt: int
    problems: List[str]
    decisions: Dict[str, Any]  # suggestion_id -> {status: 'approved'|'edited'|'rejected', final_text: str}
    route: str
    export_ids: List[str]
    risk_score: float
    status: str
    message: str
