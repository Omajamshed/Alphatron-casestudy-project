import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = Column(String(36), ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    clause_no = Column(String(50), nullable=True)  # e.g. "7.2" or "Section 4"
    heading = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    page_start = Column(Integer, default=1)
    page_end = Column(Integer, default=1)
    clause_type = Column(String(100), nullable=True)  # termination, payment, liability, ip, etc.
    summary = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)  # List of floats (384 dims)

    version = relationship("ContractVersion", back_populates="clauses")
    key_terms = relationship("KeyTerm", back_populates="clause", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="clause", cascade="all, delete-orphan")
