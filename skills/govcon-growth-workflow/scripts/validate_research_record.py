#!/usr/bin/env python3
"""Validate a normalized 1102tools research record without network access."""

from __future__ import annotations

import argparse
import ipaddress
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse


REQUIRED = {
    "schema_version",
    "skill",
    "workflow_mode",
    "question",
    "scope",
    "document_register",
    "user_context",
    "assumptions",
    "web_research",
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
LIST_FIELDS = REQUIRED - {"schema_version", "skill", "workflow_mode", "question", "scope", "web_research", "validation"}
SOURCE_CLASSES = {"document", "federal_mcp", "official_web", "other_web", "user_statement", "calculation"}
SKILLS = {
    "market-research-workflow",
    "market-research-builder",  # Legacy record identifier accepted during the RC transition.
    "govcon-growth-workflow",
}
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
WEB_MODES = {
    "tavily_with_native_fallback": {"tavily", "native_web"},
    "native_only": {"native_web"},
    "tavily_only": {"tavily"},
    "no_public_web": set(),
}
QUERY_PROVIDERS = {"federal_mcp", "tavily", "native_web"}
TAVILY_OPERATIONS = {"tavily_search", "tavily_extract"}
SENSITIVE_URL_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "key",
    "password",
    "secret",
    "sig",
    "signature",
    "token",
    "x-amz-credential",
    "x-amz-signature",
}


def public_url_failure(value: str) -> str | None:
    try:
        parsed = urlparse(value)
    except ValueError:
        return "is not a valid URL"
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "must be a public HTTP or HTTPS URL"
    if parsed.username or parsed.password:
        return "must not contain URL credentials"
    hostname = parsed.hostname.lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal", ".test")):
        return "must not target a local or internal host"
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address and not address.is_global:
        return "must not target a private, loopback, link-local, or reserved address"
    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    unsafe = sorted(query_keys & SENSITIVE_URL_KEYS)
    if unsafe:
        return "contains a credential-like query key: " + ", ".join(unsafe)
    return None


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

    if record.get("schema_version") != "1.1":
        failures.append("schema_version must be 1.1")
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

    web = record.get("web_research")
    approved_web_providers: set[str] = set()
    if not isinstance(web, dict):
        failures.append("web_research must be an object")
    else:
        expected_web_fields = {
            "mode",
            "approved",
            "approved_at",
            "disclosure_acknowledged",
            "planned_providers",
            "providers_used",
            "fallback_events",
        }
        missing_web = sorted(expected_web_fields - set(web))
        unknown_web = sorted(set(web) - expected_web_fields)
        if missing_web:
            failures.append("web_research missing fields: " + ", ".join(missing_web))
        if unknown_web:
            failures.append("web_research unknown fields: " + ", ".join(unknown_web))
        mode = web.get("mode")
        if mode not in WEB_MODES:
            failures.append("web_research.mode is not approved")
            expected_providers: set[str] = set()
        else:
            expected_providers = WEB_MODES[mode]
            approved_web_providers = set(expected_providers)
        if web.get("approved") is not True:
            failures.append("web_research.approved must be true before validation")
        if not isinstance(web.get("approved_at"), str) or not web.get("approved_at", "").strip():
            failures.append("web_research.approved_at must be a non-empty string")
        if web.get("disclosure_acknowledged") is not True:
            failures.append("web_research.disclosure_acknowledged must be true")
        planned = web.get("planned_providers")
        used = web.get("providers_used")
        events = web.get("fallback_events")
        if not isinstance(planned, list) or set(planned) != expected_providers:
            failures.append("web_research.planned_providers must match the approved mode")
        if not isinstance(used, list) or not set(used).issubset(expected_providers):
            failures.append("web_research.providers_used must be a subset of approved providers")
        if not isinstance(events, list):
            failures.append("web_research.fallback_events must be an array")
        else:
            if events and mode != "tavily_with_native_fallback":
                failures.append("web_research.fallback_events are allowed only in tavily_with_native_fallback mode")
            for index, event in enumerate(events):
                if not isinstance(event, dict):
                    failures.append(f"web_research.fallback_events[{index}] must be an object")
                    continue
                if set(event) != {"timestamp", "failed_provider", "replacement_provider", "reason"}:
                    failures.append(f"web_research.fallback_events[{index}] has invalid fields")
                    continue
                if event.get("failed_provider") not in expected_providers or event.get("replacement_provider") not in expected_providers:
                    failures.append(f"web_research.fallback_events[{index}] uses an unapproved provider")
                if event.get("failed_provider") == event.get("replacement_provider"):
                    failures.append(f"web_research.fallback_events[{index}] must switch providers")
                for field in ("timestamp", "reason"):
                    if not isinstance(event.get(field), str) or not event.get(field, "").strip():
                        failures.append(f"web_research.fallback_events[{index}].{field} must be a non-empty string")

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
        provider = query.get("provider")
        if provider not in QUERY_PROVIDERS:
            failures.append(f"queries[{index}].provider is not approved")
        elif provider in {"tavily", "native_web"} and provider not in approved_web_providers:
            failures.append(f"queries[{index}] uses a web provider not approved for this run")
        if not isinstance(query.get("operation"), str) or not query.get("operation", "").strip():
            failures.append(f"queries[{index}].operation must be a non-empty string")
        elif provider == "tavily" and query.get("operation") not in TAVILY_OPERATIONS:
            failures.append(f"queries[{index}] uses a prohibited Tavily operation")
        params = query.get("parameters", {})
        if not isinstance(params, dict):
            failures.append(f"queries[{index}].parameters must be an object")
            continue
        unsafe = sorted({str(key).lower() for key in params} & UNSAFE_QUERY_KEYS)
        if unsafe:
            failures.append(f"queries[{index}] contains unsafe parameter keys: {', '.join(unsafe)}")
        if provider in {"tavily", "native_web"}:
            for key, value in params.items():
                if str(key).lower() not in {"url", "urls"}:
                    continue
                urls = value if isinstance(value, list) else [value]
                for url in urls:
                    if not isinstance(url, str):
                        failures.append(f"queries[{index}].parameters.{key} must contain URL strings")
                        continue
                    problem = public_url_failure(url)
                    if problem:
                        failures.append(f"queries[{index}].parameters.{key} {problem}")

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
