#!/usr/bin/env python3
"""Validate all portable skills, references, shared files, and hygiene."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # The skill runtime does not require PyYAML.
    yaml = None
YAML_ERROR = getattr(yaml, "YAMLError", ValueError)


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
EXPECTED = {
    "igce-builder-cr",
    "igce-builder-ffp",
    "igce-builder-lh-tm",
    "market-research-builder",
    "govcon-growth-workflow",
    "ot-cost-analysis",
    "ot-project-description-builder",
    "sow-pws-builder",
}
ALLOWED_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
FORBIDDEN_HOST_TOKENS = ("AskUserQuestion", "request_user_input", "mcp__", "/mnt/user-data", "present_files(")
SECRET_PATTERNS = (
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:sk|cfat|SAM)-[A-Za-z0-9_-]{16,}\b", re.I),
    re.compile(r"(?:api[_ -]?key|secret|token|password)\s*[:=]\s*[^\s,}\]]{8,}", re.I),
)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError("missing or invalid YAML frontmatter")
    block = match.group(1)
    if yaml is not None:
        return yaml.safe_load(block), text
    parsed: dict[str, object] = {}
    current: str | None = None
    folded: list[str] = []
    for line in block.splitlines():
        field = re.match(r"^([a-z][a-z0-9-]*):(?:\s*(.*))?$", line)
        if field:
            if current is not None:
                parsed[current] = " ".join(part.strip() for part in folded).strip()
            current = field.group(1)
            value = (field.group(2) or "").strip()
            folded = [] if value in {">", "|"} else [value.strip("\"'")]
        elif current is not None and line.startswith((" ", "\t")):
            folded.append(line.strip())
        else:
            raise ValueError("frontmatter requires PyYAML for this structure")
    if current is not None:
        parsed[current] = " ".join(part.strip() for part in folded).strip()
    return parsed, text


def validate() -> list[str]:
    failures: list[str] = []
    actual = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    if actual != EXPECTED:
        failures.append(f"skill catalog mismatch: expected {sorted(EXPECTED)}, found {sorted(actual)}")

    for skill_name in sorted(EXPECTED & actual):
        directory = SKILLS / skill_name
        skill_md = directory / "SKILL.md"
        try:
            frontmatter, text = read_frontmatter(skill_md)
        except (OSError, ValueError, YAML_ERROR) as exc:
            failures.append(f"{skill_name}: {exc}")
            continue
        if not isinstance(frontmatter, dict):
            failures.append(f"{skill_name}: frontmatter is not an object")
            continue
        unknown = sorted(set(frontmatter) - ALLOWED_FRONTMATTER)
        if unknown:
            failures.append(f"{skill_name}: unknown frontmatter fields: {', '.join(unknown)}")
        if frontmatter.get("name") != skill_name:
            failures.append(f"{skill_name}: frontmatter name does not match folder")
        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.startswith("Trigger for:"):
            failures.append(f"{skill_name}: description must begin with 'Trigger for:'")
        elif len(description) > 1024:
            failures.append(f"{skill_name}: description exceeds 1024 characters")
        if len(text.splitlines()) > 500:
            failures.append(f"{skill_name}: SKILL.md exceeds 500 lines")
        for target in LINK.findall(text):
            if "://" in target or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            candidate = (directory / relative).resolve()
            try:
                candidate.relative_to(directory.resolve())
            except ValueError:
                failures.append(f"{skill_name}: reference escapes skill root: {target}")
                continue
            if not candidate.exists():
                failures.append(f"{skill_name}: missing referenced file: {target}")
        yaml_path = directory / "agents" / "openai.yaml"
        if not yaml_path.is_file():
            failures.append(f"{skill_name}: missing agents/openai.yaml")
        runtime_text_files = [skill_md, yaml_path]
        runtime_text_files.extend((directory / "references").rglob("*.md") if (directory / "references").is_dir() else [])
        for file_path in runtime_text_files:
            if not file_path.is_file():
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in FORBIDDEN_HOST_TOKENS:
                if token in content:
                    failures.append(f"{file_path.relative_to(ROOT)}: forbidden host-specific token {token}")
            for pattern in SECRET_PATTERNS:
                if pattern.search(content):
                    failures.append(f"{file_path.relative_to(ROOT)}: possible credential or secret")
                    break

    shared_pairs = [
        (
            SKILLS / "market-research-builder" / "references" / "evidence-contract.md",
            SKILLS / "govcon-growth-workflow" / "references" / "evidence-contract.md",
        ),
        (
            SKILLS / "market-research-builder" / "references" / "web-provider-policy.md",
            SKILLS / "govcon-growth-workflow" / "references" / "web-provider-policy.md",
        ),
        (
            SKILLS / "market-research-builder" / "scripts" / "validate_research_record.py",
            SKILLS / "govcon-growth-workflow" / "scripts" / "validate_research_record.py",
        ),
    ]
    for left, right in shared_pairs:
        if left.read_bytes() != right.read_bytes():
            failures.append(f"shared file drift: {left.relative_to(ROOT)} != {right.relative_to(ROOT)}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    failures = validate()
    if failures:
        print("VALIDATION FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Validated {len(EXPECTED)} skills, references, metadata, shared files, and hygiene.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
