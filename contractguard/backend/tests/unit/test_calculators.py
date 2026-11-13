from datetime import date
from decimal import Decimal
from app.services.rules.calculators import (
    calculate_notice_deadline,
    calculate_auto_renewal_trap_date,
    calculate_late_fee_exposure,
    calculate_early_termination_penalty,
    calculate_rent_escalation_schedule,
    calculate_total_financial_exposure,
)


def test_calculate_notice_deadline():
    end_date = date(2026, 12, 31)
    res = calculate_notice_deadline(end_date=end_date, notice_days=60)

    assert res["deadline_date"] == "2026-11-01"
    assert "2026-12-31 - 60 days = 2026-11-01" in res["formula"]


def test_calculate_auto_renewal_trap_date():
    end_date = date(2026, 8, 31)
    res = calculate_auto_renewal_trap_date(end_date=end_date, cancellation_notice_days=30)

    assert res["trap_date"] == "2026-08-01"
    assert "2026-08-31" in res["formula"]


def test_calculate_late_fee_exposure_percentage():
    base_rent = Decimal("3000.00")
    rate = Decimal("5.0")
    res = calculate_late_fee_exposure(base_amount=base_rent, rate_percent=rate, periods_late=2)

    # 3000 * 0.05 * 2 = 300
    assert res["exposure_amount"] == 300.0
    assert "3000.00 * (5.0% / 100) * 2 periods = $300.00" in res["formula"]


def test_calculate_early_termination_penalty():
    monthly = Decimal("2000.00")
    res = calculate_early_termination_penalty(monthly_amount=monthly, remaining_months=4)

    assert res["penalty_amount"] == 8000.0
    assert "$2000.00 (monthly) * 4 remaining months = $8000.00" in res["formula"]


def test_calculate_rent_escalation_schedule():
    base = Decimal("1000.00")
    pct = Decimal("5.0")
    schedule = calculate_rent_escalation_schedule(base_monthly_rent=base, annual_increase_pct=pct, years=3)

    assert len(schedule) == 3
    assert schedule[0]["monthly_rent"] == 1000.0
    assert schedule[1]["monthly_rent"] == 1050.0
    assert schedule[2]["monthly_rent"] == 1102.5


def test_calculate_total_financial_exposure():
    deposit = Decimal("2500.00")
    penalty = Decimal("5000.00")
    late = Decimal("250.00")

    res = calculate_total_financial_exposure(
        deposit=deposit,
        termination_penalty=penalty,
        late_fee_exposure=late,
        has_uncapped_liability=True,
    )

    assert res["known_financial_exposure"] == 7750.0
    assert res["is_uncapped"] is True
    assert "UNCAPPED LIABILITY" in res["formula"]
