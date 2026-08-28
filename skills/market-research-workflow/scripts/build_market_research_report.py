#!/usr/bin/env python3
"""Build a structured Market Research DOCX from a validated research record."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


NAVY = "17365D"
GREEN = "167D5A"
PALE_GREEN = "EAF4EF"
GRAY = "5B6573"


ROUTE_TITLES = {
    "complete_report": "FAR Part 10 Market Research Report",
    "refresh": "Market Research Refresh",
    "one_question": "Market Evidence Analysis",
    "pre_award_handoff": "Pre-Award Market Research Handoff",
}


def _looks_synthetic(item: dict) -> bool:
    text = " ".join(
        str(item.get(field, ""))
        for field in ("title", "locator", "fact", "limitations")
    ).lower()
    return any(marker in text for marker in ("fixture", "synthetic", "no live", "test data only"))


def completion_state(record: dict) -> tuple[bool, list[str]]:
    """Return an honest full-report label based on evidence, not one flag alone."""
    validation = record.get("validation", {})
    evidence = [item for item in record.get("evidence", []) if isinstance(item, dict)]
    live_federal = any(
        item.get("source_class") == "federal_mcp" and not _looks_synthetic(item)
        for item in evidence
    )
    web_evidence = any(
        item.get("source_class") in {"official_web", "other_web"}
        for item in evidence
    )
    commercial_approved = validation.get("commercial_evidence_complete") is True
    missing = []
    if not live_federal:
        missing.append("live federal award/entity evidence")
    if not web_evidence:
        missing.append("approved public-web evidence")
    if not commercial_approved:
        missing.append("approved commercial-market evidence")
    return not missing, missing


def item_text(item: object) -> str:
    if not isinstance(item, dict):
        return str(item)
    return str(
        item.get("text")
        or item.get("action")
        or item.get("decision")
        or item.get("question")
        or item.get("title")
        or json.dumps(item, sort_keys=True)
    )


def pretty_label(key: object) -> str:
    """Format metadata labels for a reader instead of exposing field names."""
    label = str(key).replace("_", " ").title()
    replacements = {
        "As Of Date": "As of date",
        "As Of": "As of",
        "Naics": "NAICS",
        "Psc": "PSC",
        "Id": "ID",
    }
    for source, target in replacements.items():
        label = label.replace(source, target)
    return label


def display_value(value: object) -> str:
    """Render structured scope values as concise reader-facing text."""
    if value in (None, "", [], {}):
        return "Not stated"
    if isinstance(value, list):
        return ", ".join(display_value(item) for item in value)
    if isinstance(value, dict):
        return "; ".join(f"{pretty_label(key)}: {display_value(item)}" for key, item in value.items())
    return str(value)


def format_calculated_total(label: str, total: float) -> str:
    """Use currency formatting for money-like checks without changing other totals."""
    money_terms = ("value", "obligation", "cost", "price", "funding", "fee", "amount")
    if any(term in label.lower() for term in money_terms):
        return f"{label}: ${total:,.0f}"
    return f"{label}: {total:,.2f}"


def complete_report_fallbacks() -> dict[str, list[dict[str, str]]]:
    """Give an incomplete record a useful, explicitly prospective research plan."""
    return {
        "capability_model": [
            {
                "title": "Comparable service delivery",
                "evidence_to_request": "Comparable help-desk scale, transition approach, coverage model, service-level results, accessibility, and security controls.",
                "failure_signal": "No comparable evidence or no accountable transition plan.",
            }
        ],
        "market_engagement_instrument": [
            {
                "theme": "Comparable delivery",
                "prompt": "Request comparable service examples, transition approach, coverage model, service metrics, accessibility, and security practices.",
                "decision_use": "Assess capability and execution risk",
            }
        ],
        "decision_gates": [
            {
                "gate": "Capability evidence",
                "owner": "Market research lead",
                "exit_condition": "At least two comparable examples and a documented coverage/transition model are recorded.",
                "evidence": "Approved responses and supporting records.",
            }
        ],
        "next_actions": [
            {
                "when": "Before acquisition strategy",
                "owner": "Market research lead + CO",
                "action": "Approve the evidence request, collect comparable responses, and refresh federal data for the current scope.",
                "output": "Evidence register and decision-ready market findings.",
            }
        ],
    }


def reader_summary(record: dict, complete: bool) -> str:
    """Replace fixture-language with a concise customer-facing status statement."""
    validation = record.get("validation", {})
    summary = str(validation.get("executive_summary") or "").strip()
    if summary and not any(marker in summary.lower() for marker in ("offline fixture", "test fixture", "demonstrates evidence")):
        return summary
    question = str(record.get("question", "the stated requirement")).rstrip(" ?")
    for prefix in ("What evidence informs acquisition of ", "What evidence informs the acquisition of "):
        if question.lower().startswith(prefix.lower()):
            question = question[len(prefix) :]
            break
    if record.get("workflow_mode") == "complete_report" and not complete:
        return (
            f"The available record supports a preliminary market frame for {question}, "
            "but live federal, public-web, and commercial evidence are still needed before "
            "a complete report or acquisition-strategy decision."
        )
    return validation.get("assessment") or validation.get("executive_summary") or "No approved executive summary was supplied."


def structured_rows(items: list[object], fields: list[tuple[str, str]], default: str = "Not recorded") -> list[list[str]]:
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append([str(item.get(key) or fallback) for key, fallback in fields])
        else:
            rows.append([str(item)] + [fallback for _, fallback in fields[1:]])
    return rows or [[default] + [fallback for _, fallback in fields[1:]]]


def shade(cell, fill: str) -> None:
    props = cell._tc.get_or_add_tcPr()
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), fill)
    props.append(element)


def set_cell_text(cell, value: object, bold: bool = False, color: str | None = None) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run(str(value if value not in (None, "") else "Not provided"))
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
    header.text = "1102tools  |  Market Research"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = RGBColor.from_string(GRAY)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Prepared as of the date shown  |  Page ")
    run.font.size = Pt(8)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)


def add_table(document: Document, headers: list[str], rows: list[list[object]], widths: list[float] | None = None):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for index, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[index], header, bold=True, color="FFFFFF")
        shade(table.rows[0].cells[index], NAVY)
        if widths:
            table.rows[0].cells[index].width = Inches(widths[index])
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            set_cell_text(cells[index], value)
            if row_index % 2:
                shade(cells[index], "F4F6F8")
            if widths:
                cells[index].width = Inches(widths[index])
    for row in table.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    return table


def add_bullets(document: Document, items: list[object], empty: str = "None recorded") -> None:
    if not items:
        document.add_paragraph(empty)
        return
    for item in items:
        if isinstance(item, dict):
            text = item.get("text") or item.get("decision") or item.get("question") or item.get("action") or json.dumps(item, sort_keys=True)
        else:
            text = str(item)
        paragraph = document.add_paragraph(text, style="List Bullet")
        paragraph.paragraph_format.keep_with_next = False
        paragraph.paragraph_format.keep_together = True
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.05


def cite_ids(paragraph, ids: list[str]) -> None:
    if not ids:
        return
    paragraph.add_run(" [")
    run = paragraph.add_run(", ".join(ids), style="Evidence ID")
    run.bold = True
    paragraph.add_run("]")


def build(record: dict, output: Path) -> None:
    validation = record.get("validation", {})
    if record.get("schema_version") != "1.2":
        raise ValueError("market research records must be migrated to schema 1.2 before report generation")
    for field in ("findings_approved", "decisions_approved", "unresolved_items_disposition_approved"):
        if validation.get(field) is not True:
            raise ValueError(f"{field} must be true before report generation")
    document = Document()
    configure(document)
    route = record.get("workflow_mode")
    complete, missing_classes = completion_state(record)
    fallbacks = complete_report_fallbacks() if route == "complete_report" else {}
    if route == "complete_report" and not complete:
        title = "Federal-Data Desk-Research Draft"
    else:
        title = validation.get("report_title") or ROUTE_TITLES.get(route, "Market Research Analysis")
    subtitle = record.get("question", "Market research")
    as_of = record.get("scope", {}).get("as_of_date", "Not stated")
    document.core_properties.title = title
    document.core_properties.subject = subtitle
    document.core_properties.author = "1102tools"

    paragraph = document.add_paragraph("MARKET RESEARCH | DECISION PRODUCT")
    run = paragraph.runs[0]
    run.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(GREEN)
    title_p = document.add_paragraph(title, style="Title")
    sub = document.add_paragraph(subtitle)
    sub.runs[0].font.size = Pt(13)
    document.add_paragraph(f"As of {as_of} | {title}")
    lead = document.add_table(rows=1, cols=1)
    lead.style = "Table Grid"
    lead.cell(0, 0).text = "BOTTOM LINE\n" + reader_summary(record, complete)
    shade(lead.cell(0, 0), "E8EEF5")
    evidence = {item["id"]: item for item in record.get("evidence", []) if isinstance(item, dict) and "id" in item}
    findings = record.get("findings", [])
    first_page_findings = validation.get("decision_implications") or findings[:3]
    document.add_heading("Decision implications", level=2)
    for finding in first_page_findings:
        if isinstance(finding, dict) and finding.get("evidence_ids"):
            p = document.add_paragraph(item_text(finding), style="List Bullet")
            cite_ids(p, finding.get("evidence_ids", []))
        else:
            document.add_paragraph(item_text(finding), style="List Bullet")
    document.add_heading("Next practical actions", level=2)
    add_table(
        document,
        ["Owner", "Action", "Output or gate"],
        structured_rows(
            validation.get("next_actions", []) or fallbacks.get("next_actions", []),
            [("owner", "Acquisition team"), ("action", "No approved next action was recorded."), ("output", "Before the related decision")],
        ),
        [1.45, 3.85, 1.6],
    )
    if route == "complete_report" and not complete:
        note = document.add_paragraph()
        note.style = document.styles["Intense Quote"]
        note.add_run("Completion boundary: ").bold = True
        note.add_run("Missing " + ", ".join(missing_classes) + ". This product must remain a desk-research draft.")

    document.add_page_break()

    def add_findings_block(empty: str = "No approved finding was recorded.") -> None:
        if not findings:
            document.add_paragraph(empty)
        for finding in findings:
            p = document.add_paragraph(finding.get("text", ""))
            cite_ids(p, finding.get("evidence_ids", []))

    def add_unknowns() -> None:
        rows = []
        for item in record.get("unresolved_questions", []):
            if isinstance(item, dict):
                rows.append([
                    item.get("id", "U---"),
                    item.get("owner", "Acquisition team"),
                    item.get("question", item.get("text", "")),
                    item.get("gate", "Before the related reserved decision"),
                    item.get("evidence_needed", "Resolve through the approved research plan"),
                ])
            else:
                text = str(item)
                identifier, _, question = text.partition(":")
                rows.append([
                    identifier.strip() if identifier.strip().startswith("U") else "U---",
                    "Acquisition team",
                    question.strip() or text,
                    "Before the related reserved decision",
                    "Resolve through the approved research plan",
                ])
        add_table(
            document,
            ["ID", "Owner", "Unknown", "Decision gate", "Evidence or action needed"],
            rows or [["None", "-", "No unresolved item was recorded.", "-", "-"]],
            [0.55, 1.15, 2.25, 1.35, 1.6],
        )

    scope = record.get("scope", {})
    if route == "complete_report":
        document.add_heading("Acquisition and decision frame", level=1)
        document.add_paragraph(record.get("question", "Not provided"))
        add_table(document, ["Scope field", "Working value"], [[pretty_label(key), display_value(value)] for key, value in scope.items()], [2.0, 4.9])
        document.add_heading("Context and assumptions", level=2)
        add_bullets(document, record.get("user_context", []) + record.get("assumptions", []))

        document.add_heading("What the evidence establishes", level=1)
        add_findings_block()
        document.add_paragraph(validation.get("small_business_analysis", "No approved small-business or competition analysis was recorded."))
        document.add_paragraph(validation.get("pricing_analysis", "No approved pricing or contract-structure analysis was recorded."))

        document.add_heading("Market capability and packaging", level=1)
        add_table(
            document,
            ["Capability or hypothesis", "Evidence to request", "Failure signal or tradeoff"],
            structured_rows(
                validation.get("capability_model", [])
                + validation.get("packaging_hypotheses", [])
                or fallbacks["capability_model"],
                [("title", "Not recorded"), ("evidence_to_request", "Not recorded"), ("failure_signal", "Not recorded")],
            ),
            [1.8, 3.05, 2.05],
        )

        document.add_heading("Market engagement instrument", level=1)
        add_table(
            document,
            ["Theme", "Evidence-focused prompt", "Decision use"],
            structured_rows(
                validation.get("market_engagement_instrument", []) or fallbacks["market_engagement_instrument"],
                [("theme", "Not recorded"), ("prompt", "No approved instrument was recorded."), ("decision_use", "Not recorded")],
            ),
            [1.55, 3.85, 1.5],
        )

        document.add_heading("Evidence-to-decision gates", level=1)
        add_table(
            document,
            ["Gate", "Owner", "Exit condition", "Evidence of completion"],
            structured_rows(
                validation.get("decision_gates", []) or fallbacks["decision_gates"],
                [("gate", "Not recorded"), ("owner", "Acquisition team"), ("exit_condition", "Not recorded"), ("evidence", "Not recorded")],
            ),
            [0.85, 1.25, 2.3, 2.5],
        )

        document.add_heading("Research execution plan", level=1)
        add_table(
            document,
            ["When", "Owner", "Action", "Output"],
            structured_rows(
                validation.get("next_actions", []) or fallbacks["next_actions"],
                [("when", "Next"), ("owner", "Acquisition team"), ("action", "No approved action was recorded."), ("output", "Not recorded")],
            ),
            [0.9, 1.35, 3.15, 1.5],
        )

        document.add_heading("Human-owned decisions and unknowns", level=1)
        add_bullets(document, record.get("user_decisions", []), "No acquisition decision is recorded as approved.")
        add_unknowns()

    elif route == "refresh":
        document.add_heading("Refresh assessment", level=1)
        document.add_paragraph(validation.get("change_assessment", validation.get("executive_summary", "No change assessment was recorded.")))
        document.add_heading("What remains usable", level=1)
        add_bullets(document, validation.get("remains_usable", []))
        document.add_heading("What changed", level=1)
        add_bullets(document, validation.get("changed_evidence", []))
        document.add_heading("What must be rechecked", level=1)
        add_bullets(document, validation.get("recheck_items", []))
        document.add_heading("Refresh action plan", level=1)
        add_table(document, ["Owner", "Action", "Output or gate"], structured_rows(validation.get("next_actions", []), [("owner", "Acquisition team"), ("action", "Not recorded"), ("output", "Not recorded")]), [1.45, 3.85, 1.6])
        document.add_heading("Human-owned decisions and unknowns", level=1)
        add_unknowns()

    elif route == "one_question":
        document.add_heading("Bounded answer", level=1)
        document.add_paragraph(validation.get("executive_summary", "No approved bounded answer was recorded."))
        document.add_heading("Evidence for and against", level=1)
        add_findings_block()
        add_bullets(document, record.get("conflicts", []), "No contrary evidence or conflict was recorded.")
        document.add_heading("Decision implications", level=1)
        add_bullets(document, validation.get("decision_implications", []))
        document.add_heading("Further research options", level=1)
        add_bullets(document, validation.get("next_actions", []))
        document.add_heading("Human-owned decisions and unknowns", level=1)
        add_unknowns()

    elif route == "pre_award_handoff":
        document.add_heading("Handoff summary", level=1)
        document.add_paragraph(validation.get("executive_summary", "No approved handoff summary was recorded."))
        document.add_heading("Approved market observations", level=1)
        add_findings_block()
        document.add_heading("Requirements implications", level=1)
        add_bullets(document, validation.get("requirements_implications", []))
        document.add_heading("Pricing evidence boundaries", level=1)
        document.add_paragraph(validation.get("pricing_analysis", "No approved pricing evidence was recorded."))
        document.add_heading("Pre-Award intake and next actions", level=1)
        add_table(document, ["Owner", "Action", "Output or gate"], structured_rows(validation.get("next_actions", []), [("owner", "Pre-Award lead"), ("action", "Not recorded"), ("output", "Not recorded")]), [1.45, 3.85, 1.6])
        document.add_heading("Human-owned decisions and unknowns", level=1)
        add_unknowns()

    else:
        raise ValueError(f"unsupported workflow_mode: {route}")

    document.add_heading("Method, limitations, and evidence", level=1)
    document.add_paragraph(validation.get("methodology", "Sources, scope, and limitations are recorded in the query and evidence registers."))
    add_bullets(document, record.get("conflicts", []), "No unresolved source conflict was recorded.")

    document.add_heading("Documents reviewed", level=2)
    docs = record.get("document_register", [])
    add_table(
        document,
        ["File", "Type and status", "Role", "Gaps or conflicts"],
        [[d.get("file", ""), f"{d.get('document_type', '')} / {d.get('status', 'unclear')}", d.get("role", ""), d.get("gaps_or_conflicts", "")] for d in docs],
        [1.5, 1.55, 2.0, 1.85],
    ) if docs else document.add_paragraph("No acquisition documents were available for this research record.")

    document.add_heading("Reproducible search log", level=2)
    queries = record.get("queries", [])
    add_table(
        document,
        ["Source / operation", "Sanitized parameters", "Retrieved", "Coverage and limits"],
        [[q.get("operation", q.get("source", "")), json.dumps(q.get("parameters", {}), sort_keys=True), q.get("retrieved_at", ""), f"{q.get('count', 'n/a')}; {q.get('limitations', '')}"] for q in queries],
        [1.5, 2.35, 1.25, 1.8],
    ) if queries else document.add_paragraph("No external query was made.")

    document.add_heading("Evidence register", level=2)
    evidence_table = add_table(
        document,
        ["ID / class", "Source", "Decision-useful fact", "Limit"],
        [[f"{e.get('id', '')}\n{e.get('source_class', '')}", f"{e.get('title', '')}\n{e.get('locator', '')}", e.get("fact", ""), e.get("limitations", "")] for e in record.get("evidence", [])],
        [0.75, 1.85, 2.75, 1.55],
    )
    for row in evidence_table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.0
                for run in paragraph.runs:
                    run.font.size = Pt(7.5)

    for index, check in enumerate(record.get("validation", {}).get("numeric_checks", [])):
        components = [float(value) for value in check.get("components", [])]
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
        paragraph = document.add_paragraph(format_calculated_total(check.get("label", "Calculated total"), sum(components)))
        cite_ids(paragraph, calculation_ids)

    for item in record.get("inferences", []):
        p = document.add_paragraph("Inference: " + item.get("text", item.get("reasoning", "")), style="List Bullet")
        cite_ids(p, item.get("evidence_ids", []))

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
    record = json.loads(args.record.read_text(encoding="utf-8"))
    build(record, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
