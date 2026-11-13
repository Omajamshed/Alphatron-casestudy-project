from app.services.rag.citation_validator import (
    extract_citations_from_text,
    validate_citations_against_retrieved,
)
from app.db.models.clause import Clause


def test_extract_citations():
    text = "Under the agreement, rent increases are limited [clause: 7.2, page: 4] and notice is required [Clause 12.1, p. 6]."
    citations = extract_citations_from_text(text)

    assert len(citations) >= 2
    assert citations[0]["clause"] == "7.2"
    assert citations[0]["page"] == 4
    assert citations[1]["clause"] == "12.1"
    assert citations[1]["page"] == 6


def test_validate_citations_match_retrieved():
    c1 = Clause(id="id-1", clause_no="7.2", page_start=4, page_end=4, text="Rent clause")
    c2 = Clause(id="id-2", clause_no="8.0", page_start=5, page_end=5, text="Deposit clause")

    raw_cits = [{"clause": "7.2", "page": 4}]
    is_valid, validated = validate_citations_against_retrieved(raw_cits, [c1, c2])

    assert is_valid is True
    assert len(validated) == 1
    assert validated[0]["clause_id"] == "id-1"


def test_unmatched_citations_flagged():
    c1 = Clause(id="id-1", clause_no="7.2", page_start=4, page_end=4, text="Rent clause")

    # Cited clause 99.9 which does not exist in retrieved clauses
    raw_cits = [{"clause": "99.9", "page": 10}]
    is_valid, validated = validate_citations_against_retrieved(raw_cits, [c1])

    assert is_valid is False
    assert len(validated) == 0
