import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import yaml

CONFIG_PATH = Path(__file__).resolve().parent / "risk_weights.yaml"


def load_risk_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "severity_scores": {"low": 1, "medium": 3, "high": 6, "critical": 10},
        "role_category_weights": {
            "tenant": {"rent_increase": 1.5, "deposit": 1.4, "termination": 1.3, "general": 1.0},
            "freelancer": {"liability": 2.0, "ip": 1.8, "payment": 1.5, "general": 1.0},
            "employee": {"non_compete": 2.0, "ip": 1.8, "clawback": 1.5, "general": 1.0},
            "other": {"liability": 1.5, "general": 1.0},
        },
    }


CONFIG = load_risk_config()
SEVERITY_SCORES = CONFIG.get("severity_scores", {"low": 1, "medium": 3, "high": 6, "critical": 10})


# Deterministic forced-severity rule definitions
FORCED_RULES = [
    # Uncapped / unlimited liability must always be critical
    (
        r"(?i)\b(?:unlimited\s+liability|no\s+limitation\s+of\s+liability|without\s+limitation|indemnify\s+and\s+hold\s+harmless\s+from\s+any\s+and\s+all)\b",
        "critical",
        "liability",
        "Clause imposes unlimited financial liability or unbounded indemnification without standard monetary caps.",
    ),
    # Immediate IP transfer without payment must be high or critical
    (
        r"(?i)\b(?:assigns\s+all\s+intellectual\s+property\s+regardless\s+of\s+payment|ip\s+transfers\s+immediately\s+prior\s+to\s+payment|without\s+receipt\s+of\s+payment)\b",
        "critical",
        "ip",
        "Clause transfers intellectual property ownership before receipt of full payment.",
    ),
    # Broad non-compete over 1 year
    (
        r"(?i)(?:non-compete|compete\s+with\s+company)\s+for\s+(?:a\s+period\s+of\s+)?(?:[1-9]\d*|one|two|three)\s+year",
        "critical",
        "non_compete",
        "Overly restrictive post-termination non-compete covenant exceeding one year.",
    ),
    # Unilateral rent increase without notice
    (
        r"(?i)(?:landlord\s+may\s+increase\s+rent\s+at\s+any\s+time|without\s+prior\s+notice\s+increase\s+rent)",
        "critical",
        "rent_increase",
        "Landlord retains unilateral right to increase rent without standard statutory notice.",
    ),
    # Non-refundable deposit
    (
        r"(?i)(?:deposit\s+is\s+non-refundable|nonrefundable\s+deposit|retain\s+entire\s+deposit)",
        "high",
        "deposit",
        "Security deposit declared non-refundable regardless of tenant compliance.",
    ),
]


def apply_forced_rules(clause_text: str, category: str, proposed_severity: str) -> Tuple[str, str, str]:
    """
    Applies deterministic rules overriding LLM severity if high-risk patterns are matched.
    Returns: (final_severity, category, reason)
    """
    for pattern, forced_sev, forced_cat, reason in FORCED_RULES:
        if re.search(pattern, clause_text):
            # If forced is more severe, override
            sev_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            if sev_rank.get(forced_sev, 1) >= sev_rank.get(proposed_severity.lower(), 1):
                return forced_sev, forced_cat, reason

    return proposed_severity.lower(), category, ""


def calculate_overall_contract_risk(
    findings: List[Dict[str, Any]],
    party_role: str = "tenant",
) -> Dict[str, Any]:
    """
    Calculates weighted normalized risk score (0 to 100) from findings.
    """
    if not findings:
        return {
            "overall_score": 0.0,
            "risk_level": "Low",
            "category_breakdown": [],
            "total_findings": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
        }

    role_weights = CONFIG.get("role_category_weights", {}).get(party_role.lower(), {})
    default_weight = role_weights.get("general", 1.0)

    category_buckets: Dict[str, List[Dict[str, Any]]] = {}
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    for f in findings:
        sev = (f.get("severity") or "low").lower()
        cat = (f.get("category") or "general").lower()

        if sev == "critical":
            critical_count += 1
        elif sev == "high":
            high_count += 1
        elif sev == "medium":
            medium_count += 1
        else:
            low_count += 1

        if cat not in category_buckets:
            category_buckets[cat] = []
        category_buckets[cat].append(f)

    # Weighted sum
    total_weighted_points = 0.0
    total_max_possible = 0.0
    breakdown = []

    for cat, items in category_buckets.items():
        weight = float(role_weights.get(cat, default_weight))
        cat_score = 0.0
        max_sev = "low"
        sev_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}

        for item in items:
            sev = (item.get("severity") or "low").lower()
            base_pts = float(SEVERITY_SCORES.get(sev, 1))
            cat_score += base_pts * weight

            if sev_rank.get(sev, 1) > sev_rank.get(max_sev, 1):
                max_sev = sev

        # Each finding could have had critical (10 pts)
        possible_pts = len(items) * 10.0 * weight
        total_weighted_points += cat_score
        total_max_possible += possible_pts

        breakdown.append({
            "category": cat,
            "count": len(items),
            "max_severity": max_sev,
            "weight": weight,
            "score_contribution": round(cat_score, 1),
        })

    # Normalized score between 0 and 100
    # Any critical finding guarantees score >= 65
    raw_normalized = (total_weighted_points / total_max_possible * 100.0) if total_max_possible > 0 else 0.0
    if critical_count > 0 and raw_normalized < 65.0:
        raw_normalized = 65.0 + (critical_count * 5.0)

    overall_score = min(100.0, max(0.0, round(raw_normalized, 1)))

    if overall_score >= 70:
        risk_level = "Critical"
    elif overall_score >= 50:
        risk_level = "High"
    elif overall_score >= 25:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {
        "overall_score": overall_score,
        "risk_level": risk_level,
        "category_breakdown": breakdown,
        "total_findings": len(findings),
        "critical_count": critical_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
    }
