import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.contract import Contract, ContractVersion
from app.db.repositories.contract_repo import ContractRepository
from app.db.repositories.clause_repo import ClauseRepository
from app.db.repositories.finding_repo import FindingRepository
from app.schemas.contract import (
    ContractResponse,
    ContractDetailResponse,
    VersionResponse,
)
from app.api.deps import get_current_user
from app.services.ingestion.parser import parse_document
from app.services.ingestion.clause_splitter import split_into_clauses
from app.services.ingestion.embedder import get_embedding

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("", response_model=ContractResponse)
async def upload_contract(
    file: UploadFile = File(...),
    title: str = Form(...),
    contract_type: str = Form("rental"),
    party_role: Optional[str] = Form("tenant"),
    jurisdiction: Optional[str] = Form("US"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    clause_repo = ClauseRepository(db)

    # 1. Save uploaded file
    file_id = str(uuid.uuid4())[:8]
    ext = Path(file.filename).suffix.lower()
    saved_filename = f"{file_id}_{file.filename}"
    saved_path = settings.UPLOAD_DIR / saved_filename

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Parse pages
    try:
        pages_data = parse_document(saved_path)
    except Exception as e:
        if saved_path.exists():
            saved_path.unlink()
        raise HTTPException(status_code=400, detail=f"Document parsing error: {e}")

    # 3. Create Contract & Version
    contract = contract_repo.create_contract(
        user_id=current_user.id,
        title=title,
        contract_type=contract_type,
        party_role=party_role,
        jurisdiction=jurisdiction,
    )
    version = contract_repo.create_version(
        contract_id=contract.id,
        version=1,
        filename=file.filename,
        page_count=len(pages_data),
    )

    # 4. Split into clauses and compute embeddings
    clauses = split_into_clauses(pages_data)
    clauses_to_insert = []
    for c in clauses:
        emb = get_embedding(c["text"])
        clauses_to_insert.append({
            "version_id": version.id,
            "clause_no": c.get("clause_no"),
            "heading": c.get("heading"),
            "text": c["text"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "embedding": emb,
        })

    clause_repo.add_clauses_batch(clauses_to_insert)

    return ContractResponse(
        id=contract.id,
        title=contract.title,
        contract_type=contract.contract_type,
        party_role=contract.party_role,
        jurisdiction=contract.jurisdiction,
        current_version=contract.current_version,
        created_at=contract.created_at,
        latest_risk_score=None,
        next_deadline=None,
        versions_count=1,
    )


@router.get("", response_model=List[ContractResponse])
def list_contracts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    contracts = contract_repo.list_contracts(current_user.id)
    response = []

    for c in contracts:
        latest_v = (
            db.query(ContractVersion)
            .filter(ContractVersion.contract_id == c.id)
            .order_by(ContractVersion.version.desc())
            .first()
        )
        score = float(latest_v.risk_score) if (latest_v and latest_v.risk_score is not None) else None
        
        # Check for upcoming computed deadline
        finding_repo = FindingRepository(db)
        key_terms = finding_repo.get_key_terms(latest_v.id) if latest_v else []
        deadline_str = None
        for kt in key_terms:
            if kt.kind == "computed_notice_deadline" and kt.computed and "deadline_date" in kt.computed:
                deadline_str = kt.computed["deadline_date"]
                break

        response.append(
            ContractResponse(
                id=c.id,
                title=c.title,
                contract_type=c.contract_type,
                party_role=c.party_role,
                jurisdiction=c.jurisdiction,
                current_version=c.current_version,
                created_at=c.created_at,
                latest_risk_score=score,
                next_deadline=deadline_str,
                versions_count=len(c.versions),
            )
        )
    return response


@router.get("/{contract_id}", response_model=ContractDetailResponse)
def get_contract_detail(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    contract = contract_repo.get_contract(contract_id, current_user.id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    versions_resp = [
        VersionResponse(
            id=v.id,
            version=v.version,
            filename=v.filename,
            page_count=v.page_count,
            risk_score=float(v.risk_score) if v.risk_score is not None else None,
            uploaded_at=v.uploaded_at,
        )
        for v in contract.versions
    ]

    latest_v = contract.versions[-1] if contract.versions else None
    latest_score = float(latest_v.risk_score) if (latest_v and latest_v.risk_score is not None) else None

    contract_resp = ContractResponse(
        id=contract.id,
        title=contract.title,
        contract_type=contract.contract_type,
        party_role=contract.party_role,
        jurisdiction=contract.jurisdiction,
        current_version=contract.current_version,
        created_at=contract.created_at,
        latest_risk_score=latest_score,
        next_deadline=None,
        versions_count=len(contract.versions),
    )

    return ContractDetailResponse(
        contract=contract_resp,
        versions=versions_resp,
        current_version_id=latest_v.id if latest_v else "",
    )


@router.post("/{contract_id}/versions", response_model=VersionResponse)
async def upload_contract_version(
    contract_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    clause_repo = ClauseRepository(db)

    contract = contract_repo.get_contract(contract_id, current_user.id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    new_version_num = contract.current_version + 1

    file_id = str(uuid.uuid4())[:8]
    saved_filename = f"v{new_version_num}_{file_id}_{file.filename}"
    saved_path = settings.UPLOAD_DIR / saved_filename

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        pages_data = parse_document(saved_path)
    except Exception as e:
        if saved_path.exists():
            saved_path.unlink()
        raise HTTPException(status_code=400, detail=f"Document parsing error: {e}")

    version = contract_repo.create_version(
        contract_id=contract.id,
        version=new_version_num,
        filename=file.filename,
        page_count=len(pages_data),
    )

    clauses = split_into_clauses(pages_data)
    clauses_to_insert = []
    for c in clauses:
        emb = get_embedding(c["text"])
        clauses_to_insert.append({
            "version_id": version.id,
            "clause_no": c.get("clause_no"),
            "heading": c.get("heading"),
            "text": c["text"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "embedding": emb,
        })
    clause_repo.add_clauses_batch(clauses_to_insert)

    return VersionResponse(
        id=version.id,
        version=version.version,
        filename=version.filename,
        page_count=version.page_count,
        risk_score=None,
        uploaded_at=version.uploaded_at,
    )


@router.delete("/{contract_id}")
def delete_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract_repo = ContractRepository(db)
    success = contract_repo.delete_contract(contract_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"message": "Contract and all associated data deleted successfully"}
