import re
from typing import List, Dict, Any, Optional
from app.services.rules.durations import extract_durations_from_clause

AUTO_RENEWAL_KEYWORDS = [
    r"automatic(?:ally)?\s+renew(?:s|ed|al)?",
    r"successive\s+periods\s+of",
    r"extend\s+automatically",
    r"continuation\s+of\s+term",
]

ESCALATION_KEYWORDS = [
    r"(?:annual|yearly)\s+increase\s+of\s*([0-9]+(?:\.[0-9]+)?)\s*%",
    r"rent\s+(?:shall\s+)?increase\s+by\s*([0-9]+(?:\.[0-9]+)?)\s*%",
    r"escalat(?:e|ion)\s+(?:by|of)?\s*([0-9]+(?:\.[0-9]+)?)\s*%",
]


def extract_renewal_terms_from_clause(clause_text: str, clause_id: Optional[str] = None) -> List[Dict[str, Any]]:
    results = []

    # Check auto-renewal
    for kw in AUTO_RENEWAL_KEYWORDS:
        m = re.search(rf"(?i){kw}", clause_text)
        if m:
            # Check if duration is specified
            durations = extract_durations_from_clause(clause_text, clause_id)
            cancellation_notice = 30  # default assumption
            for d in durations:
                if d["kind"] == "notice_period":
                    cancellation_notice = int(d.get("days_equivalent") or d["value_number"])
                    break

            results.append({
                "kind": "auto_renewal",
                "raw_text": m.group(0),
                "value_unit": "flag",
                "is_auto_renew": True,
                "cancellation_notice_days": cancellation_notice,
                "confidence": "high",
                "clause_id": clause_id,
            })
            break

    # Check escalation
    for kw in ESCALATION_KEYWORDS:
        m = re.search(rf"(?i){kw}", clause_text)
        if m:
            pct = float(m.group(1))
            results.append({
                "kind": "rent_escalation_rate",
                "raw_text": m.group(0),
                "value_number": pct,
                "value_unit": "percent",
                "confidence": "high",
                "clause_id": clause_id,
            })
            break

    return results
