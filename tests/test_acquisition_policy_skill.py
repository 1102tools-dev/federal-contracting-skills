from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "acquisition-policy-workflow"
FIXTURE = ROOT / "tests" / "fixtures" / "acquisition-policy-record.json"
PYTHON = sys.executable


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PolicySkillStaticTests(unittest.TestCase):
    def test_menu_and_direct_routing_are_present(self):
        core = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        launch = (SKILL / "references" / "launch-menu-and-framing.md").read_text(encoding="utf-8")
        self.assertIn("An unambiguous request may enter its matching mode directly", core)
        for number in range(1, 11):
            self.assertRegex(launch, rf"(?m)^{number}\. ")
        self.assertIn(
            "Which option would you like? You can reply with the number, label, or your own wording.",
            launch,
        )

    def test_boundary_language_is_front_loaded(self):
        core = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("FAR Council model deviation text is not operative for an agency", core)
        self.assertIn("Never describe a proposed rule", core)
        self.assertIn("Public comments are stakeholder evidence", core)
        self.assertIn("Do not substitute direct HTTP", core)


class PolicyRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module(
            SKILL / "scripts" / "validate_policy_research_record.py",
            "policy_record_validator_tests",
        )

    def fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assert_fails_with(self, record, phrase: str):
        result = self.validator.validate_record(record)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(phrase in failure for failure in result["failures"]), result["failures"])

    def test_valid_record(self):
        result = self.validator.validate_record(self.fixture())
        self.assertEqual(result["status"], "pass", result["failures"])

    def test_model_deviation_cannot_be_operative(self):
        record = self.fixture()
        record["policy_items"][1]["operative_for_agency"] = True
        self.assert_fails_with(record, "cannot mark model_deviation operative")

    def test_proposed_rule_cannot_be_operative(self):
        record = self.fixture()
        record["policy_items"][3]["operative_for_agency"] = True
        self.assert_fails_with(record, "cannot mark proposed_rule operative")

    def test_operative_deviation_requires_deviation_evidence(self):
        record = self.fixture()
        record["policy_items"][2]["evidence_ids"] = ["E002"]
        self.assert_fails_with(record, "must cite agency_deviation evidence")

    def test_unknown_evidence_reference_fails(self):
        record = self.fixture()
        record["findings"][0]["evidence_ids"] = ["E999"]
        self.assert_fails_with(record, "unknown evidence IDs")

    def test_sensitive_query_key_fails(self):
        record = self.fixture()
        record["queries"][0]["parameters"]["document_text"] = "nonpublic acquisition text"
        self.assert_fails_with(record, "unsafe parameter keys")

    def test_stakeholder_sample_requires_method_and_limits(self):
        record = self.fixture()
        record["stakeholder_positions"] = [{
            "id": "S001",
            "position": "Supports the proposal",
            "submitter_type": "Association",
            "sample_method": "",
            "reviewed_count": 1,
            "returned_count": 2,
            "evidence_ids": ["E005"],
            "limitations": "",
        }]
        self.assert_fails_with(record, "sample_method must be a non-empty string")
        self.assert_fails_with(record, "limitations must be a non-empty string")


class PolicyArtifactTests(unittest.TestCase):
    def test_build_and_validate_brief(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "acquisition-policy-impact-brief.docx"
            build = subprocess.run(
                [PYTHON, str(SKILL / "scripts" / "build_acquisition_policy_brief.py"), str(FIXTURE), str(output)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            check = subprocess.run(
                [
                    PYTHON,
                    str(SKILL / "scripts" / "validate_acquisition_policy_brief.py"),
                    str(output),
                    "--record",
                    str(FIXTURE),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertGreater(output.stat().st_size, 20_000)
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


if __name__ == "__main__":
    unittest.main()
