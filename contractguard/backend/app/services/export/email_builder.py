from typing import List, Dict, Any


def build_negotiation_email(
    contract_title: str,
    party_role: str,
    approved_suggestions: List[Dict[str, Any]],
    user_name: str = "Client",
) -> str:
    """
    Constructs a professional, collaborative negotiation email
    incorporating ONLY approved or edited suggestions.
    Rejected suggestions are strictly omitted.
    """
    if not approved_suggestions:
        raise ValueError("Cannot generate negotiation email without approved or edited suggestions.")

    items_text = []
    for idx, s in enumerate(approved_suggestions, 1):
        clause_ref = f"Clause {s.get('clause_no', 'Section')}"
        orig = s.get("original_text", "").strip()
        proposed = (s.get("final_text") or s.get("proposed_text", "")).strip()
        rationale = s.get("rationale", "").strip()

        item_str = (
            f"{idx}. {clause_ref} Revisions:\n"
            f"   - Proposed Language: \"{proposed}\"\n"
            f"   - Rationale: {rationale}"
        )
        items_text.append(item_str)

    body_points = "\n\n".join(items_text)

    email = f"""Subject: Proposed Revisions to {contract_title} - Mutual Alignment

Dear Team,

Thank you for providing the draft of {contract_title}. I have reviewed the agreement carefully and look forward to working together.

To ensure our agreement reflects standard market practices and mutual protections for both parties, I would like to propose the following specific adjustments for your consideration:

{body_points}

These requested modifications maintain the commercial intent of our partnership while establishing balanced risk protections. Please let me know if these terms are acceptable or if you would like to discuss them further.

Thank you for your collaboration.

Sincerely,
{user_name}

---
Notice: Generated via ContractGuard for negotiation and informational review. Not legal advice.
"""
    return email
