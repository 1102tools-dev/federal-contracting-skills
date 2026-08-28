# OT Cost Analysis Workbook Specification

Build one `.xlsx` with exactly these seven sheets:

1. `OT Cost Summary`
2. `Milestone Detail`
3. `Scenario Analysis`
4. `Labor Benchmarking`
5. `Cost Share & Funding`
6. `Methodology`
7. `Raw Data`

## 1. OT Cost Summary

### First-view decision dashboard

The first visible area must be a decision dashboard, not a wall of assumptions.
Show the prototype objective, analysis purpose, selected milestone basis,
Government funding planning range, performer contribution treatment, three key
drivers, and next required action. Keep formulas and editable assumptions below
the dashboard. Use a route-specific workbook title, for example "Independent
Prototype Cost Model" or "Recosting Decision Book."

### Assumptions

Keep these cells stable so validators and downstream users can audit formulas:

| Cell | Label | Handling |
|---|---|---|
| B2 | Working burden multiplier | Blue user input; no universal default |
| B3 | Annual labor escalation | Blue user input |
| B4 | Performer share of total project cost | Blue user input; Path C must be at least `1/3` |
| B5 | Government-paid fee rate | Blue user input; zero unless supplied |
| B6 | BLS vintage | `YYYY-MM` text from runtime data |
| B7 | Agreement start | `YYYY-MM` text |
| B8 | Months gap | Formula using `VALUE(LEFT(...))` and `VALUE(MID(...))` |
| B9 | Labor aging factor | Formula `=(1+B3)^(B8/12)` |
| B10 | Materials escalation | Blue user input |
| B11 | Cost-type ceiling margin | Blue user input; zero or blank when not applicable |
| B12 | Productive hours/year | Blue user input |
| B13 | Authority | Text input: `4021 Research`, `4022 Prototype`, or `4022(f) Production` |
| B14 | 4022(d) path | A, B, C, D, or `N/A` |
| B15 | Proposed amount basis | Total project cost, Government request, milestone payment, ceiling, or `None` |

Required month-gap formula pattern in B8:

```text
=(VALUE(LEFT(B7,4))-VALUE(LEFT(B6,4)))*12
 +VALUE(MID(B7,6,2))-VALUE(MID(B6,6,2))
```

Do not use `YEAR()` on text or `DATEDIF`.

### Milestone summary

Start the header at row 18:

| Column | Field |
|---|---|
| A | Milestone ID |
| B | Description |
| C | Payment Type |
| D | Should-Cost |
| E | Ceiling Basis |
| F | Government Project Share |
| G | Performer Project Share |
| H | Fee |
| I | Government Funding Requirement |
| J | Proposed Amount |
| K | Variance Dollars |
| L | Variance Percent |

Use formulas starting at row 19. For a fixed milestone, Ceiling Basis equals Should-Cost. For a cost-type milestone, Ceiling Basis equals Should-Cost multiplied by `(1 + $B$11)` unless the user supplies a fixed ceiling.

Minimum formulas for row 19:

```text
E19 =IF(C19="Cost-Type",D19*(1+$B$11),D19)
F19 =E19*(1-$B$4)
G19 =E19*$B$4
H19 =E19*$B$5
I19 =F19+H19
K19 =IF(J19="","",J19-D19)
L19 =IF(OR(J19="",D19=0),"",(J19-D19)/D19)
```

The proposed-amount comparison formula must match the confirmed basis. If J contains a Government funding request, compare it to I instead of D and label the header accordingly. Never compare unlike bases.

Use a totals row with `SUM` formulas. Keep proposed cells blank in pre-solicitation mode.

## 2. Milestone Detail

Use one dynamic block per milestone. Compute block positions before writing cross-sheet formulas or use defined names. A fixed row stride is not permitted because labor, materials, travel, and ODC line counts vary.

Each block contains:

- Milestone metadata, dates, duration, completion evidence, payment type, and funding convention
- Labor lines: performer, location, category, SOC, hours, burdened-rate reference, and formula cost
- Materials: item, quantity, unit, source, base unit cost, escalation, and formula cost
- Travel: destination, trips, travelers, nights, source FY, and formula cost
- ODC lines and source
- Formula subtotals and total project cost
- Formula Government and performer shares
- Formula fee and Government funding requirement
- For cost-type milestones, the parallel ceiling view

Labor rates reference `Labor Benchmarking`. Do not hardcode a burdened rate in a Milestone Detail cost formula.

## 3. Scenario Analysis

Show user-approved low, working, and high assumptions. Include total project cost, Government project share, performer project share, fee, and Government funding requirement for each scenario. Use formulas referencing scenario inputs and milestone totals.

Describe the proposed amount numerically against the range without a verdict.

## 4. Labor Benchmarking

One row per performer, location, labor category, SOC, and level:

- Direct BLS selected percentile
- Runtime BLS vintage
- Aging factor linked to Summary B9
- Aged direct hourly benchmark
- Approved burden multiplier
- Formula burdened benchmark
- CALC+ P25, P50, P75, sample size, query type, and date
- Proxy or fallback note

Keep institutional billing rates distinct from BLS-derived rates and label their source.

## 5. Cost Share & Funding

Per milestone show:

- Total project-cost basis
- Government share dollars and percent
- Performer cash contribution
- Performer in-kind contribution
- Total performer contribution and percent
- Fee and fee treatment
- Government funding requirement
- Planned obligation or payment period
- Cumulative Government funding

Government project share plus total performer contribution must reconcile to total project cost before separately treated fees. The cumulative column uses a running `SUM` formula.

For cost-type milestones, show should-cost and ceiling rows separately. Label ceiling rows `maximum exposure planning view`.

## 6. Methodology

Use sections:

1. Authority and user-supplied eligibility facts
2. Analysis purpose and proposed-amount basis
3. Milestone and should-cost methodology
4. Labor benchmarking
5. Materials, travel, and ODC bases
6. Contribution and fee treatment
7. Neutral comparison and scenarios
8. Data sources and as-of dates (compact evidence table, not raw payloads)
9. Limitations, open decisions, and refresh needs

Do not call the workbook an IGCE or a FAR 15.404 analysis. Do not state a price-reasonableness conclusion. For Workflow B Option B, place only the user's exact text in a separate block titled `DRAFT - USER-SUPPLIED DETERMINATION TEXT`.

## 7. Raw Data

Record compact reproducible inputs and outputs from BLS, CALC+, Per Diem, analogous prices, quotes, and user overrides. Do not paste full payloads or credentials.

## Formula and presentation rules

- Blue font for user-adjustable inputs; black font for formulas.
- Currency: `$#,##0.00;($#,##0.00)`.
- Percentage: `0.0%`.
- Multipliers: `0.0000`.
- Real Excel formulas for every derived value.
- Freeze panes below assumptions and header rows.
- Light header fills, filters, explicit widths, and readable source notes.
- No formula-error tokens, prompt text, local paths, tool namespaces, keys, or internal instructions.
- Set workbook calculation mode to automatic when supported, but do not claim this evaluates formulas.
- Use differentiated visual treatment by route: independent analysis favors a
  neutral benchmark dashboard; recosting foregrounds before/after deltas and
  changed assumptions. Do not reuse the same title and hierarchy for every output.
- Before delivery, calculate and save the final `.xlsx` through a spreadsheet
  engine so the delivered file carries cached values for every formula displayed
  on `OT Cost Summary`, including each milestone, total should-cost, ceiling
  basis, and Government project share. Render the delivered summary sheet and
  reject blank formula outputs, zeroes that result from missing cached values,
  clipped titles, or a dashboard that requires horizontal scrolling to read.
- Configure the populated print area on every sheet to fit one page wide with no
  fixed page-height limit; use landscape orientation for wide tables. The complete
  `OT Cost Summary` title, decision dashboard, milestone totals, contribution
  treatment, and next action must remain on one page wide when printed or exported.
  Never split the dashboard horizontally.
