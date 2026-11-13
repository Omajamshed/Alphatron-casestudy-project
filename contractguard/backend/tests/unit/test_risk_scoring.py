from app.services.rules.risk_scoring import (
    apply_forced_rules,
    calculate_overall_contract_risk,
)


def test_forced_severity_uncapped_liability():
    clause_text = "Contractor agrees to indemnify Company and hold harmless without limitation against all liabilities."
    sev, cat, reason = apply_forced_rules(clause_text, category="general", proposed_severity="low")

    assert sev == "critical"
    assert cat == "liability"
    assert "unlimited financial liability" in reason


def test_calculate_overall_contract_risk_weighted():
    findings = [
        {"severity": "critical", "category": "liability", "score": 10.0},
        {"severity": "high", "category": "termination", "score": 6.0},
    ]

    result_freelancer = calculate_overall_contract_risk(findings, party_role="freelancer")
    assert result_freelancer["overall_score"] >= 65.0
    assert result_freelancer["critical_count"] == 1
    assert result_freelancer["high_count"] == 1
    assert result_freelancer["risk_level"] in ["High", "Critical"]


def test_zero_findings_low_risk():
    result = calculate_overall_contract_risk([], party_role="tenant")
    assert result["overall_score"] == 0.0
    assert result["risk_level"] == "Low"
    assert result["total_findings"] == 0
