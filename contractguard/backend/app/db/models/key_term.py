import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class KeyTerm(Base):
    __tablename__ = "key_terms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = Column(String(36), ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    clause_id = Column(String(36), ForeignKey("clauses.id", ondelete="SET NULL"), nullable=True, index=True)
    kind = Column(String(100), nullable=False)  # start_date, end_date, notice_period, late_fee, deposit, etc.
    raw_text = Column(Text, nullable=True)
    value_number = Column(Numeric(14, 2), nullable=True)
    value_unit = Column(String(50), nullable=True)  # USD, days, %, etc.
    value_date = Column(Date, nullable=True)
    computed = Column(JSON, nullable=True)  # {deadlines: ..., exposure: ..., formula: ...}

    version = relationship("ContractVersion", back_populates="key_terms")
    clause = relationship("Clause", back_populates="key_terms")
