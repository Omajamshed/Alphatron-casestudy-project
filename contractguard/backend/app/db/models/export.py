import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class Export(Base):
    __tablename__ = "exports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(20), nullable=False)  # 'email', 'pdf', 'docx'
    content = Column(Text, nullable=True)      # for email text/markdown
    file_path = Column(String(500), nullable=True)  # for generated PDF or DOCX file
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    agent_run = relationship("AgentRun", back_populates="exports")
