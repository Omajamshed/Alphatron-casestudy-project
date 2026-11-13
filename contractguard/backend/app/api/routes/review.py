import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from langgraph.types import Command
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.db.repositories.contract_repo import ContractRepository
from app.db.repositories.finding_repo import FindingRepository
from app.schemas.review import (
    ReviewStartResponse,
    ReviewStatusResponse,
    ReviewDecisionsRequest,
    SuggestionResponse,
)
from app.agents.graph import review_graph
from app.api.deps import get_current_user

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/versions/{vid}/review", response_model=ReviewStartResponse)
def start_review_run(
    vid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    finding_repo = FindingRepository(db)

    version = contract_repo.get_version(vid)
    if not version:
        raise HTTPException(status_code=404, detail="Contract version not found")

    contract = version.contract
    thread_id = f"thread_{uuid.uuid4().hex[:10]}"
    config = {"configurable": {"thread_id": thread_id}}

    # Record agent run
    run = finding_repo.create_agent_run(version_id=vid, thread_id=thread_id, status="running")

    # Initial state
    initial_state = {
        "version_id": vid,
        "contract_id": contract.id if contract else "",
        "party_role": contract.party_role if contract else "tenant",
        "contract_type": contract.contract_type if contract else "rental",
    }

    try:
        review_graph.invoke(initial_state, config=config)
    except Exception as e:
        finding_repo.update_agent_run_status(run.id, "failed")
        raise HTTPException(status_code=500, detail=f"Agent review failed: {e}")

    # Inspect state snapshot
    snapshot = review_graph.get_state(config)
    if snapshot.next:
        # Paused at human_review interrupt
        finding_repo.update_agent_run_status(run.id, "awaiting_review")
        status = "awaiting_review"
        msg = "Agent paused at human review: counter-clause suggestions ready for approval."
    else:
        status = "completed"
        finding_repo.update_agent_run_status(run.id, "completed")
        msg = snapshot.values.get("message", "Review completed.")

    return ReviewStartResponse(
        run_id=run.id,
        thread_id=thread_id,
        status=status,
        message=msg,
    )


@router.get("/{run_id}", response_model=ReviewStatusResponse)
def get_review_status(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding_repo = FindingRepository(db)
    run = finding_repo.get_agent_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Review run not found")

    suggestions_db = finding_repo.get_suggestions_by_run(run.id)
    if not suggestions_db:
        # If not linked by run_id, check by finding_id from this version
        from app.db.models.finding import Finding
        from app.db.models.suggestion import Suggestion
        suggestions_db = (
            db.query(Suggestion)
            .join(Finding, Suggestion.finding_id == Finding.id)
            .filter(Finding.version_id == run.version_id)
            .all()
        )

    suggestions_resp = []
    decided_count = 0
    for s in suggestions_db:
        if s.status in ["approved", "edited", "rejected"]:
            decided_count += 1
        clause_no = s.finding.clause.clause_no if (s.finding and s.finding.clause) else None
        suggestions_resp.append(
            SuggestionResponse(
                id=s.id,
                finding_id=s.finding_id,
                clause_id=s.finding.clause_id if s.finding else None,
                clause_no=clause_no,
                original_text=s.original_text,
                proposed_text=s.proposed_text,
                rationale=s.rationale,
                status=s.status,
                final_text=s.final_text,
                category=s.finding.category if s.finding else "general",
                severity=s.finding.severity if s.finding else "medium",
            )
        )

    total_count = len(suggestions_resp)
    pending_count = total_count - decided_count
    progress_pct = (decided_count / total_count * 100.0) if total_count > 0 else 100.0

    return ReviewStatusResponse(
        run_id=run.id,
        thread_id=run.thread_id,
        status=run.status,
        suggestions=suggestions_resp,
        decisions_count=decided_count,
        pending_count=pending_count,
        total_count=total_count,
        progress_percentage=round(progress_pct, 1),
    )


@router.post("/{run_id}/decisions", response_model=ReviewStatusResponse)
def submit_review_decisions(
    run_id: str,
    body: ReviewDecisionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding_repo = FindingRepository(db)
    run = finding_repo.get_agent_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Review run not found")

    config = {"configurable": {"thread_id": run.thread_id}}
    snapshot = review_graph.get_state(config)

    # Convert decisions to dict
    decisions_dict = {
        s_id: {"status": item.status, "final_text": item.final_text}
        for s_id, item in body.decisions.items()
    }

    # Resume graph with decisions
    try:
        review_graph.invoke(Command(resume=decisions_dict), config=config)
        finding_repo.update_agent_run_status(run.id, "completed")
    except Exception as e:
        finding_repo.update_agent_run_status(run.id, "failed")
        raise HTTPException(status_code=500, detail=f"Failed to resume agent: {e}")

    return get_review_status(run_id=run.id, current_user=current_user, db=db)


@router.get("/{run_id}/exports")
def get_review_exports(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding_repo = FindingRepository(db)
    run = finding_repo.get_agent_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Review run not found")

    exports = finding_repo.get_exports_by_run(run.id)
    email_export = next((e for e in exports if e.kind == "email"), None)
    pdf_export = next((e for e in exports if e.kind == "pdf"), None)
    docx_export = next((e for e in exports if e.kind == "docx"), None)

    return {
        "run_id": run.id,
        "email_draft": email_export.content if email_export else None,
        "pdf_download_url": f"/api/v1/exports/{pdf_export.id}/download" if pdf_export else None,
        "docx_download_url": f"/api/v1/exports/{docx_export.id}/download" if docx_export else None,
    }
