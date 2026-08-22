from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillStaticTests(unittest.TestCase):
    def test_catalog_and_shared_files(self):
        result = subprocess.run([PYTHON, str(ROOT / "scripts" / "validate_skills.py")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_mandatory_launch_sequences_are_front_loaded(self):
        market = (ROOT / "skills/market-research-builder/SKILL.md").read_text(encoding="utf-8")
        growth = (ROOT / "skills/govcon-growth-workflow/SKILL.md").read_text(encoding="utf-8")
        self.assertLess(market.index("## Stage 1: launch menu"), market.index("## Stage 2: mandatory document intake"))
        self.assertLess(market.index("## Stage 2: mandatory document intake"), market.index("## Stage 6: capability preflight"))
        self.assertIn("No research, file generation, capability preflight, web search, or MCP call occurs first", market)
        self.assertIn("No research, file generation, capability preflight, web search, or MCP call occurs first", growth)
        for number in range(1, 7):
            self.assertRegex(market, rf"(?m)^{number}\. ")
        for number in range(1, 10):
            self.assertRegex(growth, rf"(?m)^{number}\. ")


class RecordValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module(
            ROOT / "skills/market-research-builder/scripts/validate_research_record.py",
            "research_record_validator",
        )

    def fixture(self, name: str):
        return json.loads((ROOT / "tests/fixtures" / name).read_text(encoding="utf-8"))

    def test_valid_market_and_growth_records(self):
        for name in ("market-research-record.json", "govcon-growth-record.json"):
            result = self.validator.validate_record(self.fixture(name))
            self.assertEqual(result["status"], "pass", result["failures"])

    def test_unknown_evidence_reference_fails(self):
        record = self.fixture("market-research-record.json")
        record["findings"][0]["evidence_ids"] = ["E999"]
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("unknown evidence" in item for item in result["failures"]))

    def test_sensitive_query_key_fails(self):
        record = self.fixture("market-research-record.json")
        record["queries"][0]["parameters"]["document_text"] = "private text"
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("unsafe parameter" in item for item in result["failures"]))

    def test_credential_pattern_fails(self):
        record = self.fixture("govcon-growth-record.json")
        record["assumptions"].append("token=abcdefghijklmnopqrstuvwxyz123456")
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("credential" in item for item in result["failures"]))


class ArtifactTests(unittest.TestCase):
    def build_and_validate(self, skill: str, record_name: str, builder: str, validator: str, output_name: str):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / output_name
            record = ROOT / "tests/fixtures" / record_name
            build = subprocess.run(
                [PYTHON, str(ROOT / "skills" / skill / "scripts" / builder), str(record), str(output)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            check = subprocess.run(
                [PYTHON, str(ROOT / "skills" / skill / "scripts" / validator), str(output), "--record", str(record)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertGreater(output.stat().st_size, 10_000)
            soffice = shutil.which("soffice")
            if soffice:
                converted = subprocess.run(
                    [soffice, "--headless", "--convert-to", "pdf", "--outdir", directory, str(output)],
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
                self.assertEqual(converted.returncode, 0, converted.stdout + converted.stderr)
                self.assertTrue((Path(directory) / f"{output.stem}.pdf").is_file())

    def test_market_report(self):
        self.build_and_validate(
            "market-research-builder",
            "market-research-record.json",
            "build_market_research_report.py",
            "validate_market_research_report.py",
            "market-research.docx",
        )

    def test_growth_brief(self):
        self.build_and_validate(
            "govcon-growth-workflow",
            "govcon-growth-record.json",
            "build_growth_brief.py",
            "validate_growth_brief.py",
            "growth-brief.docx",
        )


if __name__ == "__main__":
    unittest.main()
