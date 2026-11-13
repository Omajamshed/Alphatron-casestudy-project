import uuid
from app.services.ingestion.clause_splitter import split_into_clauses
from app.db.repositories.contract_repo import ContractRepository
from app.db.repositories.clause_repo import ClauseRepository
from app.agents.nodes.extract_clauses import extract_clauses


def test_upload_pipeline_flow(db_session, test_user):
    contract_repo = ContractRepository(db_session)
    clause_repo = ClauseRepository(db_session)

    # 1. Create contract & version
    contract = contract_repo.create_contract(
        user_id=test_user.id,
        title="Residential Lease Agreement",
        contract_type="rental",
        party_role="tenant",
    )
    version = contract_repo.create_version(
        contract_id=contract.id,
        version=1,
        filename="lease.txt",
        page_count=2,
    )

    # 2. Simulate parsed document pages
    pages_data = [
        {
            "page": 1,
            "text": "1.0 Term. The lease shall commence on January 1, 2026 and expire on December 31, 2026.\n"
                    "2.0 Rent. Monthly rent shall be $2,000.00 due on the 1st day of each month.",
        },
        {
            "page": 2,
            "text": "3.0 Termination. Either party may terminate with thirty (30) days notice.\n"
                    "4.0 Liability. Tenant agrees to hold harmless landlord with unlimited liability.",
        },
    ]

    # 3. Split into clauses
    clauses = split_into_clauses(pages_data)
    assert len(clauses) >= 4

    clauses_db = []
    for c in clauses:
        clauses_db.append({
            "version_id": version.id,
            "clause_no": c.get("clause_no"),
            "heading": c.get("heading"),
            "text": c["text"],
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "embedding": [0.1] * 384,
        })
    clause_repo.add_clauses_batch(clauses_db)

    # 4. Run rule extractor node
    state = {"version_id": version.id}
    res = extract_clauses(state)

    assert "clauses" in res
    assert "key_terms" in res
    assert len(res["key_terms"]) > 0
