import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    finding_id = Column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    original_text = Column(Text, nullable=False)
    proposed_text = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # 'pending', 'approved', 'edited', 'rejected'
    final_text = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)

    finding = relationship("Finding", back_populates="suggestions")
    agent_run = relationship("AgentRun", back_populates="suggestions")
