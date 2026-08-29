# OT Cost Analysis Workbook Specification

Build one `.xlsx` with exactly these seven sheets:

1. `OT Cost Summary`
2. `Milestone Detail`
3. `Scenario Analysis`
4. `Labor Benchmarking`
5. `Cost Share & Funding`
6. `Methodology`
7. `Raw Data`

This sheet set is the delivery contract. A bespoke sheet layout is not permitted
even when its content is correct; `validate_workbook.py` rejects any workbook
missing a canonical sheet, and a rejected workbook is not deliverable.

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

Every labor category priced in Milestone Detail MUST either have its own
SOC-matched benchmark row on `Labor Benchmarking`, or carry a Basis cell that
explicitly names the proxy benchmark used and why it is reasonable (the Basis
text must contain the word `proxy`). Never silently reuse another category's
rate under a generic basis such as "Prior bounded source benchmark".

Milestone labor hours MUST be DERIVED in the workbook, never asserted. A
hardcoded hours figure is not auditable: a reviewer who changes staffing or
duration must see the estimate move. Each priced labor row therefore exposes
its drivers as input cells on the row itself and computes hours from them:

| Column role | Cell type | Header text the validator recognizes |
|---|---|---|
| FTE loading | Blue numeric input | a header containing `FTE` |
| Weeks or duration | Blue numeric input | `Weeks`, or a header containing `duration` |
| Hours per FTE-week | Blue numeric input | a header naming hours per week or per FTE |
| Hours | Formula over the three driver cells | exactly `Hours` |

The hours cell is a real formula referencing those cells on its own row, for
example `=C15*D15*E15`. Never write the product as a literal and never move
the FTE and duration arithmetic into Basis prose; the Basis cell explains the
staffing judgment, it does not carry the math.

Each milestone block also carries a visible reconciliation that is itself a
formula, not a sentence. It compares the block's derived hours to the
milestone duration and staffing and renders a clear state, for example:

```text
=IF(ROUND(F20-SUM(C15:C19)*$B$5*E15,4)=0,"OK","MISMATCH")
```

A prose note beginning `Hours basis:` may accompany the check as narrative,
but it does not satisfy it. Do not repeat identical hours per category across
milestones of different durations.

Any sheet that restates milestone hours, `Scenario Analysis` above all, must
reference the `Milestone Detail` hours cells by formula. Repeating the hours
figures as literals on a second sheet breaks the link the workbook exists to
provide.

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

## Recosting workbooks

A recosting workbook (any output whose titles use "Recost" or "Recosting")
additionally MUST:

- Carry `Labor Benchmarking` rows only for roles that appear in its own
  Milestone Detail delta rows. Never list benchmark roles, or rates, that are
  tied to nothing in the package.
- Decompose every labor delta as hours x rate per affected labor category. A
  labor delta row carries Hours and Rate cells and computes its delta by
  formula; a single lump-sum labor delta is not acceptable, especially when the
  sheet's own management question asks whether hours and roles are
  proportionate.
- Include a delta row for every cost element the change register names (labor,
  materials, travel, ODCs, or others). When the register directs repricing of
  an element and the analysis concludes no change, carry an explicit $0 delta
  row with a one-line justification, never a silent omission.

## Formula and presentation rules

- Blue font for user-adjustable inputs; black font for formulas.
- Currency: `$#,##0.00;($#,##0.00)`.
- Percentage: `0.0%`.
- Multipliers: `0.0000`.
- Real Excel formulas for every derived value.
- Freeze panes below assumptions and header rows.
- Light header fills, filters, explicit widths, and readable source notes.
- Narrative columns (the Summary milestone Description column, Milestone Detail
  Basis cells, and source-note text) must have wrap text enabled on every
  populated cell and an explicit column width of at least 28 characters so no
  text clips mid-word in the rendered or printed view.
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
- Print setup is validated, not optional. Every canonical sheet must carry an
  explicit print area over the populated range (`ws.print_area`) and enable
  fit-to-page scaling (`ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)`
  in openpyxl; the property object must exist with `fitToPage` true). Any sheet
  wider than 8 used columns must set `ws.page_setup.orientation = "landscape"`.
  `validate_workbook.py` fails the workbook when any canonical sheet misses any
  of these.

### Column widths and text clipping

Excel and LibreOffice let a text cell overflow into the next cell **only when
that neighbour is empty**. The moment the cell to the right of a label carries a
value or a formula, the label is cut off at its own column boundary in the
printed and rendered output, however much white space appears to follow it on
screen. Setting a column width without accounting for this is what produces
labels such as `Government sh`, `0047900 Washington-Arlin`, and
`Scenario Analysis: Senior Software En` in a delivered workbook.

Every populated text cell must therefore satisfy at least one of the following,
and `validate_workbook.py` fails the workbook when none of them holds:

- **Fit.** The label fits inside its own column width.
- **Wrap.** The cell sets `wrap_text=True` and the row height is tall enough to
  show every wrapped line.
- **Free overflow.** Every cell on the label's overflow side in the same row is
  empty. That is the right-hand neighbour for left-aligned and general text, the
  left-hand neighbour for right-aligned text, and both neighbours for centred
  text.
- **Merge.** The label is merged across the columns it needs. The merged span,
  not the anchor column alone, is what has to fit.

Section headers and block titles are the common failure. A title such as
`Scenario Analysis: Senior Software Engineer` must be merged across the block it
introduces, placed on a row whose neighbouring cells are left empty, or shortened
until it fits. Never rely on visual overflow for a block title that sits beside a
populated cell.

Concrete generator guidance:

- Compute each column width from the **longest label actually written to that
  column**, not from the header text or a fixed guess. Walk the column after the
  data is written, take the widest populated string, and set
  `width = min(cap, needed + 2)`.
- Estimate a label in column-width units rather than characters. One unit is
  about one digit at Calibri 11. Lowercase letters run about 0.96 units,
  uppercase about 1.05, `i`/`l`/`j` and spaces and most punctuation about 0.45,
  `m` and `w` about 1.66, and bold text is about 14 percent wider overall.
- Prefer a merged header cell for every block title, and reserve narrow columns
  for short codes, dates, and numbers.
- Where a column must stay narrow, move the long text into a wrapped narrative
  column with an explicit width and an adequate row height. Cap runaway widths
  in the 60 to 90 unit range and wrap instead of widening past that.
- The audit allows roughly one column-width unit of slack, so a label that is
  genuinely borderline will not fail. Do not aim for the tolerance; aim for the
  fit.

The narrative wrap rule above and this clipping rule are one system. Narrative
columns wrap and carry a width floor; every other populated text cell is checked
for clipping. The clipping audit skips any cell the narrative audit has already
reported, so a missing wrap is reported once, not twice.
