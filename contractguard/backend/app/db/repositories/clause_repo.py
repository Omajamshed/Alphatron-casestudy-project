import uuid
import math
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models.clause import Clause
from app.db.models.kb_document import KBDocument


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class ClauseRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_clause(
        self,
        version_id: str,
        clause_no: Optional[str],
        heading: Optional[str],
        text: str,
        page_start: int,
        page_end: int,
        clause_type: Optional[str] = None,
        summary: Optional[str] = None,
        embedding: Optional[List[float]] = None,
    ) -> Clause:
        clause = Clause(
            id=str(uuid.uuid4()),
            version_id=version_id,
            clause_no=clause_no,
            heading=heading,
            text=text,
            page_start=page_start,
            page_end=page_end,
            clause_type=clause_type,
            summary=summary,
            embedding=embedding,
        )
        self.db.add(clause)
        self.db.commit()
        self.db.refresh(clause)
        return clause

    def add_clauses_batch(self, clauses_data: List[dict]) -> List[Clause]:
        created = []
        for c in clauses_data:
            clause = Clause(
                id=c.get("id") or str(uuid.uuid4()),
                version_id=c["version_id"],
                clause_no=c.get("clause_no"),
                heading=c.get("heading"),
                text=c["text"],
                page_start=c.get("page_start", 1),
                page_end=c.get("page_end", 1),
                clause_type=c.get("clause_type"),
                summary=c.get("summary"),
                embedding=c.get("embedding"),
            )
            self.db.add(clause)
            created.append(clause)
        self.db.commit()
        return created

    def get_clauses_by_version(self, version_id: str) -> List[Clause]:
        return (
            self.db.query(Clause)
            .filter(Clause.version_id == version_id)
            .order_by(Clause.page_start.asc(), Clause.clause_no.asc())
            .all()
        )

    def get_clause(self, clause_id: str) -> Optional[Clause]:
        return self.db.query(Clause).filter(Clause.id == clause_id).first()

    def update_clause_metadata(
        self,
        clause_id: str,
        clause_type: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> Optional[Clause]:
        clause = self.get_clause(clause_id)
        if clause:
            if clause_type is not None:
                clause.clause_type = clause_type
            if summary is not None:
                clause.summary = summary
            self.db.commit()
            self.db.refresh(clause)
        return clause

    def search_clauses(
        self,
        version_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[Tuple[Clause, float]]:
        clauses = self.get_clauses_by_version(version_id)
        scored = []
        for c in clauses:
            if c.embedding:
                score = cosine_similarity(query_embedding, c.embedding)
                if score >= threshold:
                    scored.append((c, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def search_kb(
        self,
        query_embedding: List[float],
        contract_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        top_k: int = 4,
        threshold: float = 0.0,
    ) -> List[Tuple[KBDocument, float]]:
        query = self.db.query(KBDocument)
        if contract_type:
            query = query.filter(
                (KBDocument.contract_type == contract_type) | (KBDocument.contract_type == "all")
            )
        if jurisdiction:
            query = query.filter(
                (KBDocument.jurisdiction == jurisdiction) | (KBDocument.jurisdiction == "all") | (KBDocument.jurisdiction.is_(None))
            )
        kb_docs = query.all()
        scored = []
        for doc in kb_docs:
            if doc.embedding:
                score = cosine_similarity(query_embedding, doc.embedding)
                if score >= threshold:
                    scored.append((doc, score))
            else:
                # If no embedding, fallback moderate score
                scored.append((doc, 0.40))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
