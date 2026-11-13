import uuid
from pathlib import Path
from typing import Dict, Any, List
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.repositories.finding_repo import FindingRepository
from app.db.repositories.contract_repo import ContractRepository
from app.services.export.email_builder import build_negotiation_email
from app.services.export.pdf_report import generate_pdf_report
from app.services.export.docx_report import generate_docx_report


def export_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Builds negotiation email and reports for approved/edited suggestions only."""
    version_id = state.get("version_id")
    decisions = state.get("decisions", {})
    suggestions = state.get("suggestions", [])
    party_role = state.get("party_role", "tenant")

    db = SessionLocal()
    try:
        finding_repo = FindingRepository(db)
        contract_repo = ContractRepository(db)

        version = contract_repo.get_version(version_id)
        contract = version.contract if version else None
        contract_title = contract.title if contract else "Agreement"
        contract_type = contract.contract_type if contract else "rental"
        risk_score = float(version.risk_score or 0.0) if version else 0.0

        # Update decisions in DB
        approved_suggestions = []
        for s in suggestions:
            s_id = s["id"]
            decision_data = decisions.get(s_id)
            if decision_data:
                status = decision_data.get("status", "pending")
                final_text = decision_data.get("final_text") or s.get("proposed_text")
            else:
                status = s.get("status", "pending")
                final_text = s.get("final_text") or s.get("proposed_text")

            # Persist update
            finding_repo.update_suggestion_decision(
                suggestion_id=s_id,
                status=status,
                final_text=final_text,
            )

            # Safety Rule: ONLY include approved or edited suggestions in output!
            if status in ["approved", "edited"]:
                s_copy = dict(s)
                s_copy["status"] = status
                s_copy["final_text"] = final_text
                approved_suggestions.append(s_copy)

        export_records = []
        run_record = (
            db.query(finding_repo.db.models.agent_run.AgentRun if hasattr(finding_repo.db, 'models') else None)
            if False else None
        )
        # Find active agent run by version_id
        from app.db.models.agent_run import AgentRun
        agent_run = (
            db.query(AgentRun)
            .filter(AgentRun.version_id == version_id)
            .order_by(AgentRun.created_at.desc())
            .first()
        )
        run_id = agent_run.id if agent_run else str(uuid.uuid4())

        if approved_suggestions:
            # 1. Build negotiation email
            email_text = build_negotiation_email(
                contract_title=contract_title,
                party_role=party_role,
                approved_suggestions=approved_suggestions,
            )
            email_exp = finding_repo.create_export(
                run_id=run_id,
                kind="email",
                content=email_text,
            )
            export_records.append(email_exp.id)

            # 2. Generate PDF report
            pdf_filename = f"ContractGuard_Report_{version_id[:8]}.pdf"
            pdf_path = settings.UPLOAD_DIR / pdf_filename
            generate_pdf_report(
                output_path=pdf_path,
                contract_title=contract_title,
                contract_type=contract_type,
                risk_score=risk_score,
                approved_suggestions=approved_suggestions,
            )
            pdf_exp = finding_repo.create_export(
                run_id=run_id,
                kind="pdf",
                file_path=str(pdf_path),
            )
            export_records.append(pdf_exp.id)

            # 3. Generate DOCX report
            docx_filename = f"ContractGuard_Report_{version_id[:8]}.docx"
            docx_path = settings.UPLOAD_DIR / docx_filename
            generate_docx_report(
                output_path=docx_path,
                contract_title=contract_title,
                contract_type=contract_type,
                risk_score=risk_score,
                approved_suggestions=approved_suggestions,
            )
            docx_exp = finding_repo.create_export(
                run_id=run_id,
                kind="docx",
                file_path=str(docx_path),
            )
            export_records.append(docx_exp.id)

        if agent_run:
            finding_repo.update_agent_run_status(agent_run.id, "completed")

        return {
            "export_ids": export_records,
            "status": "completed",
            "message": f"Successfully generated {len(export_records)} exports for {len(approved_suggestions)} approved counter-clauses.",
        }
    finally:
        db.close()
