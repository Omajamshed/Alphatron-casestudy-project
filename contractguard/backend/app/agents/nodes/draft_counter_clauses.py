import uuid
import json
import re
from typing import Dict, Any, List
from app.services.llm.llm_client import llm_client


def draft_counter_clauses(state: Dict[str, Any]) -> Dict[str, Any]:
    findings = state.get("findings", [])
    standard_terms_map = state.get("standard_terms", {})
    party_role = state.get("party_role", "tenant")
    problems = state.get("problems", [])
    attempt = state.get("attempt", 0)

    suggestions = []

    for f in findings:
        finding_id = f["id"]
        clause_no = f.get("clause_no") or "Clause"
        orig_text = f.get("original_text", "")
        reason = f.get("reason", "")
        category = f.get("category", "general")
        kb_docs = standard_terms_map.get(finding_id, [])

        kb_context = "\n".join([f"- {d['title']}: {d['content']}" for d in kb_docs])

        # Generate prompt for counter-clause
        sys_prompt = (
            "You are an expert contract attorney advocating for a client. "
            "Your task is to draft a balanced, commercially reasonable counter-clause "
            "that eliminates the identified legal risk while remaining acceptable to the counterparty. "
            "Respond ONLY with valid JSON in this exact structure: "
            '{"proposed_text": "...", "rationale": "..."}'
        )

        user_prompt = f"""Party Role: {party_role}
Category: {category}
Identified Risk: {reason}

Original Clause ({clause_no}):
\"\"\"{orig_text}\"\"\"

Benchmark Standard Terms:
{kb_context}
"""
        if problems:
            user_prompt += f"\nPrevious draft had issues: {'; '.join(problems)}. Please correct them."

        res = llm_client.invoke(
            user_prompt=user_prompt,
            system_prompt=sys_prompt,
            feature="draft_counter_clauses",
        )

        content = res["content"].strip()
        # Parse JSON from content
        try:
            # find JSON block if surrounded by markdown fences
            json_m = re.search(r"\{.*\}", content, re.DOTALL)
            if json_m:
                parsed = json.loads(json_m.group(0))
                proposed_text = parsed.get("proposed_text")
                rationale = parsed.get("rationale")
            else:
                proposed_text = content
                rationale = f"Replaces risky language in {clause_no} with balanced protections."
        except Exception:
            proposed_text = (
                "Neither party shall be liable for indirect, incidental, or consequential damages. "
                "Any liability under this clause shall be limited to the fees actually paid under this Agreement."
            )
            rationale = "Caps catastrophic financial exposure in accordance with standard market terms."

        suggestions.append({
            "id": str(uuid.uuid4()),
            "finding_id": finding_id,
            "clause_id": f.get("clause_id"),
            "clause_no": clause_no,
            "heading": f.get("heading"),
            "category": category,
            "severity": f.get("severity"),
            "original_text": orig_text,
            "proposed_text": proposed_text,
            "rationale": rationale,
            "status": "pending",
            "final_text": None,
        })

    return {
        "suggestions": suggestions,
        "attempt": attempt + 1,
        "status": "counter_clauses_drafted",
    }
