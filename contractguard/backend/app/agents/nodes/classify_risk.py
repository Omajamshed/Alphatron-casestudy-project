import uuid
from typing import Dict, Any, List
from app.db.session import SessionLocal
from app.db.repositories.finding_repo import FindingRepository
from app.db.repositories.contract_repo import ContractRepository
from app.db.repositories.clause_repo import ClauseRepository
from app.services.rules.risk_scoring import (
    apply_forced_rules,
    calculate_overall_contract_risk,
    SEVERITY_SCORES,
)
from app.services.llm.llm_client import llm_client


def classify_risk(state: Dict[str, Any]) -> Dict[str, Any]:
    version_id = state["version_id"]
    party_role = state.get("party_role", "tenant")
    contract_type = state.get("contract_type", "rental")
    clauses = state.get("clauses", [])

    db = SessionLocal()
    try:
        finding_repo = FindingRepository(db)
        contract_repo = ContractRepository(db)
        clause_repo = ClauseRepository(db)

        findings_data = []

        for c in clauses:
            clause_text = c.get("text", "")
            clause_id = c.get("id")

            # First, check deterministic forced rules
            forced_sev, forced_cat, forced_reason = apply_forced_rules(
                clause_text=clause_text,
                category=c.get("clause_type") or "general",
                proposed_severity="low",
            )

            if forced_reason:
                # Deterministic forced rule triggered
                final_sev = forced_sev
                final_cat = forced_cat
                reason = forced_reason
                summary = f"Identified {final_sev.upper()} risk: {reason}"
            else:
                # Keyword heuristic classification
                text_lower = clause_text.lower()
                final_sev = "low"
                final_cat = "general"
                reason = "Standard contractual clause."
                summary = (c.get("heading") or "Clause") + " text."

                if any(w in text_lower for w in ["indemnif", "liability", "damages", "hold harmless"]):
                    final_cat = "liability"
                    if "gross negligence" not in text_lower and "cap" not in text_lower:
                        final_sev = "high"
                        reason = "Indemnification or liability without reciprocal caps or exclusion carve-outs."
                    else:
                        final_sev = "medium"
                        reason = "Liability allocation clause."
                elif any(w in text_lower for w in ["terminate", "termination", "cancel", "surrender"]):
                    final_cat = "termination"
                    if "immediate" in text_lower or "sole discretion" in text_lower:
                        final_sev = "high"
                        reason = "Unilateral or immediate termination clause with restricted cure periods."
                    else:
                        final_sev = "medium"
                        reason = "Specifies notice conditions and procedure for termination."
                elif any(w in text_lower for w in ["rent increase", "escalat", "raise rent"]):
                    final_cat = "rent_increase"
                    final_sev = "high"
                    reason = "Allows rent adjustments; verify notice period and statutory percentage caps."
                elif any(w in text_lower for w in ["deposit", "security"]):
                    final_cat = "deposit"
                    final_sev = "medium"
                    reason = "Security deposit terms and deductions."
                elif any(w in text_lower for w in ["non-compete", "compete", "solicit"]):
                    final_cat = "non_compete"
                    final_sev = "high"
                    reason = "Restrictive covenant on future professional activities."
                elif any(w in text_lower for w in ["intellectual property", "work for hire", "inventions"]):
                    final_cat = "ip"
                    final_sev = "medium"
                    reason = "Allocation of intellectual property rights and work product."

            # Update clause in DB with summary & type
            clause_repo.update_clause_metadata(
                clause_id=clause_id,
                clause_type=final_cat,
                summary=summary,
            )

            # Record finding if medium, high, or critical
            if final_sev in ["medium", "high", "critical"]:
                score = float(SEVERITY_SCORES.get(final_sev, 1))
                findings_data.append({
                    "id": str(uuid.uuid4()),
                    "version_id": version_id,
                    "clause_id": clause_id,
                    "clause_no": c.get("clause_no"),
                    "heading": c.get("heading"),
                    "original_text": clause_text,
                    "severity": final_sev,
                    "category": final_cat,
                    "reason": reason,
                    "score": score,
                })

        # Calculate overall contract risk score (0-100)
        risk_summary = calculate_overall_contract_risk(findings_data, party_role=party_role)
        overall_score = risk_summary["overall_score"]

        # Persist findings and version risk score in DB
        finding_repo.add_findings_batch(findings_data)
        contract_repo.update_version_risk(version_id, overall_score)

        # Route determination: if no medium or higher findings, exit early to END
        has_actionable = any(f["severity"] in ["medium", "high", "critical"] for f in findings_data)
        route = "has_findings" if has_actionable else "no_findings"

        return {
            "findings": findings_data,
            "risk_score": overall_score,
            "route": route,
            "status": "classified",
            "message": f"Contract risk score: {overall_score}/100 with {len(findings_data)} flagged findings."
        }
    finally:
        db.close()
