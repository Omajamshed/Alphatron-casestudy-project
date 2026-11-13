from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, List


def calculate_notice_deadline(end_date: date, notice_days: int) -> Dict[str, Any]:
    """
    Formula: end_date - notice_period (calendar days)
    """
    deadline = end_date - timedelta(days=notice_days)
    formula = f"{end_date.isoformat()} - {notice_days} days = {deadline.isoformat()}"
    return {
        "deadline_date": deadline.isoformat(),
        "days_prior": notice_days,
        "formula": formula,
        "description": f"Must give notice at least {notice_days} days before {end_date.isoformat()}",
    }


def calculate_auto_renewal_trap_date(end_date: date, cancellation_notice_days: int) -> Dict[str, Any]:
    """
    Formula: end_date - cancellation_notice_days
    Auto-renewal trap date is the absolute deadline to send termination notice to avoid lock-in.
    """
    trap_date = end_date - timedelta(days=cancellation_notice_days)
    formula = f"End Date ({end_date.isoformat()}) - Notice Required ({cancellation_notice_days} days) = {trap_date.isoformat()}"
    return {
        "trap_date": trap_date.isoformat(),
        "formula": formula,
        "warning": f"After {trap_date.isoformat()}, the agreement automatically locks in for another renewal term.",
    }


def calculate_late_fee_exposure(
    base_amount: Decimal,
    rate_percent: Optional[Decimal] = None,
    flat_fee: Optional[Decimal] = None,
    periods_late: int = 1,
) -> Dict[str, Any]:
    """
    Formula: amount * rate * periods_late (or flat_fee * periods_late)
    """
    if rate_percent is not None:
        rate_dec = rate_percent / Decimal("100")
        fee_per_period = (base_amount * rate_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_fee = (fee_per_period * Decimal(periods_late)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        formula = f"{base_amount} * ({rate_percent}% / 100) * {periods_late} periods = ${total_fee}"
    elif flat_fee is not None:
        total_fee = (flat_fee * Decimal(periods_late)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        formula = f"${flat_fee} * {periods_late} period(s) = ${total_fee}"
    else:
        total_fee = Decimal("0.00")
        formula = "No late fee specified"

    return {
        "exposure_amount": float(total_fee),
        "periods_late": periods_late,
        "formula": formula,
    }


def calculate_early_termination_penalty(
    monthly_amount: Decimal,
    remaining_months: int,
    fixed_penalty: Optional[Decimal] = None,
) -> Dict[str, Any]:
    """
    Formula: remaining_months * monthly_amount, or fixed penalty as written
    """
    if fixed_penalty is not None and fixed_penalty > Decimal("0"):
        penalty = fixed_penalty.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        formula = f"Fixed termination penalty: ${penalty}"
    else:
        penalty = (monthly_amount * Decimal(remaining_months)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        formula = f"${monthly_amount} (monthly) * {remaining_months} remaining months = ${penalty}"

    return {
        "penalty_amount": float(penalty),
        "remaining_months": remaining_months,
        "formula": formula,
    }


def calculate_rent_escalation_schedule(
    base_monthly_rent: Decimal,
    annual_increase_pct: Decimal,
    years: int = 3,
) -> List[Dict[str, Any]]:
    """
    Formula: Year N Rent = Year (N-1) Rent * (1 + increase_pct / 100)
    """
    schedule = []
    current_rent = base_monthly_rent

    for year in range(1, years + 1):
        if year == 1:
            schedule.append({
                "year": 1,
                "monthly_rent": float(current_rent.quantize(Decimal("0.01"))),
                "annual_total": float((current_rent * Decimal("12")).quantize(Decimal("0.01"))),
                "formula": "Base year agreed rent",
            })
        else:
            prev_rent = current_rent
            increase_factor = Decimal("1") + (annual_increase_pct / Decimal("100"))
            current_rent = (current_rent * increase_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            schedule.append({
                "year": year,
                "monthly_rent": float(current_rent),
                "annual_total": float((current_rent * Decimal("12")).quantize(Decimal("0.01"))),
                "formula": f"${prev_rent} * (1 + {annual_increase_pct}%) = ${current_rent}",
            })
    return schedule


def calculate_total_financial_exposure(
    deposit: Optional[Decimal] = None,
    termination_penalty: Optional[Decimal] = None,
    late_fee_exposure: Optional[Decimal] = None,
    has_uncapped_liability: bool = False,
) -> Dict[str, Any]:
    """
    Sum of deposit at risk, penalties and uncapped liability flagged
    """
    dep = deposit or Decimal("0")
    term = termination_penalty or Decimal("0")
    late = late_fee_exposure or Decimal("0")

    known_total = (dep + term + late).quantize(Decimal("0.01"))
    items = []
    if dep > 0:
        items.append(f"Deposit (${dep})")
    if term > 0:
        items.append(f"Early Termination (${term})")
    if late > 0:
        items.append(f"Late Fee (${late})")

    formula = " + ".join(items) if items else "$0.00"
    if has_uncapped_liability:
        formula += " + [UNCAPPED LIABILITY (Infinite risk)]"

    return {
        "known_financial_exposure": float(known_total),
        "has_uncapped_liability": has_uncapped_liability,
        "formula": formula,
        "is_uncapped": has_uncapped_liability,
    }
