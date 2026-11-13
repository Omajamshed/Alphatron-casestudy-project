from typing import Optional
from sqlalchemy.orm import Session
from app.db.repositories.finding_repo import FindingRepository
from app.core.logging import log_llm_call


def track_llm_usage(
    feature: str,
    tokens_in: int,
    tokens_out: int,
    latency_ms: int,
    user_id: Optional[str] = None,
    db: Optional[Session] = None,
    contract_id: str = "",
) -> float:
    """
    Computes cost estimate and logs usage to DB and logger.
    Gemini 2.5/3.5 Flash pricing benchmark: ~$0.15 / 1M tokens in, $0.60 / 1M tokens out.
    """
    cost_in = (tokens_in / 1_000_000) * 0.15
    cost_out = (tokens_out / 1_000_000) * 0.60
    total_cost = round(cost_in + cost_out, 6)

    log_llm_call(
        feature=feature,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        contract_id=contract_id,
    )

    if db:
        try:
            repo = FindingRepository(db)
            repo.log_usage(
                feature=feature,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=latency_ms,
                user_id=user_id,
                cost_usd=total_cost,
            )
        except Exception:
            pass

    return total_cost
