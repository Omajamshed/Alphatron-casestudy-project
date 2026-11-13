from datetime import datetime, timezone
from sqlalchemy import Column, Integer, BigInteger, String, Numeric, DateTime
from app.db.base import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=True, index=True)
    feature = Column(String(100), nullable=False)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    cost_usd = Column(Numeric(8, 5), default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
