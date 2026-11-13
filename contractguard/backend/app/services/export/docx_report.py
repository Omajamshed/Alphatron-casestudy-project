from pathlib import Path
from typing import List, Dict, Any, Optional
import docx
from docx.shared import Inches, Pt, RGBColor


def generate_docx_report(
    output_path: Path,
    contract_title: str,
    contract_type: str,
    risk_score: float,
    approved_suggestions: List[Dict[str, Any]],
    deadlines: Optional[List[Dict[str, Any]]] = None,
) -> Path:
    """Generates an editable Word DOCX report containing approved counter-proposals."""
    doc = docx.Document()

    # Title
    title_p = doc.add_heading("ContractGuard Review & Negotiation Report", level=0)
    title_run = title_p.runs[0]
    title_run.font.color.rgb = RGBColor(30, 27, 75)

    meta_p = doc.add_paragraph()
    meta_p.add_run(f"Contract: {contract_title} | Type: {contract_type.capitalize()} | Risk Score: {risk_score}/100").bold = True

    doc.add_heading("Approved Counter-Clauses", level=1)

    if not approved_suggestions:
        doc.add_paragraph("No counter-clauses were approved.")
    else:
        table = doc.add_table(rows=1, cols=4)
        table.style = "Light Shading Accent 1" if "Light Shading Accent 1" in [s.name for s in doc.styles] else "Table Grid"
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Clause"
        hdr_cells[1].text = "Original Text"
        hdr_cells[2].text = "Approved Counter-Clause"
        hdr_cells[3].text = "Rationale"

        for s in approved_suggestions:
            row_cells = table.add_row().cells
            row_cells[0].text = s.get("clause_no") or "Clause"
            row_cells[1].text = (s.get("original_text") or "")[:250]
            row_cells[2].text = s.get("final_text") or s.get("proposed_text") or ""
            row_cells[3].text = s.get("rationale") or ""

    if deadlines:
        doc.add_heading("Key Dates and Deadlines", level=1)
        d_table = doc.add_table(rows=1, cols=3)
        d_table.style = "Table Grid"
        d_cells = d_table.rows[0].cells
        d_cells[0].text = "Event"
        d_cells[1].text = "Date / Value"
        d_cells[2].text = "Calculation Formula"

        for d in deadlines:
            r = d_table.add_row().cells
            r[0].text = d.get("kind", "").replace("_", " ").title()
            r[1].text = str(d.get("date_or_val", ""))
            r[2].text = d.get("formula", "")

    # Disclaimer
    doc.add_paragraph()
    disc = doc.add_paragraph(
        "Disclaimer: ContractGuard is an informational tool, not legal advice. "
        "Outputs do not guarantee legal enforceability and should be reviewed by qualified legal counsel."
    )
    disc.runs[0].font.italic = True
    disc.runs[0].font.size = Pt(8.5)
    disc.runs[0].font.color.rgb = RGBColor(120, 120, 120)

    doc.save(str(output_path))
    return output_path
