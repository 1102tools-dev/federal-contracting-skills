# OT Cost Analysis Validation Gates

Run all available layers against the final workbook and rerun after any change.

Delivery gate: the workbook must pass the `validate_workbook.py` structural
audit with the canonical seven-sheet layout before delivery. A bespoke sheet
set is not permitted even when its content is correct. A validator failure of
any kind, including missing canonical sheets or missing print setup, blocks
delivery; fix and revalidate instead of delivering with caveats.

## 1. Validation input

Create temporary JSON from the same raw objects used to build the workbook. Minimal shape:

```json
{
  "assumptions": {
    "authority": "prototype",
    "authority_path": "C",
    "performer_share_ratio": 0.3333333333333333,
    "fee_rate": 0.02,
    "burden_multiplier": 2.0,
    "labor_aging_factor": 1.03,
    "labor_escalation_rate": 0.025,
    "materials_escalation_rate": 0.03,
    "cost_type_ceiling_margin": 0.15
  },
  "milestones": [
    {
      "id": "M1",
      "payment_type": "Fixed",
      "months_from_start": 0,
      "labor_lines": [
        {"name": "Software Developer", "annual_wage": 132000, "hours": 1880}
      ],
      "materials": 100000,
      "travel": 10000,
      "odcs": 5000,
      "proposed_amount": null,
      "workbook_project_cost_cell": "'OT Cost Summary'!D19",
      "workbook_government_funding_cell": "'OT Cost Summary'!I19"
    }
  ],
  "workbook_total_project_cost_cell": "'OT Cost Summary'!D20",
  "workbook_total_government_funding_cell": "'OT Cost Summary'!I20",
  "formula_assertions": [
    {
      "cell": "'OT Cost Summary'!B8",
      "contains": ["VALUE(LEFT(B7,4))", "VALUE(MID(B7,6,2))"],
      "not_contains": ["DATEDIF", "YEAR("]
    }
  ]
}
```

For production, set `production_ratio_source` to a nonempty user-supplied source. Do not label the ratio inherited. For Path D, set `exceptional_circumstances_confirmed` only from user-supplied facts.

## 2. Formula structure

Run:

```text
python scripts/validate_workbook.py workbook.xlsx --expected inputs.json --engine none
```

The audit checks:

- Seven required sheets
- Summary B8/B9 aging formulas and forbidden `DATEDIF`/`YEAR(` patterns
- Formula presence and formula-error tokens
- Cost-share and fee formulas supplied as assertions
- Blank pre-solicitation proposed cells and conditional variance formulas
- Cost-type Government and performer branches using the same ceiling basis
- No stale `competition commitment` Path D language
- No automatic 100% Government funding claim for 4021 or 4022(f)
- No generated price-reasonableness conclusion
- Every Milestone Detail labor line priced from `Labor Benchmarking` matches its own benchmark row or carries a Basis naming the proxy source
- No category repeats identical hours across milestones without an `Hours basis:` reconciliation note
- Milestone labor hours are derived, not asserted: every priced labor row exposes FTE loading, weeks or duration, and hours-per-FTE-week input cells; its Hours cell is a formula referencing those cells; each milestone carries a formula reconciliation rendering `OK` or `MISMATCH` rather than prose; and no other canonical sheet restates milestone hours as literals
- Narrative columns (Description, Basis, Source note) wrap text and meet the 28-character width floor
- Every canonical sheet has an explicit print area, enables fitToPage scaling (`ws.sheet_properties.pageSetUpPr.fitToPage`), and uses landscape orientation when it spans more than 8 used columns
- For recost workbooks: no benchmark rows for roles absent from Milestone Detail, no lump-sum labor deltas without Hours and Rate cells, and a delta row for every element listed in the optional `recost_register_elements` payload array (list every cost element the change register names; a $0 delta needs a one-line justification)
- A readable first-view dashboard states the prototype, analysis purpose, milestone basis, funding planning range, contribution treatment, key drivers, source limitations, and next action without horizontal scrolling

## 3. Independent recomputation

Run:

```text
python scripts/recompute_expected_values.py inputs.json
```

The script independently computes aged labor, burdened labor, materials escalation, total project cost, contribution shares, fee, cost-type ceiling view, and Government funding requirement. It also validates authority-path arithmetic.

Do not derive expected values from workbook formula results.

## 4. Real-engine verification

Run:

```text
python scripts/validate_workbook.py workbook.xlsx --expected inputs.json --engine auto
```

The validator recalculates a temporary copy through LibreOffice when available and reopens cached values. It scans every cell on every recalculated worksheet for cached spreadsheet errors before comparing referenced cells with the independent computation. Use `--engine libreoffice` to require this layer.

## 5. Named regression gates

### Authority and cost share

- Path D means written exceptional circumstances, never competition commitment.
- Path C performer share is at least exact one-third of total project cost.
- Research ratio is user supplied; no automatic zero or 50 percent.
- Production ratio is user supplied; no automatic zero and no inherited prototype ratio.
- Government and performer project shares reconcile before separately treated fees.

### Proposed amount

- Amount basis is explicit.
- Comparison uses the matching workbook basis.
- A blank proposed amount yields a blank variance, not text or a formula error.

### Formula behavior

- Milestone labor hours are a formula over driver input cells; an asserted hours literal is a delivery failure even when the number is right.
- The per-milestone hours reconciliation is a formula with an `OK` or `MISMATCH` result, not a sentence asserting that the hours reconcile.
- Sheets that restate milestone hours link to `Milestone Detail` instead of duplicating literals.
- BLS aging is cell referenced.
- Materials escalation uses milestone-start months.
- Cost-type Government and performer values use the same ceiling basis.
- Fee uses an approved base and defaults to zero.
- Cumulative Government funding is a running formula.
- Dynamic Milestone Detail blocks do not rely on a fixed row stride.
- Summary milestone and total references resolve to the actual dynamic block total rows; displayed zeroes caused by off-by-one or missing cached references are a delivery failure.

### Data sources and pacing

- CALC+ keyword calls use `keyword=`, never `q=`.
- Discovery records `aggregations.labor_category.buckets` keys and counts.
- `detect_latest_year` controls the BLS vintage.
- Keyed calls are serialized with at least three seconds between them.

### AI boundary

- Workflow B first response stops at Option A or B without tool calls.
- Option A contains neutral evidence and no verdict.
- Option B conclusion text is verbatim user text and visibly marked DRAFT.

## 6. Result language

When all three layers pass, state:

> Formula structure, independent calculations, and LibreOffice formula execution passed.

Without a real engine, state exactly:

> Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.
