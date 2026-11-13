import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = Column(String(36), ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    clause_id = Column(String(36), ForeignKey("clauses.id", ondelete="CASCADE"), nullable=False, index=True)
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    category = Column(String(100), nullable=False)  # 'liability', 'termination', 'payment', 'ip', etc.
    reason = Column(Text, nullable=False)
    standard_term_ref = Column(String(36), ForeignKey("kb_documents.id", ondelete="SET NULL"), nullable=True)
    score = Column(Numeric(5, 2), nullable=False)

    version = relationship("ContractVersion", back_populates="findings")
    clause = relationship("Clause", back_populates="findings")
    standard_term = relationship("KBDocument", back_populates="findings")
    suggestions = relationship("Suggestion", back_populates="finding", cascade="all, delete-orphan")
