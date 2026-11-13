import os
import sys
import json
import time
from pathlib import Path

# Add backend directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models.user import User
from app.db.models.contract import Contract, ContractVersion
from app.db.models.clause import Clause
from app.core.security import get_password_hash
from app.services.rag.retriever import ContractRAGService, REFUSAL_RESPONSE
from app.services.ingestion.embedder import get_embedding
from app.services.rules.calculators import (
    calculate_notice_deadline,
    calculate_auto_renewal_trap_date,
    calculate_late_fee_exposure,
    calculate_early_termination_penalty,
)
from datetime import date
from decimal import Decimal


def setup_eval_env():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # User
    user = User(id="eval-user-1", email="eval@contractguard.local", password_hash=get_password_hash("evalpass"))
    db.add(user)

    # 1. Rental Contract
    c_rental = Contract(id="c-rental", user_id="eval-user-1", title="Sample Lease Agreement", contract_type="rental", party_role="tenant")
    v_rental = ContractVersion(id="v-rental", contract_id="c-rental", version=1, filename="lease.pdf", risk_score=45.0)
    db.add_all([c_rental, v_rental])

    sample_clauses = [
        ("1.1", "Term", "This lease shall commence on January 1, 2026 and shall expire on December 31, 2026."),
        ("2.1", "Termination Notice", "Either party may terminate this agreement with thirty (30) days prior written notice."),
        ("2.2", "Automatic Renewal", "The lease shall automatically renew for a successive one-year term unless notice is given 60 days prior."),
        ("3.0", "Rent Payment", "Monthly rent shall be $2,000.00, due on the 1st day of each calendar month."),
        ("3.1", "Security Deposit", "Tenant shall provide a security deposit of $4,000.00 upon execution of this lease."),
        ("3.2", "Deposit Return", "The landlord shall return the deposit within 30 days after tenant vacates with itemized deductions."),
        ("3.3", "Late Fees", "A late fee of 5% will be charged if rent is received after the 5th day of the month."),
        ("6.1", "Repairs & Maintenance", "Landlord is responsible for structural, roof, and exterior repairs. Tenant maintains cleanliness."),
        ("7.2", "Rent Increases", "Landlord may raise rent by up to 5% annually upon providing 60 days advance written notice."),
        ("8.0", "Pet Policy", "Small domestic pets under 25 pounds are permitted with a $250 non-refundable pet deposit."),
        ("9.0", "Landlord Entry", "Landlord must provide at least 24 hours advance notice before entering the leased premises."),
        ("9.1", "Emergency Access", "Landlord may enter immediately without advance notice in the event of an emergency threatening life or property."),
        ("10.1", "Limitation of Liability", "Contractor liability shall be capped at the total amount of fees paid under this Agreement."),
        ("12.0", "Termination for Convenience", "Client may terminate this consulting contract for convenience with 14 days written notice."),
        ("12.2", "Kill Fee", "Upon cancellation, client shall pay for all completed work plus a 20% kill fee for scheduled milestones."),
        ("8.1", "Non-Compete", "Employee agrees not to compete with company in a 25-mile radius for a period of six (6) months post-employment."),
        ("7.2", "Moonlighting IP", "Inventions created entirely on employee's own time without company equipment or trade secrets remain employee property."),
    ]

    for idx, (c_no, h, text) in enumerate(sample_clauses, 1):
        emb = get_embedding(text)
        cl = Clause(
            id=f"cl-{idx}-{c_no.replace('.', '-')}",
            version_id="v-rental",
            clause_no=c_no,
            heading=h,
            text=text,
            page_start=1,
            page_end=1,
            embedding=emb,
        )
        db.add(cl)

    db.commit()
    return db, "v-rental"


def run_evaluation():
    print("=" * 65)
    print(" CONTRACTGUARD EVALUATION HARNESS")
    print(" Measuring RAG Accuracy, Refusal Rate, & Deterministic Engines")
    print("=" * 65)

    db, version_id = setup_eval_env()
    rag = ContractRAGService(db)

    # 1. Evaluate Calculators
    calc_tests = 0
    calc_passed = 0

    # Test notice deadline
    n_res = calculate_notice_deadline(date(2026, 12, 31), 60)
    calc_tests += 1
    if n_res["deadline_date"] == "2026-11-01":
        calc_passed += 1

    # Test auto renewal trap
    t_res = calculate_auto_renewal_trap_date(date(2026, 8, 31), 30)
    calc_tests += 1
    if t_res["trap_date"] == "2026-08-01":
        calc_passed += 1

    # Test late fee
    l_res = calculate_late_fee_exposure(Decimal("2000.00"), Decimal("5.0"), periods_late=1)
    calc_tests += 1
    if l_res["exposure_amount"] == 100.0:
        calc_passed += 1

    # Test termination
    term_res = calculate_early_termination_penalty(Decimal("2000.00"), 3)
    calc_tests += 1
    if term_res["penalty_amount"] == 6000.0:
        calc_passed += 1

    calc_rate = (calc_passed / calc_tests) * 100.0
    print(f"\n[Calculators] Pass Rate: {calc_rate:.1f}% ({calc_passed}/{calc_tests}) - Target: 100%")

    # 2. Evaluate QA Cases (Retrieval & Citations)
    qa_path = Path(__file__).parent / "qa_cases.json"
    with open(qa_path, "r", encoding="utf-8") as f:
        qa_cases = json.load(f)

    qa_total = len(qa_cases)
    cited_correctly = 0
    total_latency_ms = 0

    print(f"\n[RAG QA Evaluation] Running {qa_total} Q&A cases...")
    for item in qa_cases:
        t0 = time.time()
        ans = rag.answer_question(version_id=version_id, question=item["question"], top_k=3)
        dt = (time.time() - t0) * 1000
        total_latency_ms += dt

        # Check if citations exist
        if ans["citations"] and len(ans["citations"]) > 0:
            cited_correctly += 1
        elif REFUSAL_RESPONSE.lower() in ans["answer"].lower():
            # If not in lease, correct refusal
            cited_correctly += 1

    qa_accuracy = (cited_correctly / qa_total) * 100.0
    avg_latency = total_latency_ms / qa_total if qa_total else 0
    print(f"[RAG QA Evaluation] Citation/Retrieval Accuracy: {qa_accuracy:.1f}% - Target: >= 90%")
    print(f"[RAG QA Evaluation] Average Latency: {avg_latency:.1f} ms")

    # 3. Evaluate Refusals (Out of Scope & Prompt Injections)
    refusal_path = Path(__file__).parent / "refusal_cases.json"
    with open(refusal_path, "r", encoding="utf-8") as f:
        refusal_cases = json.load(f)

    refusal_total = len(refusal_cases)
    refusal_correct = 0

    print(f"\n[Safety & Refusal Evaluation] Running {refusal_total} adversarial/out-of-scope cases...")
    for item in refusal_cases:
        ans = rag.answer_question(version_id=version_id, question=item["question"], top_k=3)
        # Verify refusal phrase is present or zero citations
        if REFUSAL_RESPONSE.lower() in ans["answer"].lower() or not ans["citations"]:
            refusal_correct += 1

    refusal_rate = (refusal_correct / refusal_total) * 100.0
    print(f"[Safety & Refusal] Refusal Rate: {refusal_rate:.1f}% - Target: 100%")

    # Summary Report
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "calculators_pass_rate": calc_rate,
        "rag_citation_accuracy": qa_accuracy,
        "refusal_rate": refusal_rate,
        "avg_latency_ms": round(avg_latency, 1),
        "status": "PASS" if (calc_rate == 100.0 and qa_accuracy >= 90.0 and refusal_rate == 100.0) else "REVIEW",
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    report_file = results_dir / "eval_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 65)
    print(f" EVALUATION RESULT: {results['status']}")
    print(f" Report saved to: {report_file}")
    print("=" * 65)
    db.close()
    return results


if __name__ == "__main__":
    run_evaluation()
