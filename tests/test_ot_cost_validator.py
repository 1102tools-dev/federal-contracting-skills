from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "ot-cost-analysis" / "scripts"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "ot_cost_validator_tests",
        SCRIPT_DIR / "validate_workbook.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


class OtCachedErrorAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_cached_error_audit_reports_every_sheet_and_cell(self):
        workbook = Workbook()
        workbook.active.title = "Summary"
        workbook["Summary"]["Z99"] = "#VALUE!"
        detail = workbook.create_sheet("Detail")
        detail["B4"] = "#DIV/0!"

        self.assertEqual(
            self.validator.cached_error_audit(workbook),
            [
                "Summary!Z99 has cached error #VALUE!",
                "Detail!B4 has cached error #DIV/0!",
            ],
        )

    def test_integrated_run_rejects_unmapped_cached_error(self):
        result = self._run_with_calculated_value("#VALUE!")

        self.assertEqual(result["status"], "fail")
        self.assertIn("Calculated!Z99 has cached error #VALUE!", result["failures"])

    def test_integrated_run_accepts_clean_recalculated_workbook(self):
        result = self._run_with_calculated_value(42.0)

        self.assertEqual(result["status"], "pass", result["failures"])

    def _run_with_calculated_value(self, value):
        formula_workbook = Workbook()
        formula_workbook.active["A1"] = "=1+1"
        calculated_workbook = Workbook()
        calculated_workbook.active.title = "Calculated"
        calculated_workbook["Calculated"]["Z99"] = value

        with tempfile.TemporaryDirectory() as directory:
            workbook_path = Path(directory) / "fixture.xlsx"
            expected_path = Path(directory) / "expected.json"
            formula_workbook.save(workbook_path)
            expected_path.write_text("{}", encoding="utf-8")
            recalculated_temp = tempfile.TemporaryDirectory()
            self.addCleanup(recalculated_temp.cleanup)

            with (
                mock.patch.object(self.validator, "load_payload", return_value={}),
                mock.patch.object(self.validator, "calculate", return_value={}),
                mock.patch.object(self.validator, "structural_audit", return_value=[]),
                mock.patch.object(self.validator, "find_soffice", return_value=Path("/fake/soffice")),
                mock.patch.object(
                    self.validator,
                    "recalculate",
                    return_value=(recalculated_temp, Path(directory) / "recalculated.xlsx"),
                ),
                mock.patch.object(
                    self.validator,
                    "load_workbook",
                    side_effect=[formula_workbook, calculated_workbook],
                ),
                mock.patch.object(self.validator, "compare", return_value=[]),
            ):
                return self.validator.run(workbook_path, expected_path, "auto", 0.01)


if __name__ == "__main__":
    unittest.main()
