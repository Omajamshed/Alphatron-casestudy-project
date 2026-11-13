import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.contract import Contract, ContractVersion


class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_contract(
        self,
        user_id: str,
        title: str,
        contract_type: str,
        party_role: Optional[str] = None,
        jurisdiction: Optional[str] = None,
    ) -> Contract:
        contract = Contract(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            contract_type=contract_type,
            party_role=party_role,
            jurisdiction=jurisdiction,
            current_version=1,
        )
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def list_contracts(self, user_id: str) -> List[Contract]:
        return (
            self.db.query(Contract)
            .filter(Contract.user_id == user_id)
            .order_by(Contract.created_at.desc())
            .all()
        )

    def get_contract(self, contract_id: str, user_id: str) -> Optional[Contract]:
        return (
            self.db.query(Contract)
            .filter(Contract.id == contract_id, Contract.user_id == user_id)
            .first()
        )

    def delete_contract(self, contract_id: str, user_id: str) -> bool:
        contract = self.get_contract(contract_id, user_id)
        if not contract:
            return False
        self.db.delete(contract)
        self.db.commit()
        return True

    def create_version(
        self,
        contract_id: str,
        version: int,
        filename: str,
        page_count: int = 1,
        risk_score: Optional[float] = None,
    ) -> ContractVersion:
        cv = ContractVersion(
            id=str(uuid.uuid4()),
            contract_id=contract_id,
            version=version,
            filename=filename,
            page_count=page_count,
            risk_score=risk_score,
        )
        self.db.add(cv)
        # Update current version on contract
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if contract and contract.current_version < version:
            contract.current_version = version
        self.db.commit()
        self.db.refresh(cv)
        return cv

    def get_version(self, version_id: str) -> Optional[ContractVersion]:
        return self.db.query(ContractVersion).filter(ContractVersion.id == version_id).first()

    def update_version_risk(self, version_id: str, score: float) -> Optional[ContractVersion]:
        cv = self.get_version(version_id)
        if cv:
            cv.risk_score = score
            self.db.commit()
            self.db.refresh(cv)
        return cv

    def get_risk_history(self, contract_id: str, user_id: str) -> List[dict]:
        contract = self.get_contract(contract_id, user_id)
        if not contract:
            return []
        versions = (
            self.db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id)
            .order_by(ContractVersion.version.asc())
            .all()
        )
        return [
            {
                "version_id": v.id,
                "version": v.version,
                "filename": v.filename,
                "risk_score": float(v.risk_score) if v.risk_score is not None else None,
                "uploaded_at": v.uploaded_at.isoformat() if v.uploaded_at else None,
            }
            for v in versions
        ]
