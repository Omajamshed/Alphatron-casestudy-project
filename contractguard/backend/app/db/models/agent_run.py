import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = Column(String(36), ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    thread_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), default="running")  # 'running', 'awaiting_review', 'completed', 'failed'
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    version = relationship("ContractVersion", back_populates="agent_runs")
    suggestions = relationship("Suggestion", back_populates="agent_run")
    exports = relationship("Export", back_populates="agent_run", cascade="all, delete-orphan")
