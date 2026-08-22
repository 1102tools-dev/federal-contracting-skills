#!/usr/bin/env python3
"""Validate a normalized 1102tools research record without network access."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED = {
    "schema_version",
    "skill",
    "workflow_mode",
    "question",
    "scope",
    "document_register",
    "user_context",
    "assumptions",
    "queries",
    "evidence",
    "findings",
    "inferences",
    "user_decisions",
    "conflicts",
    "unresolved_questions",
    "outputs",
    "validation",
}
LIST_FIELDS = REQUIRED - {"schema_version", "skill", "workflow_mode", "question", "scope", "validation"}
SOURCE_CLASSES = {"document", "federal_mcp", "official_web", "other_web", "user_statement", "calculation"}
SKILLS = {"market-research-builder", "govcon-growth-workflow"}
ID_PATTERNS = {
    "evidence": re.compile(r"^E\d{3,}$"),
    "findings": re.compile(r"^F\d{3,}$"),
    "inferences": re.compile(r"^I\d{3,}$"),
}
SECRET_PATTERNS = [
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:sk|cfat|SAM)-[A-Za-z0-9_-]{16,}\b", re.I),
    re.compile(r"(?:api[_ -]?key|secret|token|password)\s*[:=]\s*[^\s,}\]]{8,}", re.I),
]
UNSAFE_QUERY_KEYS = {
    "document_text",
    "full_text",
    "source_selection_information",
    "proprietary_data",
    "classified_data",
    "cui",
    "password",
    "api_key",
    "token",
    "secret",
}


def walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_record(record: Any) -> dict[str, Any]:
    failures: list[str] = []
    if not isinstance(record, dict):
        return {"status": "fail", "failures": ["record root must be an object"]}

    missing = sorted(REQUIRED - set(record))
    unknown = sorted(set(record) - REQUIRED)
    if missing:
        failures.append("missing top-level fields: " + ", ".join(missing))
    if unknown:
        failures.append("unknown top-level fields: " + ", ".join(unknown))

    if record.get("schema_version") != "1.0":
        failures.append("schema_version must be 1.0")
    if record.get("skill") not in SKILLS:
        failures.append("skill must identify an approved 1102tools research skill")
    if not isinstance(record.get("workflow_mode"), str) or not record.get("workflow_mode", "").strip():
        failures.append("workflow_mode must be a non-empty string")
    if not isinstance(record.get("question"), str) or not record.get("question", "").strip():
        failures.append("question must be a non-empty string")
    if not isinstance(record.get("scope"), dict):
        failures.append("scope must be an object")
    elif not isinstance(record["scope"].get("as_of_date"), str):
        failures.append("scope.as_of_date must be a string")
    if not isinstance(record.get("validation"), dict):
        failures.append("validation must be an object")
    for field in sorted(LIST_FIELDS):
        if not isinstance(record.get(field), list):
            failures.append(f"{field} must be an array")

    serialized = json.dumps(record, ensure_ascii=False)
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized):
            failures.append("record appears to contain a credential or secret")
            break
    for value in walk(record):
        if isinstance(value, float) and not math.isfinite(value):
            failures.append("record contains NaN or infinite numeric data")
            break

    ids: dict[str, set[str]] = {name: set() for name in ID_PATTERNS}
    for collection, pattern in ID_PATTERNS.items():
        values = record.get(collection, [])
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                failures.append(f"{collection}[{index}] must be an object")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not pattern.fullmatch(item_id):
                failures.append(f"{collection}[{index}].id has an invalid format")
                continue
            if item_id in ids[collection]:
                failures.append(f"duplicate ID: {item_id}")
            ids[collection].add(item_id)

    for index, item in enumerate(record.get("evidence", [])):
        if not isinstance(item, dict):
            continue
        if item.get("source_class") not in SOURCE_CLASSES:
            failures.append(f"evidence[{index}].source_class is not approved")
        for field in ("title", "locator", "retrieved_at", "fact", "limitations"):
            if not isinstance(item.get(field), str):
                failures.append(f"evidence[{index}].{field} must be a string")

    for collection in ("findings", "inferences"):
        for index, item in enumerate(record.get(collection, [])):
            if not isinstance(item, dict):
                continue
            refs = item.get("evidence_ids")
            if not isinstance(refs, list) or not refs:
                failures.append(f"{collection}[{index}] must cite at least one evidence ID")
                continue
            unknown_refs = sorted(set(refs) - ids["evidence"])
            if unknown_refs:
                failures.append(f"{collection}[{index}] cites unknown evidence IDs: {', '.join(unknown_refs)}")

    for index, query in enumerate(record.get("queries", [])):
        if not isinstance(query, dict):
            failures.append(f"queries[{index}] must be an object")
            continue
        params = query.get("parameters", {})
        if not isinstance(params, dict):
            failures.append(f"queries[{index}].parameters must be an object")
            continue
        unsafe = sorted({str(key).lower() for key in params} & UNSAFE_QUERY_KEYS)
        if unsafe:
            failures.append(f"queries[{index}] contains unsafe parameter keys: {', '.join(unsafe)}")

    return {
        "status": "pass" if not failures else "fail",
        "evidence_count": len(ids["evidence"]),
        "finding_count": len(ids["findings"]),
        "inference_count": len(ids["inferences"]),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read record: {exc}", file=sys.stderr)
        return 2
    result = validate_record(record)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "pass":
        print("Research record validation passed.")
    else:
        print("VALIDATION FAILED")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
