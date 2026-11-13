import re
from typing import Dict, Any, List


def validate(state: Dict[str, Any]) -> Dict[str, Any]:
    suggestions = state.get("suggestions", [])
    clauses = state.get("clauses", [])
    attempt = state.get("attempt", 1)

    clause_ids = {c["id"] for c in clauses if "id" in c}
    problems = []

    for s in suggestions:
        # 1. References real clause
        c_id = s.get("clause_id")
        if c_id and c_id not in clause_ids:
            problems.append(f"Suggestion {s.get('id')} references non-existent clause_id {c_id}")

        # 2. Length check
        prop = s.get("proposed_text", "")
        if not prop or len(prop.strip()) < 10:
            problems.append(f"Suggestion {s.get('id')} proposed text is too short or empty")
        elif len(prop) > 4000:
            problems.append(f"Suggestion {s.get('id')} proposed text exceeds maximum character limit")

        # 3. Check for hallucinated monetary numbers
        # If original didn't have large numbers and proposed introduces random $50,000, flag it
        orig_nums = set(re.findall(r"\b\d{4,}\b", s.get("original_text", "")))
        prop_nums = set(re.findall(r"\b\d{4,}\b", prop))
        new_large_nums = prop_nums - orig_nums
        if new_large_nums and len(new_large_nums) > 2:
            problems.append(f"Suggestion {s.get('id')} introduced arbitrary numbers: {new_large_nums}")

    # Determine retry route: if problems exist and attempt is 1, retry once
    if problems and attempt <= 1:
        route = "retry"
    else:
        route = "proceed_to_review"

    return {
        "problems": problems,
        "route": route,
        "status": "validated",
    }
