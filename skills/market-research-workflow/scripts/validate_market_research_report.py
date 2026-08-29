#!/usr/bin/env python3
"""Validate a generated Market Research DOCX and its numeric evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

from docx import Document


ROUTE_HEADINGS = {
    "complete_report": [
        "Acquisition and decision frame",
        "What the evidence establishes",
        "Market capability and packaging",
        "Market engagement instrument",
        "Evidence-to-decision gates",
        "Research execution plan",
        "Human-owned decisions and unknowns",
        "Method, limitations, and evidence",
    ],
    "refresh": [
        "Refresh assessment",
        "Prior-to-current evidence comparison",
        "Vendor and market-structure changes",
        "Strategy changes to make now",
        "What remains usable and what must be rechecked",
        "Refresh action plan",
        "Human-owned decisions and unknowns",
        "Method, limitations, and evidence",
    ],
    "one_question": [
        "Bounded answer",
        "Evidence for and against",
        "Decision implications",
        "Further research options",
        "Human-owned decisions and unknowns",
        "Method, limitations, and evidence",
    ],
    "pre_award_handoff": [
        "Handoff summary",
        "Approved market observations",
        "Market findings translated into acquisition inputs",
        "Pricing inputs and boundaries",
        "Pre-Award risk register",
        "Pre-Award intake and next actions",
        "Human-owned decisions and unknowns",
        "Method, limitations, and evidence",
    ],
}
FORBIDDEN = [
    re.compile(r"\b(?:automatically|therefore)\s+(?:recommend|requires?|proves?)\b", re.I),
    re.compile(r"\b(?:set[- ]aside|commerciality|contract type|price reasonableness)\s+is\s+automatically\b", re.I),
    re.compile(r"\bmcp__|/mnt/|/Users/|[A-Za-z]:\\", re.I),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b|\b(?:sk|cfat|SAM)-[A-Za-z0-9_-]{16,}\b", re.I),
]
# Internal evidence-class vocabulary must never render into a reader-visible
# document; the builder maps these tokens to reader labels.
INTERNAL_CLASS_TOKENS = ("federal_mcp", "official_web", "other_web", "user_statement", "source_class")


def collect_evidence_ids(value) -> set[str]:
    ids: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "evidence_ids" and isinstance(item, list):
                ids.update(str(candidate) for candidate in item)
            else:
                ids.update(collect_evidence_ids(item))
    elif isinstance(value, list):
        for item in value:
            ids.update(collect_evidence_ids(item))
    return ids


def evidence_id_map(record: dict) -> dict[str, str]:
    """Mirror the builder's focused-route renumbering of reader-visible evidence IDs."""
    if record.get("workflow_mode") == "complete_report":
        return {}
    cited = collect_evidence_ids(record.get("validation", {}))
    for item in record.get("findings", []):
        if isinstance(item, dict):
            cited.update(str(value) for value in item.get("evidence_ids", []))
    mapping: dict[str, str] = {}
    for item in record.get("evidence", []):
        if isinstance(item, dict) and item.get("id") in cited:
            mapping[str(item["id"])] = f"E{len(mapping) + 1:03d}"
    return mapping


def all_text(document: Document) -> str:
    parts = [p.text for p in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)


def _looks_synthetic(item: dict) -> bool:
    text = " ".join(
        str(item.get(field, ""))
        for field in ("title", "locator", "fact", "limitations")
    ).lower()
    return any(marker in text for marker in ("fixture", "synthetic", "no live", "test data only"))


def evidence_supports_complete_label(record: dict) -> bool:
    evidence = [item for item in record.get("evidence", []) if isinstance(item, dict)]
    live_federal = any(
        item.get("source_class") == "federal_mcp" and not _looks_synthetic(item)
        for item in evidence
    )
    public_web = any(item.get("source_class") in {"official_web", "other_web"} for item in evidence)
    commercial_approved = record.get("validation", {}).get("commercial_evidence_complete") is True
    return live_federal and public_web and commercial_approved


def validate(document_path: Path, record_path: Path) -> dict:
    failures: list[str] = []
    if not zipfile.is_zipfile(document_path):
        return {"status": "fail", "failures": ["file is not a valid DOCX ZIP"]}
    document = Document(document_path)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    text = all_text(document)
    headings = [p.text.strip() for p in document.paragraphs if getattr(p.style, "name", "") == "Heading 1"]
    route = record.get("workflow_mode")
    required_headings = list(ROUTE_HEADINGS.get(route, []))
    if route == "one_question" and record.get("validation", {}).get("analysis_focus") == "small_business":
        required_headings = [
            "Bounded answer",
            "Candidate small-business market",
            "Rule of Two evidence assessment",
            "Evidence supporting and cutting against a small-business strategy",
            "Targeted outreach plan",
            "Decision implications",
            "Further research options",
            "Human-owned decisions and unknowns",
            "Method, limitations, and evidence",
        ]
    if not required_headings:
        failures.append(f"unsupported workflow_mode for report validation: {route}")
    for heading in required_headings:
        if heading not in headings:
            failures.append(f"missing Heading 1 section: {heading}")
    if [h for h in headings if h in required_headings] != required_headings:
        failures.append("required Heading 1 sections are out of order")
    for label in ("BOTTOM LINE", "Decision implications", "Next practical actions"):
        if label not in text:
            failures.append(f"first-page decision product element is missing: {label}")
    for pattern in FORBIDDEN:
        if pattern.search(text):
            failures.append(f"forbidden content matched: {pattern.pattern}")
    for token in INTERNAL_CLASS_TOKENS:
        if token in text:
            failures.append(f"internal evidence-class token rendered in the document: {token}")
    id_map = evidence_id_map(record)
    for item in record.get("findings", []):
        for evidence_id in item.get("evidence_ids", []):
            if id_map.get(evidence_id, evidence_id) not in text:
                failures.append(f"finding evidence ID not present in report: {evidence_id}")
    complete = evidence_supports_complete_label(record)
    if route == "complete_report" and not complete and "Federal-Data Desk-Research Draft" not in text:
        failures.append("incomplete commercial evidence is not labeled as a desk-research draft")
    if route == "complete_report" and not complete and "FAR Part 10 Market Research Report" in text:
        failures.append("incomplete evidence is mislabeled as a FAR Part 10 Market Research Report")
    evidence = [item for item in record.get("evidence", []) if isinstance(item, dict)]
    # Every [E###] identifier rendered in the document must resolve to a row
    # of the rendered evidence register (the record's own IDs for the complete
    # report, the renumbered IDs for focused routes).
    if route == "complete_report":
        rendered_register_ids = {str(item.get("id")) for item in evidence}
    else:
        rendered_register_ids = set(id_map.values())
    cited_in_document = {
        cited
        for group in re.findall(r"\[([^\[\]]+)\]", text)
        for cited in re.findall(r"\bE\d{3,}\b", group)
    }
    dangling = sorted(cited_in_document - rendered_register_ids)
    if dangling:
        failures.append(
            "dangling evidence citations in the document: "
            + ", ".join(dangling)
            + " do not appear in the evidence register"
        )
    numeric_checks = record.get("validation", {}).get("numeric_checks", []) if route == "complete_report" else []
    for index, check in enumerate(numeric_checks):
        expected = sum(float(value) for value in check.get("components", []))
        reported = float(check.get("reported_total", expected))
        label = check.get("label", "numeric check")
        if abs(expected - reported) > 0.005:
            failures.append(f"independent recomputation failed for {label}")
        calculated_total = f"{expected:,.2f}"
        calculation_lines = [
            paragraph.text
            for paragraph in document.paragraphs
            if label in paragraph.text and calculated_total in paragraph.text
        ]
        if not calculation_lines:
            failures.append(f"recomputed total is missing from report: {expected:,.2f}")
            continue
        locator = f"validation.numeric_checks[{index}]"
        calculation_ids = [
            item.get("id")
            for item in evidence
            if item.get("source_class") == "calculation" and item.get("locator") == locator
        ]
        if len(calculation_ids) != 1:
            failures.append(
                f"numeric check {label} does not have exactly one calculation evidence item for {locator}"
            )
            continue
        for evidence_id in calculation_ids:
            if not any(f"[{evidence_id}]" in line for line in calculation_lines):
                failures.append(
                    f"numeric check {label} does not cite its calculation evidence ID: {evidence_id}"
                )
    return {"status": "pass" if not failures else "fail", "heading_count": len(headings), "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.document, args.record)
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "pass":
        print("Market research DOCX validation passed.")
    else:
        print("VALIDATION FAILED")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
