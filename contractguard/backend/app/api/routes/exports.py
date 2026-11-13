from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.repositories.finding_repo import FindingRepository
from app.db.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/{export_id}/download")
def download_export_file(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    finding_repo = FindingRepository(db)
    exp = finding_repo.get_export(export_id)
    if not exp or not exp.file_path:
        raise HTTPException(status_code=404, detail="Export file not found")

    file_path = Path(exp.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File on disk not found")

    media_type = "application/pdf" if exp.kind == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type=media_type,
    )
