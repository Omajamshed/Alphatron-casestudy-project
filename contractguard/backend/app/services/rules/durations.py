import re
from typing import List, Dict, Any, Optional

WORD_TO_NUM = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100,
}


def word_or_digit_to_int(token: str) -> Optional[int]:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    if token in WORD_TO_NUM:
        return WORD_TO_NUM[token]
    # Handle composite like "thirty-five" or "twenty four"
    parts = re.split(r"[\s\-]+", token)
    if len(parts) == 2 and parts[0] in WORD_TO_NUM and parts[1] in WORD_TO_NUM:
        return WORD_TO_NUM[parts[0]] + WORD_TO_NUM[parts[1]]
    return None


DURATION_PATTERN = re.compile(
    r"""(?xi)
    (?:
        # thirty (30) days or 30 days or thirty days
        ([a-z\-]+|\d+)\s*(?:\(\s*(\d+)\s*\))?\s*
        (calendar\s+days|business\s+days|working\s+days|days|months|weeks|years)
    )
    """
)


def extract_durations_from_clause(clause_text: str, clause_id: Optional[str] = None) -> List[Dict[str, Any]]:
    results = []

    # 1. Notice periods (e.g. "30 days prior written notice", "written notice of at least thirty (30) days")
    notice_m = re.findall(
        r"(?i)(?:notice\s+(?:period\s+)?of\s+|prior\s+(?:written\s+)?notice\s+of\s+|give\s+at\s+least\s+)([a-z\-]+|\d+)\s*(?:\(\s*(\d+)\s*\))?\s*(calendar\s+days|business\s+days|days|months|weeks)\b",
        clause_text,
    )
    for word_val, digit_val, unit in notice_m:
        val = int(digit_val) if digit_val else word_or_digit_to_int(word_val)
        if val is not None:
            clean_unit = unit.lower().strip()
            # Normalize to days if needed for calculation
            days_equiv = val * 30 if "month" in clean_unit else (val * 7 if "week" in clean_unit else val)
            results.append({
                "kind": "notice_period",
                "raw_text": f"{word_val} {f'({digit_val}) ' if digit_val else ''}{unit}".strip(),
                "value_number": float(val),
                "value_unit": clean_unit,
                "days_equivalent": days_equiv,
                "confidence": "high",
                "clause_id": clause_id,
            })

    # 2. Lock-in period
    lockin_m = re.search(
        r"(?i)(?:lock-in|lock\s+in)\s+(?:period\s+)?(?:of\s+)?([a-z\-]+|\d+)\s*(?:\(\s*(\d+)\s*\))?\s*(months|years|days)",
        clause_text,
    )
    if lockin_m:
        val = int(lockin_m.group(2)) if lockin_m.group(2) else word_or_digit_to_int(lockin_m.group(1))
        if val is not None:
            results.append({
                "kind": "lock_in_period",
                "raw_text": lockin_m.group(0),
                "value_number": float(val),
                "value_unit": lockin_m.group(3).lower(),
                "confidence": "high",
                "clause_id": clause_id,
            })

    # 3. Probation period
    probation_m = re.search(
        r"(?i)probation(?:ary)?\s+(?:period\s+)?(?:of\s+)?([a-z\-]+|\d+)\s*(?:\(\s*(\d+)\s*\))?\s*(months|weeks|days)",
        clause_text,
    )
    if probation_m:
        val = int(probation_m.group(2)) if probation_m.group(2) else word_or_digit_to_int(probation_m.group(1))
        if val is not None:
            results.append({
                "kind": "probation_period",
                "raw_text": probation_m.group(0),
                "value_number": float(val),
                "value_unit": probation_m.group(3).lower(),
                "confidence": "high",
                "clause_id": clause_id,
            })

    # 4. General duration if none found
    if not results:
        for m in DURATION_PATTERN.finditer(clause_text):
            word_val = m.group(1)
            digit_val = m.group(2)
            unit = m.group(3)
            val = int(digit_val) if digit_val else word_or_digit_to_int(word_val)
            if val is not None and val > 0:
                results.append({
                    "kind": "duration",
                    "raw_text": m.group(0).strip(),
                    "value_number": float(val),
                    "value_unit": unit.lower(),
                    "confidence": "needs_confirmation",
                    "clause_id": clause_id,
                })
                break

    return results
