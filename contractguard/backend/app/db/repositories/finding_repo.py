import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.key_term import KeyTerm
from app.db.models.finding import Finding
from app.db.models.suggestion import Suggestion
from app.db.models.agent_run import AgentRun
from app.db.models.export import Export
from app.db.models.usage_log import UsageLog


class FindingRepository:
    def __init__(self, db: Session):
        self.db = db

    # Key terms
    def add_key_terms_batch(self, terms: List[dict]) -> List[KeyTerm]:
        created = []
        for t in terms:
            kt = KeyTerm(
                id=str(uuid.uuid4()),
                version_id=t["version_id"],
                clause_id=t.get("clause_id"),
                kind=t["kind"],
                raw_text=t.get("raw_text"),
                value_number=t.get("value_number"),
                value_unit=t.get("value_unit"),
                value_date=t.get("value_date"),
                computed=t.get("computed"),
            )
            self.db.add(kt)
            created.append(kt)
        self.db.commit()
        return created

    def get_key_terms(self, version_id: str) -> List[KeyTerm]:
        return self.db.query(KeyTerm).filter(KeyTerm.version_id == version_id).all()

    # Findings
    def add_findings_batch(self, findings_data: List[dict]) -> List[Finding]:
        created = []
        for f in findings_data:
            finding = Finding(
                id=f.get("id") or str(uuid.uuid4()),
                version_id=f["version_id"],
                clause_id=f["clause_id"],
                severity=f["severity"],
                category=f["category"],
                reason=f["reason"],
                standard_term_ref=f.get("standard_term_ref"),
                score=f["score"],
            )
            self.db.add(finding)
            created.append(finding)
        self.db.commit()
        return created

    def get_findings(self, version_id: str) -> List[Finding]:
        return self.db.query(Finding).filter(Finding.version_id == version_id).all()

    # Suggestions
    def add_suggestions_batch(self, suggestions_data: List[dict]) -> List[Suggestion]:
        created = []
        for s in suggestions_data:
            sug = Suggestion(
                id=s.get("id") or str(uuid.uuid4()),
                finding_id=s["finding_id"],
                run_id=s.get("run_id"),
                original_text=s["original_text"],
                proposed_text=s["proposed_text"],
                rationale=s["rationale"],
                status=s.get("status", "pending"),
                final_text=s.get("final_text"),
            )
            self.db.add(sug)
            created.append(sug)
        self.db.commit()
        return created

    def get_suggestions_by_run(self, run_id: str) -> List[Suggestion]:
        return self.db.query(Suggestion).filter(Suggestion.run_id == run_id).all()

    def get_suggestion(self, suggestion_id: str) -> Optional[Suggestion]:
        return self.db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()

    def update_suggestion_decision(
        self,
        suggestion_id: str,
        status: str,
        final_text: Optional[str] = None,
    ) -> Optional[Suggestion]:
        sug = self.get_suggestion(suggestion_id)
        if sug:
            sug.status = status
            sug.final_text = final_text or sug.proposed_text
            sug.decided_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(sug)
        return sug

    # Agent runs
    def create_agent_run(self, version_id: str, thread_id: str, status: str = "running") -> AgentRun:
        run = AgentRun(
            id=str(uuid.uuid4()),
            version_id=version_id,
            thread_id=thread_id,
            status=status,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_agent_run(self, run_id: str) -> Optional[AgentRun]:
        return self.db.query(AgentRun).filter(AgentRun.id == run_id).first()

    def get_agent_run_by_thread(self, thread_id: str) -> Optional[AgentRun]:
        return self.db.query(AgentRun).filter(AgentRun.thread_id == thread_id).first()

    def update_agent_run_status(self, run_id: str, status: str) -> Optional[AgentRun]:
        run = self.get_agent_run(run_id)
        if run:
            run.status = status
            self.db.commit()
            self.db.refresh(run)
        return run

    # Exports
    def create_export(self, run_id: str, kind: str, content: Optional[str] = None, file_path: Optional[str] = None) -> Export:
        exp = Export(
            id=str(uuid.uuid4()),
            run_id=run_id,
            kind=kind,
            content=content,
            file_path=file_path,
        )
        self.db.add(exp)
        self.db.commit()
        self.db.refresh(exp)
        return exp

    def get_exports_by_run(self, run_id: str) -> List[Export]:
        return self.db.query(Export).filter(Export.run_id == run_id).all()

    def get_export(self, export_id: str) -> Optional[Export]:
        return self.db.query(Export).filter(Export.id == export_id).first()

    # Usage logs
    def log_usage(
        self,
        feature: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: int,
        user_id: Optional[str] = None,
        cost_usd: float = 0.0,
    ) -> UsageLog:
        log = UsageLog(
            user_id=user_id,
            feature=feature,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_usage_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        query = self.db.query(UsageLog)
        if user_id:
            query = query.filter(UsageLog.user_id == user_id)
        logs = query.all()

        total_tokens_in = sum(l.tokens_in for l in logs)
        total_tokens_out = sum(l.tokens_out for l in logs)
        total_cost = sum(float(l.cost_usd or 0) for l in logs)
        avg_latency = (
            sum(l.latency_ms for l in logs) / len(logs) if logs else 0
        )

        by_feature = {}
        for l in logs:
            if l.feature not in by_feature:
                by_feature[l.feature] = {"calls": 0, "tokens": 0, "cost": 0.0}
            by_feature[l.feature]["calls"] += 1
            by_feature[l.feature]["tokens"] += (l.tokens_in + l.tokens_out)
            by_feature[l.feature]["cost"] += float(l.cost_usd or 0)

        return {
            "total_calls": len(logs),
            "total_tokens_in": total_tokens_in,
            "total_tokens_out": total_tokens_out,
            "total_tokens": total_tokens_in + total_tokens_out,
            "total_cost_usd": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 1),
            "by_feature": by_feature,
        }

    def get_history_logs(self, user_id: Optional[str] = None, limit: int = 50) -> List[dict]:
        query = self.db.query(UsageLog)
        if user_id:
            query = query.filter(UsageLog.user_id == user_id)
        logs = query.order_by(UsageLog.created_at.desc()).limit(limit).all()
        return [
            {
                "id": l.id,
                "feature": l.feature,
                "tokens_in": l.tokens_in,
                "tokens_out": l.tokens_out,
                "latency_ms": l.latency_ms,
                "cost_usd": float(l.cost_usd or 0),
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ]
