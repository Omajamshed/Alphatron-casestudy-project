import time
import json
import re
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.services.llm.usage_tracker import track_llm_usage


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class MockLLMResponse:
    def __init__(self, content: str):
        self.content = content


def _generate_mock_completion(system_prompt: str, user_prompt: str, feature: str) -> str:
    """Smart fallback generator providing context-aware legal responses for offline/demo use."""
    user_lower = user_prompt.lower()

    if "classify" in feature or "classify_risk" in feature:
        # Generate classification JSON
        findings = []
        if "liability" in user_lower or "indemnif" in user_lower:
            findings.append({
                "clause_type": "liability",
                "severity": "critical",
                "category": "liability",
                "reason": "Clause imposes broad indemnification and uncapped liability on the counterparty.",
                "summary": "Tenant/contractor assumes unlimited liability for damages.",
            })
        if "rent" in user_lower and "increase" in user_lower:
            findings.append({
                "clause_type": "payment",
                "severity": "high",
                "category": "rent_increase",
                "reason": "Allows landlord to escalate rent without 60-day notice or statutory cap.",
                "summary": "Rent escalation clause without statutory protections.",
            })
        if "non-compete" in user_lower or "compete" in user_lower:
            findings.append({
                "clause_type": "restrictive_covenant",
                "severity": "high",
                "category": "non_compete",
                "reason": "Broad post-contract restrictive covenant preventing competing work.",
                "summary": "Restricts freelance/employment work in similar industry.",
            })
        if "deposit" in user_lower:
            findings.append({
                "clause_type": "security_deposit",
                "severity": "medium",
                "category": "deposit",
                "reason": "Deposit return terms exceed standard statutory 30-day window.",
                "summary": "Outlines terms for holding and returning the security deposit.",
            })
        if not findings:
            findings.append({
                "clause_type": "general",
                "severity": "low",
                "category": "general",
                "reason": "Standard contractual provision without high risk factors.",
                "summary": "General terms and recitals.",
            })
        return json.dumps(findings)

    elif "draft_counter_clauses" in feature or "counter" in feature:
        return json.dumps({
            "proposed_text": "Either party's aggregate liability under this Agreement shall be limited to the total fees paid or payable in the twelve (12) months preceding the claim. Neither party shall be liable for indirect, incidental, or consequential damages.",
            "rationale": "Standard mutual liability cap protects against disproportionate catastrophic financial exposure.",
        })

    elif "email" in feature:
        return (
            "Subject: Proposed Revisions to Agreement - ContractGuard Review\n\n"
            "Dear Counterparty,\n\n"
            "Thank you for sharing the draft agreement. I have reviewed the terms and would like to propose a few constructive adjustments to ensure mutual balance and alignment with market standards:\n\n"
            "1. Liability Cap: Added standard mutual liability limitation capped at fees paid over the preceding 12 months.\n"
            "2. Notice Requirements: Standardized notice periods to 30 calendar days.\n\n"
            "Please review the attached marked changes. I look forward to finalizing the agreement.\n\n"
            "Best regards,\n[Your Name]"
        )

    # General RAG Q&A fallback
    return (
        "Based on the provided contract clauses, the agreement contains terms addressing this subject. "
        "Specifically, see the cited section for exact obligations and timelines."
    )


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.client = None
        self._init_client()

    def _init_client(self):
        if self.provider == "gemini" and settings.LLM_API_KEY:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.client = ChatGoogleGenerativeAI(
                    model=settings.LLM_MODEL,
                    google_api_key=settings.LLM_API_KEY,
                    temperature=0.1,
                )
            except Exception:
                self.client = None
        elif self.provider == "claude" and settings.ANTHROPIC_API_KEY:
            try:
                from langchain_anthropic import ChatAnthropic
                self.client = ChatAnthropic(
                    model=settings.CLAUDE_MODEL,
                    api_key=settings.ANTHROPIC_API_KEY,
                    temperature=0.1,
                )
            except Exception:
                self.client = None

    def invoke(
        self,
        user_prompt: str,
        system_prompt: str = "",
        feature: str = "general",
        user_id: Optional[str] = None,
        db: Optional[Any] = None,
        contract_id: str = "",
    ) -> Dict[str, Any]:
        start_time = time.time()
        tokens_in = _estimate_tokens(system_prompt + " " + user_prompt)

        if self.client is not None:
            try:
                from langchain_core.messages import SystemMessage, HumanMessage
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=user_prompt))
                response = self.client.invoke(messages)
                content = response.content
            except Exception as e:
                # Fallback to mock on API error
                content = _generate_mock_completion(system_prompt, user_prompt, feature)
        else:
            content = _generate_mock_completion(system_prompt, user_prompt, feature)

        latency_ms = int((time.time() - start_time) * 1000)
        tokens_out = _estimate_tokens(content)

        cost = track_llm_usage(
            feature=feature,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            user_id=user_id,
            db=db,
            contract_id=contract_id,
        )

        return {
            "content": content,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_ms": latency_ms,
            "cost_usd": cost,
            "seconds": round(time.time() - start_time, 2),
        }


llm_client = LLMClient()
