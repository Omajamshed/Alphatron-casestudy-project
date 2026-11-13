import re
from typing import List, Dict, Any

HEADING_PATTERNS = [
    # E.g., "Section 7.2 Termination" or "Article IV: Term" or "Clause 3 - Payment"
    re.compile(
        r"^(?:Section|Article|Clause|Paragraph)\s+([0-9A-Za-z\.\-]+)(?:[:\.\-\s]+(.*))?$",
        re.IGNORECASE,
    ),
    # E.g., "7.2 Rent Escalation" or "1. Term of Lease"
    re.compile(r"^([0-9]{1,2}(?:\.[0-9]{1,2}){0,3})\.?\s+([A-Z0-9].*)$"),
    # E.g., "1. " or "2. " followed by text
    re.compile(r"^([0-9]{1,2})\.\s+(.*)$"),
]


def split_into_clauses(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Segments document pages into structured clauses with clause_no, heading,
    full text, page_start, and page_end.
    """
    raw_clauses = []
    current_clause = None

    for page_info in pages_data:
        page_num = page_info["page"]
        text = page_info["text"]
        lines = text.split("\n")

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                if current_clause and current_clause["text"]:
                    current_clause["text"] += "\n"
                continue

            matched = False
            for pattern in HEADING_PATTERNS:
                m = pattern.match(trimmed)
                if m:
                    clause_no = m.group(1).strip()
                    heading_text = (m.group(2) or "").strip() if len(m.groups()) >= 2 else ""

                    # Save existing clause
                    if current_clause and current_clause["text"].strip():
                        current_clause["text"] = current_clause["text"].strip()
                        raw_clauses.append(current_clause)

                    current_clause = {
                        "clause_no": clause_no,
                        "heading": heading_text or f"Clause {clause_no}",
                        "text": trimmed + "\n",
                        "page_start": page_num,
                        "page_end": page_num,
                    }
                    matched = True
                    break

            if not matched:
                if current_clause is None:
                    # Initial preamble / title section before first clause
                    current_clause = {
                        "clause_no": "Preamble",
                        "heading": "Recitals & Preamble",
                        "text": trimmed + "\n",
                        "page_start": page_num,
                        "page_end": page_num,
                    }
                else:
                    current_clause["text"] += trimmed + " "
                    current_clause["page_end"] = page_num

    if current_clause and current_clause["text"].strip():
        current_clause["text"] = current_clause["text"].strip()
        raw_clauses.append(current_clause)

    # Fallback: if fewer than 2 clauses detected, segment by paragraphs with overlap
    if len(raw_clauses) <= 1:
        fallback_clauses = []
        for page_info in pages_data:
            page_num = page_info["page"]
            paras = [p.strip() for p in page_info["text"].split("\n\n") if p.strip()]
            for idx, p in enumerate(paras):
                fallback_clauses.append({
                    "clause_no": f"Para {len(fallback_clauses) + 1}",
                    "heading": f"Paragraph {len(fallback_clauses) + 1}",
                    "text": p,
                    "page_start": page_num,
                    "page_end": page_num,
                })
        if fallback_clauses:
            return fallback_clauses

    return raw_clauses
