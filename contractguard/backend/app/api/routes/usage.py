from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.db.repositories.finding_repo import FindingRepository
from app.api.deps import get_current_user

router = APIRouter(tags=["usage"])


@router.get("/usage")
def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding_repo = FindingRepository(db)
    return finding_repo.get_usage_summary(user_id=current_user.id)


@router.get("/history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding_repo = FindingRepository(db)
    return finding_repo.get_history_logs(user_id=current_user.id, limit=50)
