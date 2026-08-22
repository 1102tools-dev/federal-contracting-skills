from __future__ import annotations

import importlib.util
import json
import copy
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
        self.assertIn("No research, file generation, capability preflight, web-research request, or MCP tool invocation occurs first", market)
        self.assertIn("No research, file generation, capability preflight, web-research request, or MCP tool invocation occurs first", growth)
        for text in (market, growth):
            self.assertIn("Tavily with native fallback", text)
            self.assertIn("native only", text)
            self.assertIn("Tavily only", text)
            self.assertIn("no public web", text)
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

    def web_fixture(self, mode: str, planned: list[str], used: list[str] | None = None):
        record = self.fixture("market-research-record.json")
        record["web_research"] = {
            "mode": mode,
            "approved": True,
            "approved_at": "2026-08-21T19:00:00Z",
            "disclosure_acknowledged": True,
            "planned_providers": planned,
            "providers_used": list(used or []),
            "fallback_events": [],
        }
        return record

    def test_all_provider_modes_validate(self):
        modes = {
            "tavily_with_native_fallback": ["tavily", "native_web"],
            "native_only": ["native_web"],
            "tavily_only": ["tavily"],
            "no_public_web": [],
        }
        for mode, providers in modes.items():
            with self.subTest(mode=mode):
                record = self.web_fixture(mode, providers)
                result = self.validator.validate_record(record)
                self.assertEqual(result["status"], "pass", result["failures"])

    def test_combined_mode_records_approved_fallback(self):
        record = self.web_fixture(
            "tavily_with_native_fallback",
            ["tavily", "native_web"],
            ["tavily", "native_web"],
        )
        record["web_research"]["fallback_events"] = [{
            "timestamp": "2026-08-21T19:05:00Z",
            "failed_provider": "tavily",
            "replacement_provider": "native_web",
            "reason": "Simulated rate limit",
        }]
        record["queries"].append({
            "provider": "native_web",
            "operation": "native search",
            "parameters": {"query": "official federal market research guidance"},
            "retrieved_at": "2026-08-21T19:06:00Z",
            "count": 3,
            "limitations": "Synthetic fallback fixture",
        })
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "pass", result["failures"])

    def test_unapproved_provider_fails(self):
        record = self.web_fixture("native_only", ["native_web"], ["native_web"])
        record["queries"].append({
            "provider": "tavily",
            "operation": "tavily-search",
            "parameters": {"query": "public query"},
            "retrieved_at": "2026-08-21T19:06:00Z",
            "count": 1,
            "limitations": "Synthetic fixture",
        })
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("not approved" in item for item in result["failures"]))

    def test_fallback_event_requires_combined_mode_and_provider_switch(self):
        record = self.web_fixture("tavily_only", ["tavily"], ["tavily"])
        record["web_research"]["fallback_events"] = [{
            "timestamp": "2026-08-21T19:05:00Z",
            "failed_provider": "tavily",
            "replacement_provider": "tavily",
            "reason": "Synthetic invalid fallback",
        }]
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("allowed only" in item for item in result["failures"]))
        self.assertTrue(any("must switch providers" in item for item in result["failures"]))

    def test_unapproved_or_unacknowledged_plan_fails(self):
        record = self.web_fixture("tavily_only", ["tavily"])
        record["web_research"]["approved"] = False
        record["web_research"]["disclosure_acknowledged"] = False
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("approved must be true" in item for item in result["failures"]))
        self.assertTrue(any("disclosure_acknowledged" in item for item in result["failures"]))

    def test_private_and_signed_urls_fail(self):
        base = self.web_fixture("tavily_only", ["tavily"], ["tavily"])
        bad_urls = (
            "file:///Users/example/private.pdf",
            "http://127.0.0.1/report",
            "https://intranet.internal/report",
            "https://example.com/report?token=secret-value",
        )
        for url in bad_urls:
            with self.subTest(url=url):
                record = copy.deepcopy(base)
                record["queries"].append({
                    "provider": "tavily",
                    "operation": "tavily-extract",
                    "parameters": {"urls": [url]},
                    "retrieved_at": "2026-08-21T19:06:00Z",
                    "count": 0,
                    "limitations": "Synthetic safety fixture",
                })
                result = self.validator.validate_record(record)
                self.assertEqual(result["status"], "fail")
                self.assertTrue(any("parameters.urls" in item for item in result["failures"]))

    def test_public_extraction_url_passes(self):
        record = self.web_fixture("tavily_only", ["tavily"], ["tavily"])
        record["queries"].append({
            "provider": "tavily",
            "operation": "tavily-extract",
            "parameters": {"urls": ["https://www.acquisition.gov/far/part-10"]},
            "retrieved_at": "2026-08-21T19:06:00Z",
            "count": 1,
            "limitations": "Synthetic safety fixture",
        })
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "pass", result["failures"])


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
