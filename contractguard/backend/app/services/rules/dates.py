import re
from datetime import date
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser

# Clean regex without inline flags inside template
DATE_REGEX = r"""(?:
    \d{4}[-/]\d{1,2}[-/]\d{1,2}
    |
    \d{1,2}[-/]\d{1,2}[-/]\d{2,4}
    |
    (?:(?:1st|2nd|3rd|\d{1,2}th|\d{1,2})\s+(?:of\s+)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[,\s]+\d{4})
    |
    (?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(?:1st|2nd|3rd|\d{1,2}th|\d{1,2})[,\s]+\d{4})
)"""

START_KEYWORDS = [
    r"commenc(?:e|ing|es)\s+on",
    r"effective\s+(?:date|as\s+of)",
    r"start(?:ing)?\s+date",
    r"term\s+shall\s+begin",
    r"beginning\s+on",
]

END_KEYWORDS = [
    r"expir(?:e|ing|es|ation)\s+(?:on|date)?",
    r"terminat(?:e|ing|es|ion)\s+(?:on|date)?",
    r"end(?:ing)?\s+date",
    r"term\s+shall\s+end",
    r"through\s+and\s+including",
]

SIGNING_KEYWORDS = [
    r"signed\s+(?:on|this)?",
    r"executed\s+(?:on|this)?",
    r"dated\s+as\s+of",
    r"date\s+of\s+execution",
]


def _clean_ordinal(text: str) -> str:
    return re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text, flags=re.IGNORECASE)


def parse_raw_date(date_str: str) -> Optional[date]:
    cleaned = _clean_ordinal(date_str.strip())
    cleaned = re.sub(r"\bof\b", "", cleaned, flags=re.IGNORECASE)
    try:
        dt = date_parser.parse(cleaned, fuzzy=True)
        return dt.date()
    except Exception:
        return None


def extract_dates_from_clause(clause_text: str, clause_id: Optional[str] = None) -> List[Dict[str, Any]]:
    results = []

    # 1. Search for start date
    for kw in START_KEYWORDS:
        pattern = rf"(?:{kw})\s*[:\s\-]*({DATE_REGEX})"
        m = re.search(pattern, clause_text, flags=re.IGNORECASE | re.VERBOSE)
        if m:
            raw_val = m.group(1).strip()
            parsed_d = parse_raw_date(raw_val)
            if parsed_d:
                results.append({
                    "kind": "start_date",
                    "raw_text": m.group(0).strip(),
                    "value_date": parsed_d,
                    "confidence": "high",
                    "clause_id": clause_id,
                })
                break

    # 2. Search for end date
    for kw in END_KEYWORDS:
        pattern = rf"(?:{kw})\s*[:\s\-]*({DATE_REGEX})"
        m = re.search(pattern, clause_text, flags=re.IGNORECASE | re.VERBOSE)
        if m:
            raw_val = m.group(1).strip()
            parsed_d = parse_raw_date(raw_val)
            if parsed_d:
                results.append({
                    "kind": "end_date",
                    "raw_text": m.group(0).strip(),
                    "value_date": parsed_d,
                    "confidence": "high",
                    "clause_id": clause_id,
                })
                break

    # 3. Search for signing date
    for kw in SIGNING_KEYWORDS:
        pattern = rf"(?:{kw})\s*[:\s\-]*({DATE_REGEX})"
        m = re.search(pattern, clause_text, flags=re.IGNORECASE | re.VERBOSE)
        if m:
            raw_val = m.group(1).strip()
            parsed_d = parse_raw_date(raw_val)
            if parsed_d:
                results.append({
                    "kind": "signing_date",
                    "raw_text": m.group(0).strip(),
                    "value_date": parsed_d,
                    "confidence": "high",
                    "clause_id": clause_id,
                })
                break

    # 4. Search for payment due date (e.g. "due on the 1st day of each month")
    m_due = re.search(
        r"due\s+on\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+(?:day\s+of\s+each\s+month|of\s+the\s+month)",
        clause_text,
        flags=re.IGNORECASE,
    )
    if m_due:
        day_num = int(m_due.group(1))
        results.append({
            "kind": "payment_due_day",
            "raw_text": m_due.group(0),
            "value_number": day_num,
            "value_unit": "day_of_month",
            "confidence": "high",
            "clause_id": clause_id,
        })

    return results
