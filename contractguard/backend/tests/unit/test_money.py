from decimal import Decimal
from app.services.rules.money import extract_money_from_clause, clean_amount_to_decimal


def test_clean_amount_to_decimal():
    assert clean_amount_to_decimal("2,500.00") == Decimal("2500.00")
    assert clean_amount_to_decimal("$1,200") == Decimal("1200")
    assert clean_amount_to_decimal("350.50") == Decimal("350.50")


def test_extract_rent_and_deposit():
    clause_text = (
        "Tenant agrees to pay monthly rent of $2,500.00 on the first of each month. "
        "A security deposit of $5,000.00 is required upon signing."
    )
    terms = extract_money_from_clause(clause_text)
    kinds = {t["kind"]: t["value_number"] for t in terms}

    assert "rent_amount" in kinds
    assert kinds["rent_amount"] == 2500.0
    assert "security_deposit" in kinds
    assert kinds["security_deposit"] == 5000.0


def test_extract_late_fee_percentage():
    clause_text = "If rent is received after the 5th, a late fee of 5% shall be assessed."
    terms = extract_money_from_clause(clause_text)
    late_items = [t for t in terms if t["kind"] == "late_fee_rate"]

    assert len(late_items) == 1
    assert late_items[0]["value_number"] == 5.0
    assert late_items[0]["value_unit"] == "percent"


def test_uncapped_liability_detection():
    clause_text = "Contractor agrees to indemnify Client with unlimited liability for any claims."
    terms = extract_money_from_clause(clause_text)
    cap_items = [t for t in terms if t["kind"] == "liability_cap"]

    assert len(cap_items) == 1
    assert cap_items[0]["value_unit"] == "unlimited"
    assert cap_items[0]["value_number"] == -1.0
