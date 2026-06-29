from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem,
)
from rubrics import RUBRICS


def build_pdf(inputs: dict, result: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("t", parent=styles["Title"], textColor=colors.HexColor("#7c3aed"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#4f46e5"))
    body = styles["BodyText"]

    flow = [
        Paragraph("Startup Idea Validation Report", title),
        Spacer(1, 6),
        Paragraph(f"<b>Idea:</b> {inputs['idea']}", body),
        Paragraph(f"<b>Customer:</b> {inputs.get('customer') or '(inferred)'}", body),
        Paragraph(f"<b>Industry:</b> {result.get('industry','-')}", body),
        Spacer(1, 6),
        Paragraph(f"<b>Interpreted:</b> {result.get('interpreted_idea','')}", body),
        Spacer(1, 10),
        Paragraph(f"Overall Score: {result['weighted_score']} / 100", h2),
        Paragraph(result["verdict_label"], body),
        Paragraph(f"<i>{result['overall_summary']}</i>", body),
        Spacer(1, 12),
        Paragraph("Rubric Breakdown", h2),
    ]

    rows = [["Rubric", "Score", "Finding"]]
    for k, r in RUBRICS.items():
        s = result["scores"][k]
        rows.append([r["name"], f"{s['score']}/10 ({s['grade']})", s["finding"]])
    tbl = Table(rows, colWidths=[1.6 * inch, 1.1 * inch, 3.6 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flow.append(tbl)
    flow.append(Spacer(1, 12))

    def bullets(heading, items):
        flow.append(Paragraph(heading, h2))
        flow.append(ListFlowable([ListItem(Paragraph(str(i), body)) for i in items], bulletType="bullet"))
        flow.append(Spacer(1, 8))

    bullets("Top Risks", result.get("top_risks", []))
    bullets("Opportunities", result.get("top_opportunities", []))
    bullets("Next Steps", result.get("next_steps", []))
    if result.get("coaching_questions"):
        bullets("Questions to Sharpen Your Idea", result["coaching_questions"])
    if result.get("pivot_ideas"):
        bullets("Stronger Angles in This Theme", result["pivot_ideas"])

    if result.get("idea_shaping"):
        flow.append(Paragraph("How to Shape This Idea", h2))
        flow.append(Paragraph(result["idea_shaping"], body))

    doc.build(flow)
    return buf.getvalue()
