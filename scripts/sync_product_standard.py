#!/usr/bin/env python3
"""Synchronize the shared professional-product standard into portable skills."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "professional-product-standard.md"
SKILLS_ROOT = ROOT / "skills"
TARGETS = (
    "acquisition-policy-workflow",
    "govcon-growth-workflow",
    "market-research-workflow",
    "sow-pws-builder",
    "igce-builder-ffp",
    "igce-builder-lh-tm",
    "igce-builder-cr",
    "ot-project-description-builder",
    "ot-cost-analysis",
)


def target_path(skill_name: str) -> Path:
    return SKILLS_ROOT / skill_name / "references" / "professional-product-standard.md"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = CANONICAL.read_bytes()
    failures: list[str] = []
    for skill_name in TARGETS:
        target = target_path(skill_name)
        if args.check:
            if not target.is_file():
                failures.append(f"missing: {target.relative_to(ROOT)}")
            elif target.read_bytes() != expected:
                failures.append(f"out of sync: {target.relative_to(ROOT)}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(expected)
        print(f"synchronized {target.relative_to(ROOT)}")

    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
