from datetime import date
from app.services.rules.dates import parse_raw_date, extract_dates_from_clause


def test_parse_raw_date_formats():
    assert parse_raw_date("2026-05-15") == date(2026, 5, 15)
    assert parse_raw_date("January 1, 2026") == date(2026, 1, 1)
    assert parse_raw_date("1st of February 2026") == date(2026, 2, 1)
    assert parse_raw_date("December 31, 2026") == date(2026, 12, 31)


def test_extract_start_and_end_dates():
    clause_text = (
        "1.1 Term. This Lease Agreement shall commence on January 1, 2026 "
        "and shall expire on December 31, 2026, unless earlier terminated."
    )
    extracted = extract_dates_from_clause(clause_text)
    kinds = {d["kind"]: d["value_date"] for d in extracted}

    assert "start_date" in kinds
    assert kinds["start_date"] == date(2026, 1, 1)
    assert "end_date" in kinds
    assert kinds["end_date"] == date(2026, 12, 31)


def test_extract_payment_due_day():
    clause_text = "Rent is due on the 5th day of each month without demand or deduction."
    extracted = extract_dates_from_clause(clause_text)
    due_items = [d for d in extracted if d["kind"] == "payment_due_day"]

    assert len(due_items) == 1
    assert due_items[0]["value_number"] == 5
