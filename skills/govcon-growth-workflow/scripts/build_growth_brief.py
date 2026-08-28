#!/usr/bin/env python3
"""Build a structured GovCon Growth Brief from a validated research record."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


NAVY = "17365D"
GREEN = "167D5A"
GRAY = "5B6573"

WORKFLOW_PRODUCTS = {
    "opportunity": {
        "title": "Federal Opportunity Shortlist",
        "posture": "Pipeline decision",
        "decision_label": "PORTFOLIO POSTURE",
        "analysis": "Priority opportunities",
        "assessment": "Pipeline prioritization",
        "immediate": "48-hour shortlist moves",
        "actions": "Capture action plan",
        "unknowns": "Qualification gaps",
    },
    "bid_screen": {
        "title": "Opportunity Evidence Screen",
        "posture": "Pursuit posture",
        "decision_label": "MANAGEMENT POSTURE",
        "analysis": "Executive scorecard",
        "assessment": "Pursuit logic",
        "immediate": "48-hour decision gates",
        "actions": "Conditions before commitment",
        "unknowns": "Material unknowns",
    },
    "competitor": {
        "title": "Competitor Landscape",
        "posture": "Competitive posture",
        "decision_label": "POSITIONING POSTURE",
        "analysis": "Positioning snapshot",
        "assessment": "Competitive implications",
        "immediate": "Immediate positioning moves",
        "actions": "Engagement plan",
        "unknowns": "Claims and assumptions to validate",
    },
    "recompete": {
        "title": "Recompete and Follow-on Pipeline",
        "posture": "Pipeline timing posture",
        "decision_label": "PIPELINE POSTURE",
        "analysis": "Recompete radar",
        "assessment": "Timing and validation thesis",
        "immediate": "Near-term validation moves",
        "actions": "Validation calendar",
        "unknowns": "Dates and triggers to validate",
    },
    "teaming": {
        "title": "Teaming Partner Decision Card",
        "posture": "Partner posture",
        "decision_label": "PARTNER POSTURE",
        "analysis": "Partner-fit scorecard",
        "assessment": "Partner-fit decision",
        "immediate": "Next partner moves",
        "actions": "Diligence and engagement plan",
        "unknowns": "Diligence gaps",
    },
    "market": {
        "title": "Agency or Market Account Plan",
        "posture": "Account posture",
        "decision_label": "ACCOUNT POSTURE",
        "analysis": "Market thesis",
        "assessment": "Account implications",
        "immediate": "Next account moves",
        "actions": "90-day account plan",
        "unknowns": "Account unknowns",
    },
    "pricing": {
        "title": "Labor-Rate and Pricing Context",
        "posture": "Pricing posture",
        "decision_label": "PRICING POSTURE",
        "analysis": "Rate-position dashboard",
        "assessment": "Rate-position interpretation",
        "immediate": "Immediate pricing moves",
        "actions": "Proposal guardrails",
        "unknowns": "Pricing unknowns",
    },
    "refresh": {
        "title": "Prior-Research Delta Audit",
        "posture": "Updated posture",
        "decision_label": "DELTA POSTURE",
        "analysis": "What changed",
        "assessment": "Decision impact of the delta",
        "immediate": "Immediate update moves",
        "actions": "Updated action plan",
        "unknowns": "Unresolved deltas",
    },
}

DEFAULT_PRODUCT = {
    "title": "GovCon Growth Analysis",
    "posture": "Executive posture",
    "decision_label": "MANAGEMENT POSTURE",
    "analysis": "Decision-relevant analysis",
    "assessment": "Commercial implications",
    "immediate": "Immediate moves",
    "actions": "Action plan",
    "unknowns": "Operational unknowns",
}


def shade(cell, fill: str) -> None:
    props = cell._tc.get_or_add_tcPr()
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), fill)
    props.append(element)


def set_cell_text(cell, value: object, *, bold: bool = False, color: str | None = None) -> None:
    cell.text = ""
    run = cell.paragraphs[0].add_run(str(value if value not in (None, "") else "Not provided"))
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def configure(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)
    normal = document.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.08
    for name, size, color in (("Title", 28, NAVY), ("Heading 1", 17, NAVY), ("Heading 2", 12.5, GREEN)):
        style = document.styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(10)
        style.paragraph_format.space_after = Pt(5)
    if "Evidence ID" not in document.styles:
        style = document.styles.add_style("Evidence ID", WD_STYLE_TYPE.CHARACTER)
        style.font.name = "Aptos"
        style.font.size = Pt(8.5)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(GREEN)
    header = section.header.paragraphs[0]
    header.text = "1102tools  |  GovCon Growth"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = RGBColor.from_string(GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Prepared as of the date shown  |  Page ").font.size = Pt(8)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)


def add_table(
    document: Document,
    headers: list[str],
    rows: list[list[object]],
    widths: list[float],
    *,
    repeat_header: bool = True,
):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for index, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[index], header, bold=True, color="FFFFFF")
        shade(table.rows[0].cells[index], NAVY)
        table.rows[0].cells[index].width = Inches(widths[index])
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            set_cell_text(cells[index], value)
            if row_index % 2:
                shade(cells[index], "F4F6F8")
            cells[index].width = Inches(widths[index])
    for row in table.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    if repeat_header:
        table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    return table


def add_bullets(document: Document, items: list[object], empty: str) -> None:
    if not items:
        document.add_paragraph(empty)
        return
    for item in items:
        if isinstance(item, dict):
            text = item.get("text") or item.get("decision") or item.get("question") or json.dumps(item, sort_keys=True)
        else:
            text = str(item)
        paragraph = document.add_paragraph(text, style="List Bullet")
        paragraph.paragraph_format.keep_with_next = False
        paragraph.paragraph_format.keep_together = True
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.05


def item_text(item: object) -> str:
    """Return the reader-facing text from a record item."""
    if isinstance(item, dict):
        return str(
            item.get("text")
            or item.get("decision")
            or item.get("question")
            or json.dumps(item, sort_keys=True)
        )
    return str(item)


def operational_unknowns(record: dict) -> list[object]:
    """Combine decision-blocking unknowns without converting absence into fact."""
    items: list[object] = []
    items.extend(record.get("validation", {}).get("missing_bid_context", []))
    items.extend(record.get("unresolved_questions", []))
    seen: set[str] = set()
    result: list[object] = []
    for item in items:
        text = item_text(item).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(item)
    return result


def add_page_one_signals(document: Document, findings: list[dict]) -> None:
    """Add a compact decision dashboard from approved findings."""
    rows: list[list[object]] = []
    for finding in findings[:3]:
        evidence_ids = finding.get("evidence_ids", [])
        rows.append([
            finding.get("text", "No finding text was recorded."),
            ", ".join(evidence_ids) if evidence_ids else "No linked evidence ID",
        ])
    if rows:
        add_table(document, ["Decision signal", "Evidence"], rows, [5.55, 1.35])


def cite_ids(paragraph, ids: list[str]) -> None:
    if ids:
        paragraph.add_run(" [")
        paragraph.add_run(", ".join(ids), style="Evidence ID")
        paragraph.add_run("]")


def research_basis(record: dict) -> str:
    """Return a reader-facing evidence basis without overstating research performed."""
    web_mode = record.get("web_research", {}).get("mode")
    queries = record.get("queries", [])
    if web_mode == "no_public_web":
        return "Supplied evidence only | No public research performed"
    if queries:
        return "Public-source research with supplied company context"
    return "Supplied company and planning evidence | No external query recorded"


def scope_rows(scope: dict) -> list[list[object]]:
    """Format scope metadata as executive-readable labels and values."""
    rows: list[list[object]] = []
    for key, value in scope.items():
        label = key.replace("_", " ").title()
        if key.endswith("_usd"):
            label = label.removesuffix(" Usd")
            if isinstance(value, (int, float)):
                value = f"${value:,.0f}"
        rows.append([label, value])
    return rows


def build(record: dict, output: Path) -> None:
    document = Document()
    configure(document)
    as_of = record.get("scope", {}).get("as_of_date", "Not stated")
    has_bid_decision = bool(record.get("validation", {}).get("bid_context_complete"))
    workflow_mode = record.get("workflow_mode", "")
    product = WORKFLOW_PRODUCTS.get(workflow_mode, DEFAULT_PRODUCT)
    label = record.get("validation", {}).get("report_title", product["title"])
    validation = record.get("validation", {})
    findings = record.get("findings", [])
    unknowns = operational_unknowns(record)
    next_actions = validation.get("next_actions", [])

    brand = document.add_paragraph("GOVCON GROWTH | DECISION PRODUCT")
    brand.runs[0].bold = True
    brand.runs[0].font.size = Pt(9)
    brand.runs[0].font.color.rgb = RGBColor.from_string(GREEN)
    document.add_paragraph(label, style="Title")
    subtitle = document.add_paragraph(record.get("question", "GovCon growth research"))
    subtitle.runs[0].font.size = Pt(13)
    subtitle.runs[0].font.color.rgb = RGBColor.from_string(GRAY)
    document.add_paragraph(f"As of {as_of} | {research_basis(record)}")
    opening_insight = findings[0].get("text", "No approved finding was recorded.") if findings else "No approved finding was recorded."
    posture = validation.get("assessment") or validation.get("executive_summary") or opening_insight
    callout = document.add_table(rows=1, cols=1)
    callout.style = "Table Grid"
    shade(callout.cell(0, 0), "E8EEF5")
    set_cell_text(callout.cell(0, 0), f"{product['decision_label']}\n{posture}", bold=True, color=NAVY)

    document.add_heading(product["posture"], level=1)
    document.add_paragraph(validation.get("executive_summary", opening_insight))
    add_page_one_signals(document, findings)
    if not has_bid_decision:
        quote = document.add_paragraph(style="Intense Quote")
        quote.add_run("Decision boundary: ").bold = True
        quote.add_run("Internal company context is incomplete. This product is a conditional pursuit posture, not a bid or no-bid recommendation.")

    document.add_heading(product["immediate"], level=1)
    add_bullets(document, next_actions[:3], "Confirm the next validation action with the accountable growth lead.")
    document.add_heading(product["unknowns"], level=2)
    add_bullets(document, unknowns[:3], "No decision-blocking unknown was recorded.")
    decision_rule = validation.get("decision_rule")
    if decision_rule:
        quote = document.add_paragraph(style="Intense Quote")
        quote.add_run("Decision rule: ").bold = True
        quote.add_run(str(decision_rule))

    headings = [
        product["posture"],
        product["immediate"],
        product["analysis"],
        product["assessment"],
        "Business question and scope",
        "Company context and assumptions",
        product["unknowns"],
        "Risks, contrary evidence, and limitations",
        product["actions"],
        "Research record",
        "Evidence appendix",
    ]
    analysis_heading = document.add_heading(headings[2], level=1)
    analysis_heading.paragraph_format.page_break_before = True
    for finding in findings:
        p = document.add_paragraph(finding.get("text", ""), style="List Bullet")
        cite_ids(p, finding.get("evidence_ids", []))
    if not findings:
        document.add_paragraph("No approved finding was recorded.")
    for index, check in enumerate(record.get("validation", {}).get("numeric_checks", [])):
        total = sum(float(value) for value in check.get("components", []))
        locator = f"validation.numeric_checks[{index}]"
        calculation_ids = [
            item.get("id")
            for item in record.get("evidence", [])
            if isinstance(item, dict)
            and item.get("source_class") == "calculation"
            and item.get("locator") == locator
        ]
        if len(calculation_ids) != 1:
            raise ValueError(
                f"numeric check {index} requires exactly one calculation evidence item whose locator is {locator}"
            )
        paragraph = document.add_paragraph(f"{check.get('label', 'Calculated total')}: {total:,.2f}")
        cite_ids(paragraph, calculation_ids)

    document.add_heading(headings[3], level=1)
    document.add_paragraph(validation.get("assessment", "No final assessment was approved."))
    pipeline = validation.get("pipeline", [])
    if pipeline:
        add_table(document, ["Candidate", "Signal", "Timing", "Confidence", "Next validation"], [[p.get("candidate", ""), p.get("signal", ""), p.get("timing", ""), p.get("confidence", ""), p.get("next_validation", "")] for p in pipeline], [1.5, 1.8, 1.1, 0.8, 1.7])

    document.add_heading(headings[4], level=1)
    document.add_paragraph(record.get("question", "Not provided"))
    add_table(document, ["Scope field", "Value"], scope_rows(record.get("scope", {})), [2.1, 4.8])

    document.add_heading(headings[5], level=1)
    add_bullets(document, record.get("user_context", []), "No internal company context was supplied.")
    document.add_heading("Assumptions", level=2)
    add_bullets(document, record.get("assumptions", []), "No working assumption was recorded.")

    document.add_heading(headings[6], level=1)
    add_bullets(document, unknowns, "No operational unknown was recorded.")

    document.add_heading(headings[7], level=1)
    add_bullets(document, record.get("conflicts", []), "No source conflict was recorded.")
    for inference in record.get("inferences", []):
        p = document.add_paragraph("Inference: " + inference.get("text", inference.get("reasoning", "")), style="List Bullet")
        cite_ids(p, inference.get("evidence_ids", []))

    document.add_heading(headings[8], level=1)
    add_bullets(document, record.get("user_decisions", []), "No user decision was recorded.")
    add_bullets(document, next_actions, "No next action was recorded.")

    document.add_heading(headings[9], level=1)
    queries = record.get("queries", [])
    if queries:
        add_table(document, ["Source / operation", "Sanitized parameters", "Retrieved", "Coverage and limits"], [[q.get("operation", q.get("source", "")), json.dumps(q.get("parameters", {}), sort_keys=True), q.get("retrieved_at", ""), f"{q.get('count', 'n/a')}; {q.get('limitations', '')}"] for q in queries], [1.5, 2.35, 1.25, 2.0])
    else:
        document.add_paragraph("No external query was made.")

    document.add_heading(headings[10], level=1)
    # LibreOffice can position a repeated header above the printable area on a
    # later page of a long fixed-width table. Keep the header on the first page
    # only so every continued evidence row remains fully visible after PDF
    # conversion.
    add_table(
        document,
        ["ID", "Class", "Source", "Fact", "Limitations"],
        [[
            e.get("id", ""),
            e.get("source_class", ""),
            f"{e.get('title', '')}\n{e.get('locator', '')}",
            e.get("fact", ""),
            e.get("limitations", ""),
        ] for e in record.get("evidence", [])],
        [0.55, 0.85, 1.55, 2.5, 1.65],
        repeat_header=False,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    validator = Path(__file__).with_name("validate_research_record.py")
    result = subprocess.run([sys.executable, str(validator), str(args.record)], check=False)
    if result.returncode:
        return result.returncode
    build(json.loads(args.record.read_text(encoding="utf-8")), args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
