from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "igce-builder-lh-tm" / "scripts" / "validate_workbook.py"


def fixture_workbook(handling_value=0) -> Workbook:
    workbook = Workbook()
    workbook.active.title = "IGCE Summary"
    for name in (
        "Scenario Analysis",
        "Rate Validation",
        "Travel Detail",
        "Materials Detail",
        "Methodology",
        "Raw Data",
    ):
        workbook.create_sheet(name)

    summary = workbook["IGCE Summary"]
    summary["B2"] = 1.8
    summary["B3"] = 2.0
    summary["B4"] = 2.2
    summary["B5"] = 0.025
    summary["B8"] = "2026-01"
    summary["B9"] = "2026-01"
    summary["B10"] = (
        "=MAX(0,(VALUE(LEFT(B9,4))-VALUE(LEFT(B8,4)))*12+"
        "VALUE(MID(B9,6,2))-VALUE(MID(B8,6,2)))"
    )
    summary["B11"] = "=(1+B5)^(B10/12)"
    summary["B11"].number_format = "0.0000"

    scenario = workbook["Scenario Analysis"]
    scenario["A1"] = "Scenario Analysis: Test Analyst"
    scenario["B2"] = 100000
    scenario["B3"] = "='IGCE Summary'!$B$11"
    scenario["B3"].number_format = "0.0000"
    scenario["B4"] = "=B2*B3"
    scenario["B5"] = "=B4/2080"
    scenario["B7"] = "='IGCE Summary'!$B$2"
    scenario["B8"] = "=B5*B7"
    scenario["B9"] = "='IGCE Summary'!$B$3"
    scenario["B10"] = "=B5*B9"
    scenario["B11"] = "='IGCE Summary'!$B$4"
    scenario["B12"] = "=B5*B11"

    materials = workbook["Materials Detail"]
    materials["A1"] = "Item"
    materials["G1"] = "Material Handling Indirect"
    materials["A2"] = "Cloud hosting"
    materials["G2"] = handling_value
    return workbook


def fixture_payload() -> dict:
    return {
        "assumptions": {
            "contract_type": "T&M",
            "burden_low": 1.8,
            "burden_mid": 2.0,
            "burden_high": 2.2,
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


class LhTmMaterialHandlingValidatorTests(unittest.TestCase):
    def test_zero_material_handling_passes_integrated_validator(self):
        result = self._run(fixture_workbook(0), fixture_payload())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_undisclosed_percentage_formula_fails_integrated_validator(self):
        result = self._run(fixture_workbook("=D2*E2*0.07"), fixture_payload())

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn(
            "Materials Detail!G2 contains undisclosed material handling '=D2*E2*0.07'",
            payload["failures"][0],
        )

    def test_disclosed_formula_and_basis_pass_integrated_validator(self):
        payload = fixture_payload()
        payload["material_handling_assertions"] = [
            {
                "cell": "'Materials Detail'!G2",
                "equals": "=D2*E2*0.07",
                "basis": "User-supplied accounting practice dated 2026-08-23",
            }
        ]
        result = self._run(fixture_workbook("=D2*E2*0.07"), payload)

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
