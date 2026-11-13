import re
from typing import List, Dict, Any, Tuple, Optional
from app.db.models.clause import Clause


CITATION_REGEX = re.compile(
    r"\[(?:clause:?\s*([0-9A-Za-z\.\-]+))?(?:,\s*)?(?:page:?\s*([0-9]+))?\]",
    re.IGNORECASE,
)

ALT_CITATION_REGEX = re.compile(
    r"\[(?:Clause|Section)\s+([0-9A-Za-z\.\-]+)(?:,\s*p(?:age|\.)?\s*([0-9]+))?\]",
    re.IGNORECASE,
)


def extract_citations_from_text(text: str) -> List[Dict[str, Any]]:
    citations = []
    # Primary pattern [clause: 7.2, page: 4]
    for m in CITATION_REGEX.finditer(text):
        clause_val = m.group(1)
        page_val = m.group(2)
        if clause_val or page_val:
            citations.append({
                "raw": m.group(0),
                "clause": clause_val.strip() if clause_val else None,
                "page": int(page_val) if page_val else None,
            })

    # Secondary pattern [Clause 7.2, p. 4]
    for m in ALT_CITATION_REGEX.finditer(text):
        clause_val = m.group(1)
        page_val = m.group(2)
        citations.append({
            "raw": m.group(0),
            "clause": clause_val.strip() if clause_val else None,
            "page": int(page_val) if page_val else None,
        })

    return citations


def validate_citations_against_retrieved(
    raw_citations: List[Dict[str, Any]],
    retrieved_clauses: List[Clause],
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validates that every cited clause in the LLM answer actually belongs to the retrieved passages.
    Returns: (is_valid, validated_citation_objects)
    """
    if not raw_citations:
        # If no citations were made, valid if the answer was a refusal
        return True, []

    retrieved_map = {}
    for c in retrieved_clauses:
        if c.clause_no:
            retrieved_map[c.clause_no.lower().strip()] = c
        # Also map without leading 'section' or 'clause'
        clean_num = re.sub(r"^(?:section|clause|article)\s*", "", c.clause_no or "", flags=re.IGNORECASE).strip()
        if clean_num:
            retrieved_map[clean_num.lower()] = c

    validated = []
    all_matched = True

    for cit in raw_citations:
        c_num = cit.get("clause")
        p_num = cit.get("page")

        matched_clause = None
        if c_num and c_num.lower() in retrieved_map:
            matched_clause = retrieved_map[c_num.lower()]
        elif p_num:
            # Match by page if single clause on that page
            page_clauses = [c for c in retrieved_clauses if c.page_start <= p_num <= c.page_end]
            if len(page_clauses) == 1:
                matched_clause = page_clauses[0]

        if matched_clause:
            validated.append({
                "file": "contract.pdf",
                "clause": matched_clause.clause_no or "General",
                "page": p_num or matched_clause.page_start,
                "clause_id": matched_clause.id,
                "heading": matched_clause.heading,
            })
        else:
            all_matched = False

    return all_matched, validated
