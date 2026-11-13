import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    contract_type = Column(String(50), nullable=False)  # 'rental', 'freelance', 'employment', 'other'
    party_role = Column(String(50), nullable=True)     # 'tenant', 'freelancer', 'employee'
    jurisdiction = Column(String(100), nullable=True)
    current_version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="contracts")
    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan", order_by="ContractVersion.version")


class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    filename = Column(String(255), nullable=True)
    page_count = Column(Integer, default=1)
    risk_score = Column(Numeric(5, 2), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("contract_id", "version", name="uq_contract_version"),
    )

    contract = relationship("Contract", back_populates="versions")
    clauses = relationship("Clause", back_populates="version", cascade="all, delete-orphan")
    key_terms = relationship("KeyTerm", back_populates="version", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="version", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="version", cascade="all, delete-orphan")
