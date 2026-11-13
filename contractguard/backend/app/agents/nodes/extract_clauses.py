from decimal import Decimal
from typing import Dict, Any
from app.db.session import SessionLocal
from app.db.repositories.clause_repo import ClauseRepository
from app.db.repositories.finding_repo import FindingRepository
from app.services.rules.dates import extract_dates_from_clause
from app.services.rules.durations import extract_durations_from_clause
from app.services.rules.money import extract_money_from_clause
from app.services.rules.renewal import extract_renewal_terms_from_clause
from app.services.rules.calculators import (
    calculate_notice_deadline,
    calculate_auto_renewal_trap_date,
    calculate_late_fee_exposure,
    calculate_early_termination_penalty,
    calculate_total_financial_exposure,
    calculate_rent_escalation_schedule,
)


def extract_clauses(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Load clauses, run deterministic rule engine extractors, and save key_terms."""
    version_id = state["version_id"]
    db = SessionLocal()
    try:
        clause_repo = ClauseRepository(db)
        finding_repo = FindingRepository(db)

        clauses_db = clause_repo.get_clauses_by_version(version_id)
        clauses_data = []
        all_terms = []

        start_date = None
        end_date = None
        notice_days = 30
        rent_amount = None
        deposit_amount = None
        late_fee_rate = None
        late_fee_flat = None
        has_uncapped_liability = False
        is_auto_renew = False

        for c in clauses_db:
            c_dict = {
                "id": c.id,
                "version_id": c.version_id,
                "clause_no": c.clause_no,
                "heading": c.heading,
                "text": c.text,
                "page_start": c.page_start,
                "page_end": c.page_end,
                "clause_type": c.clause_type,
                "summary": c.summary,
            }
            clauses_data.append(c_dict)

            # 1. Dates
            dates = extract_dates_from_clause(c.text, c.id)
            for d in dates:
                if d["kind"] == "start_date" and not start_date:
                    start_date = d["value_date"]
                elif d["kind"] == "end_date" and not end_date:
                    end_date = d["value_date"]
                all_terms.append({
                    "version_id": version_id,
                    "clause_id": c.id,
                    "kind": d["kind"],
                    "raw_text": d.get("raw_text"),
                    "value_date": d.get("value_date"),
                    "computed": {"confidence": d.get("confidence")},
                })

            # 2. Durations
            durations = extract_durations_from_clause(c.text, c.id)
            for dur in durations:
                if dur["kind"] == "notice_period":
                    notice_days = int(dur.get("days_equivalent") or dur.get("value_number") or 30)
                all_terms.append({
                    "version_id": version_id,
                    "clause_id": c.id,
                    "kind": dur["kind"],
                    "raw_text": dur.get("raw_text"),
                    "value_number": dur.get("value_number"),
                    "value_unit": dur.get("value_unit"),
                    "computed": {"confidence": dur.get("confidence"), "days_equivalent": dur.get("days_equivalent")},
                })

            # 3. Money
            money_terms = extract_money_from_clause(c.text, c.id)
            for m in money_terms:
                if m["kind"] == "rent_amount" and not rent_amount:
                    rent_amount = Decimal(str(m["value_number"]))
                elif m["kind"] == "security_deposit" and not deposit_amount:
                    deposit_amount = Decimal(str(m["value_number"]))
                elif m["kind"] == "late_fee_rate" and not late_fee_rate:
                    late_fee_rate = Decimal(str(m["value_number"]))
                elif m["kind"] == "late_fee_flat" and not late_fee_flat:
                    late_fee_flat = Decimal(str(m["value_number"]))
                elif m["kind"] == "liability_cap" and m.get("value_unit") == "unlimited":
                    has_uncapped_liability = True

                all_terms.append({
                    "version_id": version_id,
                    "clause_id": c.id,
                    "kind": m["kind"],
                    "raw_text": m.get("raw_text"),
                    "value_number": m.get("value_number"),
                    "value_unit": m.get("value_unit"),
                    "computed": {"confidence": m.get("confidence")},
                })

            # 4. Renewal & Escalation
            renewals = extract_renewal_terms_from_clause(c.text, c.id)
            for r in renewals:
                if r["kind"] == "auto_renewal":
                    is_auto_renew = True
                all_terms.append({
                    "version_id": version_id,
                    "clause_id": c.id,
                    "kind": r["kind"],
                    "raw_text": r.get("raw_text"),
                    "value_number": r.get("value_number"),
                    "value_unit": r.get("value_unit"),
                    "computed": {"confidence": r.get("confidence")},
                })

        # Run Calculators if relevant inputs exist
        if end_date and notice_days:
            calc_notice = calculate_notice_deadline(end_date, notice_days)
            all_terms.append({
                "version_id": version_id,
                "clause_id": None,
                "kind": "computed_notice_deadline",
                "raw_text": calc_notice["description"],
                "computed": calc_notice,
            })

        if end_date and is_auto_renew:
            calc_trap = calculate_auto_renewal_trap_date(end_date, notice_days)
            all_terms.append({
                "version_id": version_id,
                "clause_id": None,
                "kind": "computed_auto_renewal_trap",
                "raw_text": calc_trap["warning"],
                "computed": calc_trap,
            })

        if rent_amount:
            calc_late = calculate_late_fee_exposure(
                base_amount=rent_amount,
                rate_percent=late_fee_rate,
                flat_fee=late_fee_flat,
                periods_late=1,
            )
            calc_term = calculate_early_termination_penalty(
                monthly_amount=rent_amount,
                remaining_months=3,
            )
            calc_exp = calculate_total_financial_exposure(
                deposit=deposit_amount,
                termination_penalty=Decimal(str(calc_term["penalty_amount"])),
                late_fee_exposure=Decimal(str(calc_late["exposure_amount"])),
                has_uncapped_liability=has_uncapped_liability,
            )
            all_terms.append({
                "version_id": version_id,
                "clause_id": None,
                "kind": "computed_financial_exposure",
                "raw_text": calc_exp["formula"],
                "value_number": calc_exp["known_financial_exposure"],
                "computed": calc_exp,
            })

        # Save key terms to DB
        finding_repo.add_key_terms_batch(all_terms)

        return {
            "clauses": clauses_data,
            "key_terms": all_terms,
            "attempt": 0,
            "problems": [],
        }
    finally:
        db.close()
