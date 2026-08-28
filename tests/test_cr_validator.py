from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "igce-builder-cr" / "scripts" / "validate_workbook.py"


def fixture_workbook() -> Workbook:
    workbook = Workbook()
    workbook.active.title = "IGCE Summary"
    for name in (
        "Cost Buildup",
        "Scenario Analysis",
        "Rate Validation",
        "Travel Detail",
        "Methodology",
        "Raw Data",
    ):
        workbook.create_sheet(name)

    summary = workbook["IGCE Summary"]
    summary["B2"] = 0.32
    summary["B3"] = 0.45
    summary["B4"] = 0.12
    summary["B5"] = 0.005
    summary["B6"] = 0.025
    summary["B7"] = 1880
    summary["B8"] = 12
    summary["B9"] = "2026-01"
    summary["B10"] = "2026-01"
    summary["B11"] = (
        "=MAX(0,(VALUE(LEFT(B10,4))-VALUE(LEFT(B9,4)))*12+"
        "VALUE(MID(B10,6,2))-VALUE(MID(B9,6,2)))"
    )
    summary["B12"] = "=(1+B6)^(B11/12)"
    summary["B12"].number_format = "0.0000"
    summary["B13"] = "CPFF"
    summary["B14"] = 0.07
    summary["A19"] = "Total Periods (Base plus Options)"
    summary["B19"] = 1
    summary["A21"] = "Total estimated cost"
    summary["B21"] = 1000000
    summary["A22"] = "Fee"
    summary["B22"] = 70000
    summary["A23"] = "Total estimated price"
    summary["B23"] = 1070000

    buildup = workbook["Cost Buildup"]
    buildup["A1"] = "Cost Buildup: Test Analyst"
    buildup["B2"] = 100000
    buildup["B3"] = "='IGCE Summary'!$B$12"
    buildup["B3"].number_format = "0.0000"
    buildup["B4"] = "=B2*B3"
    buildup["B5"] = "=B4/2080"
    buildup["B7"] = "='IGCE Summary'!$B$2"
    buildup["B8"] = "=B5*B7"
    buildup["B9"] = "=B5+B8"
    buildup["B10"] = "='IGCE Summary'!$B$3"
    buildup["B11"] = "=B9*B10"
    buildup["B12"] = "=B9+B11"
    buildup["B13"] = "='IGCE Summary'!$B$4"
    buildup["B14"] = "=B12*B13"
    buildup["B15"] = "='IGCE Summary'!$B$5"
    buildup["B16"] = "=(B12+B14)*B15"
    buildup["B17"] = "=B12+B14+B16"
    buildup["B18"] = "='IGCE Summary'!$B$13"
    buildup["B19"] = "='IGCE Summary'!$B$14"
    buildup["B20"] = "=B17*'IGCE Summary'!$B$14"
    buildup["B21"] = "=B17+B20"
    buildup["B22"] = "=B21/B5"

    scenario = workbook["Scenario Analysis"]
    scenario["A1"] = "CPFF Scenario Analysis"
    scenario["A3"] = "Scenario"
    scenario["B3"] = "Estimated cost"
    scenario["C3"] = "Fee"
    scenario["D3"] = "Estimated price"
    scenario["A4"] = "Working"
    scenario["B4"] = 1000000
    scenario["C4"] = 70000
    scenario["D4"] = 1070000
    return workbook


def fixture_payload() -> dict:
    return {
        "assumptions": {
            "fee_type": "CPFF",
            "primary_fee_rate": 0.07,
            "fringe_rate": 0.32,
            "overhead_rate": 0.45,
            "ga_rate": 0.12,
            "fccm_rate": 0.005,
            "aging_factor": 1.0,
            "productive_hours": 1880,
        },
        "labor_lines": [
            {
                "name": "Test Analyst",
                "annual_wage": 100000,
                "fte": 1,
            }
        ],
        "non_labor_lines": [],
    }


class CrValidatorTests(unittest.TestCase):
    def test_conforming_fixture_passes(self):
        result = self._run(fixture_workbook(), fixture_payload())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_price_labeled_total_equal_to_cost_subtotal_fails(self):
        workbook = fixture_workbook()
        workbook["IGCE Summary"]["B23"] = 1000000

        result = self._run(workbook, fixture_payload())

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any("must equal estimated cost" in failure for failure in failures),
            failures,
        )

    def test_scenario_fee_base_drift_from_summary_fails(self):
        workbook = fixture_workbook()
        workbook["Scenario Analysis"]["D4"] = 1080000

        result = self._run(workbook, fixture_payload())

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any("same fee-base rule" in failure for failure in failures),
            failures,
        )

    def test_multi_period_without_per_period_breakdown_fails(self):
        workbook = fixture_workbook()
        workbook["IGCE Summary"]["B19"] = 3
        payload = fixture_payload()
        payload["assumptions"]["periods"] = 3

        result = self._run(workbook, payload)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any("no per-period breakdown" in failure for failure in failures),
            failures,
        )

    def test_multi_period_with_per_period_breakdown_passes(self):
        workbook = fixture_workbook()
        summary = workbook["IGCE Summary"]
        summary["B19"] = 3
        summary["A25"] = "Base Year"
        summary["A26"] = "Option Year 1"
        summary["A27"] = "Option Year 2"
        payload = fixture_payload()
        payload["assumptions"]["periods"] = 3

        result = self._run(workbook, payload)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def _run(self, workbook: Workbook, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workbook_path = root / "fixture.xlsx"
            payload_path = root / "expected.json"
            workbook.save(workbook_path)
            payload_path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(workbook_path),
                    "--expected",
                    str(payload_path),
                    "--engine",
                    "none",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )


if __name__ == "__main__":
    unittest.main()
