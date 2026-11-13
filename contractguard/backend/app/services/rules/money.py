import re
from decimal import Decimal
from typing import List, Dict, Any, Optional

CURRENCY_SYMBOLS = r"(?:\$|£|€|₹|Rs\.?|USD|EUR|GBP|INR)"

AMOUNT_PATTERN = rf"""(?:
    {CURRENCY_SYMBOLS}\s*([0-9]{{1,3}}(?:,[0-9]{{3}})*(?:\.[0-9]{{1,2}})?|[0-9]+(?:\.[0-9]{{1,2}})?)
    |
    ([0-9]{{1,3}}(?:,[0-9]{{3}})*(?:\.[0-9]{{1,2}})?|[0-9]+(?:\.[0-9]{{1,2}})?)\s*(?:USD|dollars|EUR|euros|GBP|pounds)
)"""

PERCENTAGE_PATTERN = r"([0-9]+(?:\.[0-9]+)?)\s*%"


def clean_amount_to_decimal(val_str: str) -> Optional[Decimal]:
    if not val_str:
        return None
    # Strip currency symbols and commas
    cleaned = re.sub(r"[^\d.]", "", val_str.strip())
    try:
        return Decimal(cleaned)
    except Exception:
        return None


def extract_money_from_clause(clause_text: str, clause_id: Optional[str] = None) -> List[Dict[str, Any]]:
    results = []

    # 1. Rent amount
    rent_pattern = rf"(?:monthly\s+rent|rent\s+of|base\s+rent)\s*(?:is|shall\s+be|of)?\s*[:\s]*{AMOUNT_PATTERN}"
    rent_m = re.search(rent_pattern, clause_text, flags=re.IGNORECASE | re.VERBOSE)
    if rent_m:
        raw = rent_m.group(0)
        num_m = re.search(r"([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", raw)
        if num_m:
            dec = clean_amount_to_decimal(num_m.group(1))
            if dec:
                results.append({
                    "kind": "rent_amount",
                    "raw_text": raw.strip(),
                    "value_number": float(dec),
                    "value_unit": "monthly",
                    "confidence": "high",
                    "clause_id": clause_id,
                })

    # 2. Security deposit
    deposit_pattern = rf"(?:security\s+deposit|deposit)\s*(?:of|is|shall\s+be)?\s*[:\s]*{AMOUNT_PATTERN}"
    deposit_m = re.search(deposit_pattern, clause_text, flags=re.IGNORECASE | re.VERBOSE)
    if deposit_m:
        raw = deposit_m.group(0)
        num_m = re.search(r"([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", raw)
        if num_m:
            dec = clean_amount_to_decimal(num_m.group(1))
            if dec:
                results.append({
                    "kind": "security_deposit",
                    "raw_text": raw.strip(),
                    "value_number": float(dec),
                    "value_unit": "fixed",
                    "confidence": "high",
                    "clause_id": clause_id,
                })

    # 3. Late fee
    late_pct_m = re.search(
        rf"late\s+(?:fee|charge|penalty)\s*(?:of|is)?\s*{PERCENTAGE_PATTERN}",
        clause_text,
        flags=re.IGNORECASE,
    )
    if late_pct_m:
        pct = float(late_pct_m.group(1))
        results.append({
            "kind": "late_fee_rate",
            "raw_text": late_pct_m.group(0),
            "value_number": pct,
            "value_unit": "percent",
            "confidence": "high",
            "clause_id": clause_id,
        })
    else:
        late_amt_m = re.search(
            rf"late\s+(?:fee|charge|penalty)\s*(?:of|is)?\s*{AMOUNT_PATTERN}",
            clause_text,
            flags=re.IGNORECASE | re.VERBOSE,
        )
        if late_amt_m:
            raw = late_amt_m.group(0)
            num_m = re.search(r"([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", raw)
            if num_m:
                dec = clean_amount_to_decimal(num_m.group(1))
                if dec:
                    results.append({
                        "kind": "late_fee_flat",
                        "raw_text": raw.strip(),
                        "value_number": float(dec),
                        "value_unit": "flat",
                        "confidence": "high",
                        "clause_id": clause_id,
                    })

    # 4. Liability cap or Uncapped liability
    uncapped_m = re.search(
        r"\b(?:unlimited\s+liability|no\s+limitation\s+of\s+liability|without\s+limitation|liability\s+shall\s+not\s+be\s+limited)\b",
        clause_text,
        flags=re.IGNORECASE,
    )
    if uncapped_m:
        results.append({
            "kind": "liability_cap",
            "raw_text": uncapped_m.group(0),
            "value_number": -1.0,
            "value_unit": "unlimited",
            "confidence": "high",
            "clause_id": clause_id,
        })
    else:
        cap_m = re.search(
            rf"(?:liability\s+capped\s+at|limitation\s+of\s+liability\s+to|shall\s+not\s+exceed)\s*{AMOUNT_PATTERN}",
            clause_text,
            flags=re.IGNORECASE | re.VERBOSE,
        )
        if cap_m:
            raw = cap_m.group(0)
            num_m = re.search(r"([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", raw)
            if num_m:
                dec = clean_amount_to_decimal(num_m.group(1))
                if dec:
                    results.append({
                        "kind": "liability_cap",
                        "raw_text": raw.strip(),
                        "value_number": float(dec),
                        "value_unit": "capped",
                        "confidence": "high",
                        "clause_id": clause_id,
                    })

    return results
