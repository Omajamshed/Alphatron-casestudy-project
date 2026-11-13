from typing import Dict, Any
from langgraph.types import interrupt
from app.db.session import SessionLocal
from app.db.repositories.finding_repo import FindingRepository


def human_review(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pauses graph execution via interrupt, returning pending counter-clause suggestions.
    Resumes when user submits decisions (approved, edited, rejected).
    """
    suggestions = state.get("suggestions", [])
    version_id = state.get("version_id")

    # Persist suggestions to DB if not already present
    db = SessionLocal()
    try:
        finding_repo = FindingRepository(db)
        # Check if already saved
        for s in suggestions:
            existing = finding_repo.get_suggestion(s["id"])
            if not existing:
                finding_repo.add_suggestions_batch([s])
    finally:
        db.close()

    # Pause execution until user reviews
    decisions = interrupt({
        "version_id": version_id,
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
        "message": "Human review required: Please approve, edit, or reject the proposed counter-clauses.",
    })

    return {
        "decisions": decisions or {},
        "status": "review_completed",
    }
