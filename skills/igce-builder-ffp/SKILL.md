---
name: igce-builder-ffp
description: >
  Build IGCEs for Firm-Fixed-Price (FFP) federal contracts using structured
  wrap rate buildup (fringe, overhead, G&A, profit). Orchestrates BLS OEWS,
  GSA CALC+, and GSA Per Diem skills. Supports FFP-by-period and
  FFP-by-deliverable pricing structures, SOW/PWS decomposition into labor
  categories, and rate validation against CALC+ market data. Trigger for:
  FFP IGCE, firm fixed price estimate, firm fixed price cost estimate,
  wrap rate, wrap rate buildup, cost buildup, FFP cost model, build an
  FFP IGCE, price this FFP contract, fixed price estimate, FFP from this
  SOW. Also trigger for wrap rate analysis, implied multiplier, FFP
  scenario analysis, or FFP rate comparison. Do NOT use for Labor Hour,
  T&M, or cost-reimbursement IGCEs (use IGCE Builder LH/T&M or IGCE
  Builder CR). Do NOT use for grant budgets (use Grant Budget Builder).
  Requires the bls-oews, gsa-calc, and gsa-perdiem MCP servers.
---

# IGCE Builder: Firm-Fixed-Price (FFP)

## Purpose and operating boundary

Build an auditable FFP Independent Government Cost Estimate from BLS wages, layered indirect rates, CALC+ positioning data, travel inputs, and the Contracting Officer's assumptions. Keep the BLS wage, aging adjustment, fringe, overhead, G&A, profit, and fixed-price calculations visible and formula driven.

Assemble data and format workbooks. Do not originate professional judgments reserved to the Contracting Officer:

- Do not determine that a price or rate is fair and reasonable.
- Do not invent premiums for clearance, SCIF, OCONUS, specialty labor, or other conditions that the available data does not quantify.
- Do not draft a determination, negotiation position, responsibility finding, or signature-ready FAR memorandum unless the user supplies the rationale and conclusion. If supplied, reproduce that text verbatim and mark the output DRAFT.
- Use neutral positioning language such as "at CALC+ P77" or "above P50 by 22%." Avoid "reasonable," "defensible," "acceptable," "competitive," and similar conclusions.
- Workflow B produces positioning data only unless the user chooses the controlled memo-fill path and supplies the required determination text.

If a sentence concludes whether a number is right or wrong, stop and replace it with sourced data, arithmetic, and the decision left to the Contracting Officer.

## Reference map

Read only the references needed for the active workflow:

- Read [wrap-rate-presets.md](references/wrap-rate-presets.md) before selecting or testing indirect-rate assumptions.
- Read [data-source-operations.md](references/data-source-operations.md) before mapping SOCs or calling BLS, CALC+, or Per Diem operations.
- Read [workbook-specification.md](references/workbook-specification.md) in full before generating the workbook.
- Read [validation-gates.md](references/validation-gates.md) before building and again before delivering the workbook.
- Read [runtime-adaptation.md](references/runtime-adaptation.md) when collecting structured answers, locating tools, selecting a calculation engine, or delivering files.

## Non-negotiable gates

These gates prevent documented silent wrong answers. Keep them active even when shortening or adapting the workflow.

1. **CALC+ query signature:** Use the CALC+ `/v3/api/ceilingrates/` endpoint with the `keyword=` parameter when a keyword query is required. Never use `q=`. The wrong parameter can silently return the full corpus. Preserve the discovery path `aggregations.labor_category.buckets` with each bucket's `key` and `doc_count` in the data-source reference.
2. **Cross-sheet hourly-rate index:** In each 19-row Cost Buildup block, row 4 is Aged Annual Wage and row 5 is Direct Labor Rate (Hourly). Summary, scenario, and validation formulas that need hourly direct labor must reference `5 + (i-1)*19`, never `4 + (i-1)*19`. The wrong row produced a documented $16.9 billion result.
3. **Month-gap formula:** Store BLS vintage and contract start as `YYYY-MM` text and compute months with `VALUE(LEFT(...))` and `VALUE(MID(...))`. Do not use `YEAR()` on text and do not substitute `DATEDIF` for this tested pattern.
4. **Step 8.5 validation:** Run the formula-structure audit, independent Python recomputation, and real spreadsheet-engine verification when available. Never call an openpyxl-only check recalculation or proof of formula execution.
5. **AI boundary:** Never originate a fair-and-reasonable determination. Workflow B is data only unless the user supplies verbatim Option B rationale and determination text.
6. **BLS vintage:** Treat May 2025 only as the current documented baseline. Call `detect_latest_year` at runtime and use its result. Never age wages from a stale hardcoded vintage.
7. **Rate-positioning bands:** Report 0-15% above CALC+ P50 as the expected range, 15-40% as the FFP premium band, and anything above 40% with explicit stacked-factor arithmetic. These are positioning bands, not determinations.
8. **Staged questions:** For SOW/PWS decomposition, complete Stage A decomposition confirmation before Stage B build parameters. End each response at its question and wait. Never self-approve either stage.
9. **Aging factor:** Put the aging assumptions in named or clearly labeled assumption cells. Reference those cells from formulas. Never hardcode an aging multiplier into labor formulas or methodology prose.

## Pre-flight: capabilities and dependencies

Run this before workflow selection on every trigger.

1. Inspect the operations available in the current session. Match by advertised MCP server and operation name or by equivalent operation schema. Do not depend on a host-generated namespace or separator.
2. Confirm these operation groups are present:
   - `bls-oews`: `detect_latest_year`, `get_wage_data`, and the SOC/metro lookup operations.
   - `gsa-calc`: `suggest_contains`, `exact_search`, `keyword_search`, `igce_benchmark`, and `price_reasonableness_check`.
   - `gsa-perdiem`: `estimate_travel_cost`, `lookup_city_perdiem`, and `get_mie_breakdown`.
3. Make lightweight calls to `detect_latest_year` and `get_mie_breakdown` to distinguish installed-but-unauthenticated servers from working servers. Do not expose keys or credentials.
4. If an operation is unavailable, look for a semantically equivalent operation exposed by the same server. Do not replace the MCP with a hand-built public API call.
5. If a required capability remains missing, stop and list the missing server or operation. State whether it appears uninstalled, unauthenticated, or unavailable in the current host.

Use this message when installation is missing:

> This skill requires the `bls-oews`, `gsa-calc`, and `gsa-perdiem` MCP servers. Missing: [list]. Install and configure them in this client, restart or refresh the client, and try again.

Use this message when authentication is missing:

> [server] is available, but its required API key is not configured or was rejected. Configure the provider key in the MCP server, restart or refresh the client, and try again.

## Select a workflow

### Workflow A: Full FFP IGCE build

Use when the user supplies structured labor and contract inputs. Execute Steps 1 through 9.

### Workflow A+: SOW/PWS-driven FFP build

Use when the user supplies a SOW, PWS, or unstructured requirement. Execute Step 0, obtain both staged confirmations when required, then execute Steps 1 through 9. Skip decomposition when the user already provided labor category, discipline, location, FTE, and period details.

### Workflow B: FFP rate positioning

Use when the user asks whether proposed FFP rates are reasonable, asks to validate a proposal, or requests price-reasonableness analysis.

On the first Workflow B response, do not call tools or begin analysis. Emit this boundary and stop:

> I can pull positioning data that shows where each proposed rate sits against CALC+ ceiling rates and BLS market wages. I cannot draft a price reasonableness memo, write a "fair and reasonable" determination, or recommend negotiation positions. Those are Contracting Officer decisions under FAR 15.404-1, not skill outputs.
>
> Tell me which you want:
>
> **Option A: Positioning data only.** I produce a table with each proposed rate, CALC+ P25/P50/P75/P90 and sample size, plus a BLS metro burdened equivalent. I provide no verdict or recommendation.
>
> **Option B: Memo template fill.** You provide your rationale and determination. I reproduce your text verbatim in a DRAFT memo and place the benchmark tables underneath it. I do not originate conclusions or negotiation positions.
>
> Which option?

Proceed only after the user selects Option A or supplies both Option B rationale and determination text. For Option A, return neutral benchmark tables and stop. For Option B, reproduce user-supplied rationale and determination verbatim, mark the memo DRAFT, and use placeholders for the Contracting Officer and agency.

## Collect inputs

Collect missing information in the fewest useful stages. Use the host's structured question tool when it is available. Otherwise present numbered choices in chat and accept a number, label, or free-text answer.

Required for a build:

- Labor categories or priceable task areas
- Performance location or metro
- FTE or other staffing basis
- Productive hours per person, default 1,880
- Period of performance and pricing structure
- Contract start month
- Contract vehicle or indirect-rate basis

Optional with disclosed defaults:

- Fringe, overhead, G&A, profit, and escalation rates
- Travel destinations, frequency, nights, travelers, months, and origin
- NAICS and PSC
- Partial-period months
- Shift-coverage requirement
- Deliverable weights or per-LCAT allocation matrix

Do not guess a required discipline, location, staffing basis, vehicle, or pricing structure.

## Orchestration

### Step 0: Decompose requirements for Workflow A+

1. Check for labor disciplines, staffing indicators, location, period, deliverables, and travel. Hard stop when performance location is absent. If three or more elements are missing from a short requirement, ask whether to continue with labeled assumptions or obtain clarification.
2. Separate the requirement into task areas. Record discipline, complexity, cadence, deliverable, and staffing basis.
3. Map each task to candidate labor categories and SOCs using [data-source-operations.md](references/data-source-operations.md). Use multiple categories when a task spans disciplines.
4. Estimate FTE ranges only when the scope supports them. Identify the basis for every estimate.
5. Present the decomposition table.
6. **Stage A:** Ask the user to confirm or amend decomposition. End the response at the question and wait.
7. **Stage B:** After Stage A is confirmed, ask for vehicle, metro, contract start, NAICS/PSC, pricing structure, deliverable allocation, and any shift-density decision. End the response at the question and wait.

Skip both stages only when the user already supplied labor categories with discipline, metro, FTE, period, and the remaining build parameters.

### Step 0.5: Convert shift coverage to staffing

Use these tested conventions unless the user supplies another documented staffing basis:

```text
24x7x365 single-seat coverage = 4.2 FTE
24x7x365 double-seat coverage = 8.4 FTE
8x5 single-seat coverage      = 1.2 FTE
```

Do not price one FTE as continuous coverage. Distinguish standalone Tier 2 coverage from a Tier 2 on-call overlay. Ask which applies. For shift teams with travel, default to one representative per trip unless the requirement says otherwise. Do not silently add clearance or compliance buffers.

### Step 1: Map labor categories to SOCs

Classify the requirement as IT/software, physical engineering, science/research, medical, operations, or professional services before selecting codes. A Program Manager is context dependent: use 11-3021 for IT, 11-9041 for engineering, and 11-1021 for operations unless better evidence supports another code. Load the complete mapping and specialty fallback rules from [data-source-operations.md](references/data-source-operations.md).

Document every ambiguous mapping and any alternative queried.

### Step 2: Pull and age BLS wage data

1. Call `detect_latest_year` and record the returned vintage.
2. Query mean and P10/P25/P50/P75/P90 using `get_wage_data` for every SOC and location.
3. Follow metro to state to national fallback only after confirming that the metro series is unavailable, not merely renumbered.
4. Apply the documented seniority convention when BLS lacks job-level tiers. Do not invent a team mix when no tiers are supplied.
5. Age the selected wage to contract start using assumption cells and the month-gap formula in the workbook specification.

Use May 2025 only as the current baseline for comparison. The runtime result controls the workbook.

### Step 3: Build FFP wrap rates

Calculate each cost pool separately:

```text
direct labor rate = aged annual wage / 2,080
fringe amount     = direct labor rate * fringe rate
labor + fringe    = direct labor rate + fringe amount
overhead amount   = labor + fringe * overhead rate
subtotal          = labor + fringe + overhead amount
G&A amount        = subtotal * G&A rate
total cost        = subtotal + G&A amount
profit            = total cost * profit rate
fully burdened    = total cost + profit
```

Use the vehicle preset selected from [wrap-rate-presets.md](references/wrap-rate-presets.md). User-supplied rates override presets. DCAA-audited or otherwise approved rates are authoritative point estimates and do not receive invented low/high bookends. Create sensitivity scenarios only when the basis permits them.

### Step 4: Position rates against CALC+

Use the operation flow in [data-source-operations.md](references/data-source-operations.md). Preserve these rules in every run:

- Discover labor-category buckets first.
- Use exact buckets when the matched pool is adequate.
- Use `keyword_search(keyword=<term>)` only when exact buckets are fragmented. The underlying CALC+ signature is `/v3/api/ceilingrates/` with `keyword=`. Never use `q=`.
- Use `igce_benchmark` for compact percentile statistics.
- For senior categories, present title-match and experience-match pools separately.
- Label small pools as directional.
- Report the 0-15%, 15-40%, and above-40% positioning bands without converting them into a determination.

### Step 5: Price travel when required

Use `estimate_travel_cost` and the locality, fiscal-year fallback, 0-night trip, and installation-crosswalk rules in [data-source-operations.md](references/data-source-operations.md). Do not discount first/last-day M&IE twice. When no travel is required, retain explicit zero and Not Applicable rows so the workbook shows that travel was considered.

### Step 6: Handle multiple locations

Use separate labor lines when the user supplies headcount by location. Use a weighted wage when the user supplies percentages. Use the highest applicable median only as a disclosed fallback when allocation is unknown. Do not ask the user to choose a method already implied by explicit headcount.

### Step 7: Calculate fixed prices

For FFP by period, calculate labor, travel, and ODCs for each base or option period and apply escalation after the wage-aging adjustment.

For FFP by deliverable, select one disclosed allocation method:

- Uniform allocation by scope weight
- Per-LCAT allocation matrix
- Staffing-profile allocation by date range

Require deliverable percentages to total 100%, or ask whether to normalize, reject, or retain with documentation. For a single-period engagement, age wages once to contract start and do not escalate between deliverables. For multi-year milestones, escalate to each deliverable midpoint.

### Step 8: Build the workbook

Read [workbook-specification.md](references/workbook-specification.md) in full before writing code. Build the seven required sheets with formulas, source notes, assumption cells, and editable inputs. Preserve these structural rules:

- Use `YYYY-MM` text for BLS Vintage and Contract Start.
- Compute Months Gap with the tested `VALUE(LEFT(...))` and `VALUE(MID(...))` formula.
- Reference the Aging Factor cell from every labor calculation.
- Use 19-row Cost Buildup blocks. Direct Labor Rate is row 5 of each block, Fully Burdened Rate is row 18, and Implied Multiplier is row 19.
- Never reference row 4 as an hourly rate.
- Keep derived Methodology numbers formula-linked to workbook cells.
- Keep numeric calculation cells numeric. Put TBD or explanatory text only in adjacent note cells.
- Guard 0-night travel with the required day-trip formulas.

Create a temporary validation-input JSON file using the schema in [validation-gates.md](references/validation-gates.md). It must contain the raw inputs used to build the workbook and the cells where calculated results should appear. Do not deliver the temporary file unless the user requests it.

### Step 8.5: Validate before delivery

Run all available layers described in [validation-gates.md](references/validation-gates.md):

1. Run `scripts/recompute_expected_values.py` against the validation-input JSON.
2. Run `scripts/validate_workbook.py` against the workbook and the same JSON.
3. If LibreOffice or another real spreadsheet engine is available, let the validator recalculate a temporary copy and compare cached results with the independent Python results.
4. If no calculation engine is available, report exactly:

> Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.

Do not claim full workbook validation when the third layer did not run. Fix every structural or numerical mismatch before delivery. The grand total must also pass the dimensional sanity check against fully burdened rates, productive hours, FTE, periods, travel, and ODCs.

### Step 9: Deliver the workbook

Use the host's file-output or attachment capability when available. Otherwise write to the user-supplied path or current working directory and return the absolute path. Do not assume a host sandbox path, a particular file-presentation function, or an OS-specific open command. Follow [runtime-adaptation.md](references/runtime-adaptation.md).

State which validation layers passed and whether a real spreadsheet engine ran. Do not bury the limitation when only static and independent checks ran.

## Edge conditions

- Mid-scenario multipliers must be checked against the selected vehicle's expected band, not a universal band. High sensitivity cases may legitimately exceed 3.5x.
- Treat text beginning with `=`, `+`, `-`, or `@` as a formula-injection risk. Prefix or rewrite explanatory text.
- Keep same-metro travel, OCONUS travel, airfare, ground transportation, equipment, subscriptions, subcontractors, clearance processing, SCIF construction, TEMPEST, and COMSEC as separately sourced inputs or explicit exclusions.
- Use the LH/T&M or Cost-Reimbursement skill for those contract types. Do not reuse this FFP wrap workflow.

---

*MIT copyright James Jenrette / 1102tools. Source: github.com/1102tools/federal-contracting-skills*
