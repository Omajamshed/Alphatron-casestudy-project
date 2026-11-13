import uuid
from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class KBDocument(Base):
    __tablename__ = "kb_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_type = Column(String(50), nullable=False)  # 'rental', 'freelance', 'employment'
    jurisdiction = Column(String(100), nullable=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    embedding = Column(JSON, nullable=True)

    findings = relationship("Finding", back_populates="standard_term")
