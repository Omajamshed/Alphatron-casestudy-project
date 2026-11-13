from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.db.repositories.contract_repo import ContractRepository
from app.db.repositories.clause_repo import ClauseRepository
from app.db.repositories.finding_repo import FindingRepository
from app.schemas.clause import ClauseResponse
from app.schemas.contract import KeyTermResponse
from app.schemas.risk import (
    RiskAnalysisResponse,
    FindingResponse,
    CategoryBreakdownItem,
    RiskHistoryItem,
)
from app.services.rules.risk_scoring import calculate_overall_contract_risk
from app.api.deps import get_current_user

router = APIRouter(tags=["risk"])


@router.get("/versions/{vid}/clauses", response_model=List[ClauseResponse])
def get_version_clauses(
    vid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    clause_repo = ClauseRepository(db)
    finding_repo = FindingRepository(db)
    clauses = clause_repo.get_clauses_by_version(vid)
    findings = finding_repo.get_findings(vid)

    finding_map = {f.clause_id: f.severity for f in findings}

    result = []
    for c in clauses:
        risk_lvl = finding_map.get(c.id, "low")
        result.append(
            ClauseResponse(
                id=c.id,
                version_id=c.version_id,
                clause_no=c.clause_no,
                heading=c.heading,
                text=c.text,
                page_start=c.page_start,
                page_end=c.page_end,
                clause_type=c.clause_type,
                summary=c.summary,
                risk_level=risk_lvl,
            )
        )
    return result


@router.get("/versions/{vid}/key-terms", response_model=List[KeyTermResponse])
def get_version_key_terms(
    vid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding_repo = FindingRepository(db)
    key_terms = finding_repo.get_key_terms(vid)
    result = []
    for kt in key_terms:
        c_no = kt.clause.clause_no if kt.clause else None
        result.append(
            KeyTermResponse(
                id=kt.id,
                clause_id=kt.clause_id,
                clause_no=c_no,
                kind=kt.kind,
                raw_text=kt.raw_text,
                value_number=float(kt.value_number) if kt.value_number is not None else None,
                value_unit=kt.value_unit,
                value_date=kt.value_date,
                computed=kt.computed,
            )
        )
    return result


@router.get("/versions/{vid}/risk", response_model=RiskAnalysisResponse)
def get_version_risk(
    vid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    finding_repo = FindingRepository(db)

    version = contract_repo.get_version(vid)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    findings = finding_repo.get_findings(vid)
    party_role = version.contract.party_role if version.contract else "tenant"

    findings_data = [
        {
            "id": f.id,
            "clause_id": f.clause_id,
            "severity": f.severity,
            "category": f.category,
            "reason": f.reason,
            "score": float(f.score),
        }
        for f in findings
    ]

    calc = calculate_overall_contract_risk(findings_data, party_role=party_role)

    # Convert to response
    findings_resp = [
        FindingResponse(
            id=f.id,
            clause_id=f.clause_id,
            clause_no=f.clause.clause_no if f.clause else None,
            heading=f.clause.heading if f.clause else None,
            original_text=f.clause.text if f.clause else None,
            severity=f.severity,
            category=f.category,
            reason=f.reason,
            standard_term_ref=f.standard_term_ref,
            score=float(f.score),
        )
        for f in findings
    ]

    breakdown = [
        CategoryBreakdownItem(
            category=b["category"],
            count=b["count"],
            max_severity=b["max_severity"],
            weight=b["weight"],
            score_contribution=b["score_contribution"],
        )
        for b in calc["category_breakdown"]
    ]

    score = float(version.risk_score) if version.risk_score is not None else calc["overall_score"]

    return RiskAnalysisResponse(
        version_id=vid,
        contract_id=version.contract_id,
        overall_score=score,
        risk_level=calc["risk_level"],
        findings=findings_resp,
        category_breakdown=breakdown,
        total_findings=calc["total_findings"],
        critical_count=calc["critical_count"],
        high_count=calc["high_count"],
        medium_count=calc["medium_count"],
        low_count=calc["low_count"],
    )


@router.get("/contracts/{contract_id}/risk-history", response_model=List[RiskHistoryItem])
def get_contract_risk_history(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    history = contract_repo.get_risk_history(contract_id, current_user.id)
    return [RiskHistoryItem(**h) for h in history]
