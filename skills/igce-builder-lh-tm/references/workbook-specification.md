# LH/T&M Workbook Specification

Build one `.xlsx` workbook with seven sheets in this order:

1. `IGCE Summary`
2. `Scenario Analysis`
3. `Rate Validation`
4. `Travel Detail`
5. `Materials Detail`
6. `Methodology`
7. `Raw Data`

Keep `Materials Detail` in an LH workbook and mark it `Not Applicable` with numeric zero. This preserves a stable structure without implying that LH reimburses materials.

### First-view decision dashboard

The first visible area of `IGCE Summary` must state the requirement, estimate purpose, LH or T&M structure, period, point estimate and useful range, ceiling-hour and materials exposure, major rate drivers, live-source status, and the next acquisition-team action. Keep the dashboard readable without horizontal scrolling and distinguish hourly-rate, ceiling-hour, travel, and T&M materials effects. Do not make a price-reasonableness determination.

Do not deliver a workbook whose sheets merely exist. Populate the summary, scenarios, rate validation, travel/materials treatment, source limitations, and next actions so a reviewer can understand and challenge the estimate without reverse-engineering formulas.

## 1. IGCE Summary

### Assumption cells

| Cell | Label or value |
|---|---|
| A1:B1 | `IGCE Assumptions (LH/T&M)` |
| A2 / B2 | Low Burden Multiplier / input |
| A3 / B3 | Mid Burden Multiplier / input |
| A4 / B4 | High Burden Multiplier / input |
| A5 / B5 | Escalation Rate / input |
| A6 / B6 | Productive Hours per FTE / input |
| A7 / B7 | Base Year Months / input |
| A8 / B8 | BLS Vintage / `YYYY-MM` text |
| A9 / B9 | Contract Start / `YYYY-MM` text |
| A10 / B10 | Months Gap / formula below |
| A11 / B11 | Aging Factor / formula below |
| A12 / B12 | Contract Type / `LH` or `T&M` |
| A13 / B13 | Total Ceiling Price / user input or blank |
| A14 / B14 | Total Periods (Base plus Options) / whole-number input, 1 for a single-period requirement |

Use:

```excel
B10 =MAX(0,(VALUE(LEFT(B9,4))-VALUE(LEFT(B8,4)))*12+VALUE(MID(B9,6,2))-VALUE(MID(B8,6,2)))
B11 =(1+B5)^(B10/12)
```

Format B11 as `0.0000`. Never use `YEAR` on the text cells or rely on `DATEDIF`.

### Labor and period table

Start below row 15. Include:

- Labor category and SOC
- Location and level
- FTE
- Productive hours per FTE
- Estimated hours by period
- Labor-category ceiling hours by period
- Low, mid, and high burdened hourly rates
- Low, mid, and high labor totals
- Travel and materials as separate rows
- Mid IGCE total
- Total ceiling-price input
- Difference between the mid IGCE and ceiling input

Ceiling hours and total ceiling price are inputs or procurement decisions. Do not overwrite them with calculated estimates.

The headline total must cover every period of the stated period of performance. When `Total Periods` is greater than 1, show per-period totals for the base period and each option period (labeled `Base Year`, `Option Year 1`, and so on) plus the all-periods total; the validator rejects a multi-period requirement whose summary carries no per-period breakdown. Only when the user explicitly scoped the estimate to a single period may the workbook show one period, and then the label adjacent to the headline total must state the coverage (for example `TOTAL PLANNING ESTIMATE (BASE YEAR ONLY)`). Never present a one-year total as the planning estimate for a multi-period requirement.

Every highlighted input must feed calculations. In a multi-period estimate the Escalation Rate input must be referenced by the period pricing formulas (directly or through the aging factor); never hardcode escalation factors while the input cell sits dead. The validator rejects an escalation input referenced by zero formulas when the stated period of performance has more than one period.

Every money line on `IGCE Summary` must trace to a detail sheet or an assumptions input, and its source must appear in the `Raw Data` refresh register. Do not hardcode a money amount of $1,000 or more directly on the summary with no backing detail and no register entry; the validator rejects such constants.

## 2. Scenario Analysis

Use a fixed 13-row block per labor category. Block `N` begins at:

```text
base row = 1 + (N - 1) * 13
```

| Offset | Label | Formula or input |
|---:|---|---|
| 0 | `Scenario Analysis: <LCAT>` | header |
| 1 | BLS Base Annual Wage | source input |
| 2 | Aging Factor | `='IGCE Summary'!$B$11` |
| 3 | Aged Annual Wage | base wage times aging factor |
| 4 | Direct Labor Rate Hourly | aged wage divided by 2,080 |
| 5 | blank | separator |
| 6 | Low Multiplier | `='IGCE Summary'!$B$2` |
| 7 | Low Burdened Rate | direct rate times low multiplier |
| 8 | Mid Multiplier | `='IGCE Summary'!$B$3` |
| 9 | Mid Burdened Rate | direct rate times mid multiplier |
| 10 | High Multiplier | `='IGCE Summary'!$B$4` |
| 11 | High Burdened Rate | direct rate times high multiplier |
| 12 | blank | block separator |

In the first block, Direct Labor Rate Hourly is row 5. Cross-sheet formulas must not use row 4, which is Aged Annual Wage.

Below the blocks, show period totals using the Summary productive-hours and month assumptions. Add travel and materials after labor, never inside burden multiplication.

## 3. Rate Validation

Use columns for labor category, BLS direct rate, multiplier, BLS burdened low/mid/high, CALC+ P25/P50/P75/P90, sample size, divergence from P50, and neutral note. Add title-match and experience-match columns when pools are thin or ambiguous.

Do not use `reasonable`, `acceptable`, `competitive`, `outlier`, or negotiation recommendations.

## 4. Travel Detail

Use a 17-row block per destination. Calculate zero-night trips with zero lodging and one discounted first/last-day M&IE amount. Sum travel into the Summary without burden.

For T&M, label travel as a materials-category ODC. For LH, state the separate reimbursement or CLIN basis supplied by the user. If no basis exists, show the estimate separately and flag that it is not part of the LH labor amount.

## 5. Materials Detail

For T&M, include one row per item:

- Category and description
- Vendor or estimate source
- Base-year actual or estimated cost
- Credits or discounts
- Applicable material-handling indirect cost
- Escalation by period
- Total

Material handling must be a supported indirect cost clearly excluded from labor rates. It is not fee or profit. Do not apply the labor multiplier, G&A, or a default handling percentage.

Use numeric zero when no supported basis was supplied. When a user supplies a supported accounting or solicitation basis, record every nonzero material-handling cell in the validation sidecar under `material_handling_assertions` with the exact cell, numeric value or formula, and basis text. The bundled validator rejects nonzero or formula-driven material handling that is not disclosed there.

For LH, show `Materials Not Applicable to Labor-Hour Contract` and numeric zero.

## 6. Methodology

Include:

- LH or T&M selection and user confirmation
- FAR 16.601 limitations and the fact that the D&F is outside the skill
- Fixed-hourly-rate content
- Productive and ceiling hours by category
- Total ceiling-price input and comparison with the IGCE
- SOC, BLS vintage, location, aging, and escalation
- Multiplier source and any sensitivity convention
- CALC+ pool construction and limitations
- Travel treatment
- T&M materials and material-handling basis, if applicable
- Coverage calculations
- Exclusions and user overrides
- Validation layers actually run

Do not state that the workbook itself establishes the D&F, fair and reasonable pricing, or the binding contract ceiling.

## 7. Raw Data

Record compact, reproducible parameters and result summaries, not full JSON. Include BLS series inputs and percentiles, CALC+ pool terms and statistics, Per Diem locality and rates, multiplier source, material-cost sources, and every fallback.

The refresh register must carry an entry (with the current value) for every money line on `IGCE Summary`, including ODCs, materials pools, and travel, so a reviewer can refresh each amount from its source.

## Formatting and safety

- Blue font for inputs; black for formulas.
- Currency: `$#,##0.00`; percentage: `0.0%`; aging factor: `0.0000`; multiplier: `0.00x`.
- Freeze panes below assumption and header blocks.
- Escape text beginning with `=`, `+`, `-`, or `@`.
- Use numeric zero, not text `TBD`, inside formula ranges.
- Wrap long notes and cap column widths at readable sizes.

### Delivery-view gate

Before delivery, recalculate and save the final workbook through a calculation
engine. The delivered file must retain cached values for formula cells on `IGCE
Summary`, including labor totals, materials, and the ceiling or scenario totals.
Render the summary and fix any blank total, clipped limitation, unreadable
assumption, or summary that requires horizontal scrolling to understand.

Configure the populated print area on every sheet to fit one page wide with no
fixed page-height limit. Use landscape orientation for wide tables. The complete
`IGCE Summary` title, decision dashboard, assumptions, labor totals, ceiling
comparison, travel, and materials treatment must remain on one page wide when
printed or exported; never split the dashboard horizontally.
