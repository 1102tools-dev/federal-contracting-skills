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


def multi_period_workbook(handling_value=0) -> Workbook:
    workbook = fixture_workbook(handling_value)
    summary = workbook["IGCE Summary"]
    summary["A5"] = "Escalation Rate"
    summary["A14"] = "Total Periods (Base plus Options)"
    summary["B14"] = 3
    summary["A20"] = "Base Year total"
    summary["A21"] = "Option Year 1 total"
    summary["A22"] = "Option Year 2 total"
    return workbook


def scenario_period_workbook(
    mid_values=(2500000.0, 2562500.0, 2626562.5), zeroed=False
) -> Workbook:
    """Multi-period fixture with a Scenario Analysis period-totals table.

    The IGCE Summary per-period totals are always the nonzero mid_values; the
    scenario table carries the same values unless zeroed is set, which models a
    stale-formula workbook whose cached scenario results collapsed to zero.
    """
    workbook = multi_period_workbook()
    scenario_values = (0.0, 0.0, 0.0) if zeroed else mid_values

    summary = workbook["IGCE Summary"]
    summary["B20"] = mid_values[0]
    summary["B21"] = mid_values[1]
    summary["B22"] = mid_values[2]
    summary["A23"] = "TOTAL ALL PERIODS"
    summary["B23"] = sum(mid_values)

    register = workbook["Raw Data"]
    register["A1"] = "Per-period labor totals"
    for offset, amount in enumerate((*mid_values, sum(mid_values))):
        register.cell(row=2 + offset, column=1, value=amount)

    scenario = workbook["Scenario Analysis"]
    scenario["A20"] = "PERIOD TOTALS FROM THE BURDENED RATES ABOVE"
    scenario["A21"] = "Period"
    scenario["B21"] = "Labor (Mid)"
    scenario["A22"] = "Base Year"
    scenario["B22"] = scenario_values[0]
    scenario["A23"] = "Option Year 1"
    scenario["B23"] = scenario_values[1]
    scenario["A24"] = "Option Year 2"
    scenario["B24"] = scenario_values[2]
    scenario["A25"] = "TOTAL LABOR, ALL PERIODS"
    scenario["B25"] = sum(scenario_values)
    return workbook


def multi_period_payload() -> dict:
    payload = fixture_payload()
    payload["assumptions"]["periods"] = 3
    return payload


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

    def test_multi_period_fixture_passes(self):
        result = self._run(multi_period_workbook(), multi_period_payload())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_multi_period_without_per_period_totals_fails(self):
        workbook = multi_period_workbook()
        summary = workbook["IGCE Summary"]
        for coordinate in ("A20", "A21", "A22"):
            summary[coordinate] = None

        result = self._run(workbook, multi_period_payload())

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any("no per-period totals" in failure for failure in failures),
            failures,
        )

    def test_dead_escalation_input_fails(self):
        workbook = multi_period_workbook()
        summary = workbook["IGCE Summary"]
        summary["A5"] = None
        summary["A6"] = "Escalation Rate"
        summary["C6"] = 0.03

        result = self._run(workbook, multi_period_payload())

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any("referenced by zero formulas" in failure for failure in failures),
            failures,
        )

    def test_undisclosed_summary_money_constant_fails(self):
        workbook = multi_period_workbook()
        summary = workbook["IGCE Summary"]
        summary["A25"] = "Other direct costs"
        summary["B25"] = 75000

        result = self._run(workbook, multi_period_payload())

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any("Raw Data refresh register" in failure for failure in failures),
            failures,
        )

    def test_registered_summary_money_constant_passes(self):
        workbook = multi_period_workbook()
        summary = workbook["IGCE Summary"]
        summary["A25"] = "Other direct costs"
        summary["B25"] = 75000
        register = workbook["Raw Data"]
        register["A1"] = "ODCs"
        register["B1"] = "$75,000 vendor quote"

        result = self._run(workbook, multi_period_payload())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_scenario_period_totals_tied_to_summary_pass(self):
        result = self._run(scenario_period_workbook(), multi_period_payload())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_zeroed_scenario_period_totals_fail(self):
        result = self._run(
            scenario_period_workbook(zeroed=True), multi_period_payload()
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any(
                "are all zero while IGCE Summary per-period totals are nonzero"
                in failure
                for failure in failures
            ),
            failures,
        )

    def test_scenario_period_total_off_by_more_than_one_dollar_fails(self):
        workbook = scenario_period_workbook()
        workbook["Scenario Analysis"]["B22"] = 2500005.0

        result = self._run(workbook, multi_period_payload())

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        failures = json.loads(result.stdout)["failures"]
        self.assertTrue(
            any(
                "no IGCE Summary amount for that period is within $1" in failure
                for failure in failures
            ),
            failures,
        )

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
