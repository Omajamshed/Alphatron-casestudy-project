from pathlib import Path
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf_report(
    output_path: Path,
    contract_title: str,
    contract_type: str,
    risk_score: float,
    approved_suggestions: List[Dict[str, Any]],
    deadlines: Optional[List[Dict[str, Any]]] = None,
) -> Path:
    """Generates an executive PDF report summarizing contract analysis and approved counter-clauses."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#4338ca"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerCustom",
        parent=styles["Italic"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6b7280"),
        spaceBefore=16,
    )

    story = []

    # Header
    story.append(Paragraph("ContractGuard Negotiation & Review Report", title_style))
    story.append(Paragraph(f"<b>Agreement:</b> {contract_title} &nbsp;|&nbsp; <b>Type:</b> {contract_type.capitalize()} &nbsp;|&nbsp; <b>Risk Score:</b> {risk_score}/100", body_style))
    story.append(Spacer(1, 14))

    # Approved Changes Section
    story.append(Paragraph("Approved Counter-Clauses & Negotiation Terms", h2_style))
    if not approved_suggestions:
        story.append(Paragraph("No counter-clauses were approved for this contract version.", body_style))
    else:
        table_data = [
            [
                Paragraph("<b>Clause</b>", body_style),
                Paragraph("<b>Original Wording</b>", body_style),
                Paragraph("<b>Approved Counter-Clause</b>", body_style),
                Paragraph("<b>Rationale</b>", body_style),
            ]
        ]
        for s in approved_suggestions:
            clause_no = s.get("clause_no") or "Clause"
            orig = s.get("original_text", "")[:300] + ("..." if len(s.get("original_text", "")) > 300 else "")
            proposed = s.get("final_text") or s.get("proposed_text", "")
            rationale = s.get("rationale", "")
            table_data.append([
                Paragraph(clause_no, body_style),
                Paragraph(orig, body_style),
                Paragraph(proposed, body_style),
                Paragraph(rationale, body_style),
            ])

        t = Table(table_data, colWidths=[65, 160, 185, 130])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ede9fe")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#4338ca")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#9ca3af")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)

    # Key Deadlines Section
    if deadlines:
        story.append(Spacer(1, 14))
        story.append(Paragraph("Key Deadlines and Calendar Commitments", h2_style))
        dl_data = [[Paragraph("<b>Event / Term</b>", body_style), Paragraph("<b>Date / Value</b>", body_style), Paragraph("<b>Calculation Method</b>", body_style)]]
        for d in deadlines:
            dl_data.append([
                Paragraph(d.get("kind", "").replace("_", " ").title(), body_style),
                Paragraph(str(d.get("date_or_val", "")), body_style),
                Paragraph(d.get("formula", ""), body_style),
            ])
        dl_table = Table(dl_data, colWidths=[150, 150, 240])
        dl_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(dl_table)

    # Disclaimer
    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "<b>Legal Notice:</b> ContractGuard is an informational tool, not legal advice. "
        "The analysis, scores, and counter-proposals provided in this report are generated using AI-assisted heuristic "
        "comparison against public market benchmarks. Consult licensed legal counsel for binding legal advice.",
        disclaimer_style,
    ))

    doc.build(story)
    return output_path
