import json
import uuid
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, init_db
from app.db.models.kb_document import KBDocument
from app.services.ingestion.embedder import get_embedding

SEED_DIR = Path(__file__).resolve().parent / "seed"


def seed_kb(db: Session):
    init_db()
    json_files = list(SEED_DIR.glob("*.json"))
    total_added = 0

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            items = json.load(f)

        for item in items:
            title = item.get("title")
            existing = db.query(KBDocument).filter(KBDocument.title == title).first()
            if existing:
                continue

            content = item.get("content", "")
            embedding = get_embedding(content)

            kb_doc = KBDocument(
                id=str(uuid.uuid4()),
                contract_type=item.get("contract_type", "all"),
                jurisdiction=item.get("jurisdiction", "all"),
                category=item.get("category", "general"),
                title=title,
                content=content,
                source=item.get("source"),
                embedding=embedding,
            )
            db.add(kb_doc)
            total_added += 1

    db.commit()
    print(f"Successfully seeded {total_added} knowledge base documents.")
    return total_added


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_kb(db)
    finally:
        db.close()
