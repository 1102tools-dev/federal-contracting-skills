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

## Overview

This skill produces Independent Government Cost Estimates for FFP contracts using a layered wrap rate buildup model. Instead of the single burden multiplier used in T&M/LH pricing, FFP separates direct labor, fringe benefits, overhead, G&A, and profit into distinct auditable cost pools. The BLS base wage anchors the estimate; each cost pool adds a layer; the result is a fully burdened FFP rate per labor category.

**Required MCP servers:**
1. **bls-oews** -- market wage data by occupation and geography. Key tools: `get_wage_data`, `igce_wage_benchmark`, `list_common_metros`, `list_common_soc_codes`.
2. **gsa-calc** -- awarded GSA MAS ceiling hourly rates. Key tools: `suggest_contains`, `exact_search`, `keyword_search`, `igce_benchmark`, `price_reasonableness_check`.
3. **gsa-perdiem** -- federal CONUS travel lodging and M&IE. Key tools: `lookup_city_perdiem`, `estimate_travel_cost`, `get_mie_breakdown`.

The MCPs handle API keys, URL construction, series ID assembly, MSA renumbering, JSON path parsing, and the 75% first/last day M&IE rule. Call the tools directly; do not hand-construct API requests.

**Regulatory basis:** FAR 15.402 (cost/pricing data). FAR 15.404-1(a) (cost analysis). FAR 15.404-1(b) (price analysis). FAR 15.404-4 (profit/fee analysis). FAR 16.202 (FFP contracts).

## Operating Principle (ai-boundaries)

This skill **assembles data** and **formats documents** from reasoning the contracting officer supplies. It does NOT originate evaluative conclusions. Specifically:

- The skill pulls BLS wages, CALC+ ceiling rates, and Per Diem rates, and formats them into a workbook.
- The skill does NOT determine whether a rate is "fair and reasonable" under FAR 15.404-1. That determination is the CO's.
- The skill does NOT assert premiums (TS/SCI, OCONUS, SCIF, specialty labor) that are outside BLS/CALC+/Per Diem data. If a premium is needed and the data does not support it, the skill names the gap and hands the decision back to the CO.
- The skill does NOT draft a price reasonableness memo, a responsibility determination, or any FAR-citing signature document unless the CO has already supplied the rationale and conclusion, in which case the skill formats the CO's text into the template.
- Narrative prose (chat summaries, Methodology sheet, Rate Validation status) avoids evaluative verbs: "defensible," "reasonable," "acceptable," "competitive," "outlier." Replace with neutral positioning: "at P77 of CALC+ pool (n=X)," "within BLS P90 fully-burdened equivalent," "above P50 by Y%, document stacked factors in Methodology."

Stacked factors refers to the component sources of a rate premium. Typical examples: metro wage differential, seniority tier premium, clearance requirement premium, lab/SCIF overhead, thin CALC+ corpus (directional only), MAS ceiling vs CR cost-plus-fee separation, BLS vintage aging. Name the specific factors that apply, not the word "stacked" alone.

If you find yourself writing a conclusion about whether a number is right or wrong, stop. Present the data and let the CO conclude.

## Pre-flight: MCP dependency check

**Runs before Workflow Selection. Required on every skill trigger.**

This skill needs three MCP servers: `bls-oews`, `gsa-calc`, `gsa-perdiem`. Do not proceed to any workflow until both checks below pass.

**Check 1: MCP presence.** Verify all three are available in the current session by looking for one known tool from each:

- `bls-oews` (check for `mcp__bls-oews__detect_latest_year`)
- `gsa-calc` (check for `mcp__gsa-calc__suggest_contains`)
- `gsa-perdiem` (check for `mcp__gsa-perdiem__get_mie_breakdown`)

If any are missing, respond with:

> This skill requires the `bls-oews`, `gsa-calc`, and `gsa-perdiem` MCP servers. Missing: [list]. Install and configure them in your MCP client before using this skill.

**Check 2: API key presence.** Two of the three need API keys. Verify by lightweight ping:

- `mcp__bls-oews__detect_latest_year` (needs a BLS API key)
- `mcp__gsa-perdiem__get_mie_breakdown` (needs an api.data.gov key)
- `gsa-calc` needs no key, skip

If either ping returns an auth error or missing-key error, respond with:

> [bls-oews | gsa-perdiem] is installed but its API key is not set. This MCP needs a free API key (BLS for `bls-oews`, api.data.gov for `gsa-perdiem`). Register the key with the provider and add it to the MCP's configuration, then restart your MCP client.

Only proceed to Workflow Selection after both checks pass. Do not try to work around missing MCPs by calling APIs directly; the skill relies on MCP-guaranteed behaviors (MSA renumbering lookups, JSON path normalization, first/last day M&IE math).

## Workflow Selection

### Workflow A: Full FFP IGCE Build (Default)
User needs a complete FFP cost estimate. Execute Steps 1 through 9 in order.
Triggers: "FFP IGCE," "firm fixed price estimate," "wrap rate buildup," "cost buildup."

### Workflow A+: SOW/PWS-Driven FFP Build
User provides a Statement of Work or requirement description instead of pre-structured labor inputs. Execute Step 0 (Requirements Decomposition) first, validate with user, then Steps 1-9.
Triggers: "build an FFP IGCE from this SOW," "price this PWS as FFP," or when the user provides a block of requirement text rather than a labor category table.

**Skip Step 0 if the user provides explicit staffing** (headcount per labor category) even if they reference an underlying PWS or SOW. Go straight to Workflow A.

### Workflow B: FFP Rate Positioning (Data Only, No Determination)

User has proposed rates and wants to see where they sit against market data. The skill returns the data and the CO decides reasonableness. **The skill does not produce a "fair and reasonable" determination, a signed memo, or advisory text telling the CO how to negotiate.**

Triggers: "is this FFP rate reasonable," "validate these wrap rates," "check this FFP proposal," "price reasonableness analysis."

**Step 0 / GATE (MANDATORY FIRST — runs before any other Workflow B step).**

**Workflow B entry = gate fires unconditionally.** If the user's prompt matches any Workflow B trigger ("is this FFP rate reasonable," "validate these wrap rates," "check this FFP proposal," "price reasonableness analysis," or any variant), the ENTIRE first response must be the refusal template below, emitted verbatim. No rate analysis. No CALC+ pull. No BLS pull. No "let me start with the analysis" preamble. No offer to continue with the memo if the user provides more info in the same response. Emit the template. Stop. Wait for the user's explicit Option A or Option B choice. This applies whether or not the prompt contains memo-drafting tokens; the gate is not token-gated.

Memo-drafting tokens (emit the template WITH the additional hard prohibition in bold: "I will not draft a determination section absent your verbatim rationale"): "memo", "determination", "fair and reasonable", "reasonable" (standalone), "price reasonableness", "reasonableness memo", "draft the memo", "for the file", "contract file", "document this", "memorandum", "validate," "acceptable," "justify."

**Refusal template (emit verbatim):**

> I can pull positioning data that shows where each proposed rate sits against CALC+ ceiling rates and BLS market wages. I cannot draft a price reasonableness memo, write a "fair and reasonable" determination, or recommend negotiation positions. Those are Contracting Officer decisions under FAR 15.404-1, not skill outputs.
>
> Tell me which you want:
>
> **Option A — Positioning data only.** I produce a table: per-LCAT proposed rate, CALC+ P25/P50/P75/P90 with sample size, BLS metro burdened equivalent. No verdict. No recommendation. You draw the conclusion.
>
> **Option B — Memo template fill.** You provide your rationale (what supports or doesn't support each rate) and your determination (fair and reasonable / not fair and reasonable / declining to determine). I drop your text verbatim into the memo template, add the benchmark tables underneath, mark it DRAFT. I will not originate determinations, recommend negotiation positions, or add hedging language.
>
> Which option?

**Proceed to Steps 1-5 only after:**
- User explicitly selects Option A, OR
- User provides Option B inputs (rationale text + determination text)

**Hard prohibitions at ALL times (Option A or Option B):**
- Do NOT write "the rate is fair and reasonable" or "not fair and reasonable" unless quoting the user's Option B text verbatim.
- Do NOT label rates "competitive," "aggressive," "outlier requiring justification," "premium warrants clarification," or any equivalent evaluative phrase. Use positional language only ("at P77," "above P50 by X%," "below P25").
- Do NOT recommend negotiation positions, evaluation notices, or counter-offer dollar figures.
- Do NOT write "Summary of findings" or "Determination" sections that draw conclusions the user has not supplied.

**Workflow B steps (run only after Step 0 gate clears):**

1. Collect the vendor's proposed labor categories, fully burdened hourly rates, and any scope context (metro, clearance, experience tier).

2. For each LCAT, call `mcp__gsa-calc__price_reasonableness_check(labor_category, proposed_rate, experience_min, education_level)`. The MCP returns count, min/max, median, IQR bounds, z-score, and percentile position. If sample size is below ~25 records, label the pool "directional only, not statistical validation."

3. For senior LCATs, also run the Step 4 dual-pool flow (title-match via `suggest_contains` + `exact_search`, plus experience-match via `igce_benchmark`) and present both medians side-by-side.

4. If metro context matters (DC, SF, NYC, Boston, etc.), pull BLS OEWS for that metro via `mcp__bls-oews__get_wage_data` and present the P50/P75/P90 fully-burdened equivalent using the vehicle wrap preset. This shows how the rate sits against local market labor independent of the CALC+ nationwide pool.

5. **Present a neutral positioning summary.** Example format:

> Proposed rate: $225/hr fully burdened, Senior Data Scientist, DC metro, Agency BPA cleared.
>
> CALC+ benchmark (Senior Data Scientist, 8+ yrs, n=7, thin-corpus directional only):
> - P25 $170, P50 $190, P75 $218, P90 $236
> - Proposed rate at P77, z-score 1.1, within 2σ outlier bounds ($139-$250)
>
> BLS OEWS DC metro (15-2051 Data Scientists, 2025 vintage aged to [contract start] at 2.5%):
> - P50 annual $135,190, P90 annual $208,600
> - Applied Agency BPA cleared wrap (3.17x) to P90 hourly: fully-burdened equivalent $234
>
> Premium factors this data does NOT capture: TS/SCI clearance premium, any SCIF-specific overhead, specialty cyber/data-science labor market tightness. If the CO intends to attribute part of the premium to clearance, the clearance premium range is the CO's to set based on agency policy or independent market research.

6. **Stop.** Do not write "the rate is fair and reasonable." Do not recommend negotiation positions. Do not suggest "push back only if..." text.

7. **Memo output (Option B path only).** If the user selected Option B at the Step 0 gate and supplied rationale + determination text, fill the memo template: benchmark tables from Steps 2-4, the user's rationale text verbatim in the findings section, the user's determination text verbatim in Section 7 (Determination). Do NOT paraphrase, do NOT add hedging, do NOT originate any conclusion text. Mark DRAFT. Use `[Contracting Officer Name]` and `[Agency]` placeholders. If Option A was selected, skip this step entirely.

## Information to Collect

Batch clarifying questions rather than ask iteratively. If key inputs are missing, ask all in one message before building. Provide defaults where noted. If any Required Input is ambiguous or missing for Workflow A (e.g., labor count without discipline, location without metro, fee type not specified), use `AskUserQuestion` to collect before pulling data. Do not guess.

### Required Inputs

| Input | Description | Example |
|-------|-------------|---------|
| Labor categories | Job titles or SOC codes | Software Developer, Project Manager |
| Performance location | City/state or metro area | Washington, DC |
| Staffing | Headcount per labor category | 2 developers, 1 PM |
| Hours per year | Productive hours per person (default: 1,880) | 1,880 |
| Period of performance | Base year + option years | Base + 2 OYs |
| Contract start date | Needed for wage aging | October 1, 2026 |

### Optional Inputs (Defaults Applied If Not Provided)

| Input | Default | Notes |
|-------|---------|-------|
| Fringe rate | 32% | FICA + health + retirement + PTO + workers' comp |
| Overhead rate | 80% | Applied to labor + fringe |
| G&A rate | 12% | Applied to subtotal |
| Profit rate | 10% | Applied to total cost; see FAR 15.404-4 |
| Escalation rate | 2.5%/yr | Applied to labor and travel |
| Travel destinations | None | City/state per destination |
| Travel frequency | None | Trips/year per destination |
| Travel duration | None | Nights per trip |
| Number of travelers | All staff | Travelers per trip |
| Travel months | Max monthly rate | Specific months if known |
| FY for per diem | Current federal FY | Compute at build time (Oct-Sep cycle) |
| Duty station / origin | Performance location | For City Pair airfare lookup |
| NAICS code | None | Include in output if provided |
| PSC code | None | Include in output if provided |
| Partial start | Full year (12 months) | Specify months if base year is partial |
| FFP pricing structure | By period | "By period" or "By deliverable/CLIN" |
| Shift coverage | Business hours (8x5) default | Specify 24x7 / 16x7 / 12x5 if applicable; Step 0.5 computes FTE |

### Wrap Rate Component Guidance

**This table is a sensitivity reference for scenario Low/High bounds, NOT a default pick for MID.** MID should come from the Vehicle Preset table below when a vehicle applies. The Low/High columns here are the outer envelope used to stress-test scenarios once MID is set.

| Component | Low | Mid | High | Notes |
|-----------|-----|-----|------|-------|
| Fringe | 25% | 32% | 40% | Higher for generous benefits, union shops |
| Overhead | 60% | 80% | 120% | Higher for SCIF/cleared, large firms |
| G&A | 8% | 12% | 18% | Higher for large corporate structures |
| Profit | 7% | 10% | 15% | FAR 15.404-4: risk, investment, complexity |

The generic Mid (32/80/12/10 → 2.93x) matches the **DoD non-cleared** vehicle preset. Do not apply it to GSA MAS commercial, Agency BPA, DoE M&O, or OCONUS builds without checking the Vehicle Preset table.

### Wrap Rate Presets by Contract Vehicle

**CRITICAL: ASK about contract vehicle before applying default wrap rates.** Workers have historically defaulted to skill mid (32/80/12/10, implied multiplier 2.93x) regardless of vehicle. That is correct for GSA MAS commercial or agency BPA non-cleared, but materially wrong for DoE M&O, cleared DoD, or OCONUS. Use this table to select MID scenario defaults keyed by the actual vehicle/environment the contract will use:

| Vehicle / environment | Fringe | Overhead | G&A | Profit | Implied mult | Expected band |
|----------------------|--------|----------|-----|--------|--------------|---------------|
| GSA MAS (commercial) | 30% | 60% | 10% | 8% | **2.47x** | 2.3-2.7x |
| GSA MAS (cleared services) | 32% | 80% | 12% | 8% | **2.87x** | 2.7-3.1x |
| Agency BPA / IDIQ (non-cleared) | 32% | 75% | 12% | 10% | **2.85x** | 2.7-3.1x |
| Agency BPA / IDIQ (cleared) | 32% | 95% | 12% | 10% | **3.17x** | 3.0-3.4x |
| DoD BPA (TS/SCI SCIF) | 32% | 115% | 13% | 10% | **3.39x** | 3.2-3.6x |
| DoD prime (non-cleared) | 32% | 80% | 12% | 10% | **2.93x** | 2.7-3.1x |
| DoD prime (Secret, non-SCIF) | 32% | 100% | 12% | 10% | **3.25x** | 3.0-3.4x |
| DoD prime (SCIF / deployed) | 32% | 120% | 14% | 10% | **3.64x** | 3.5-3.8x |
| DoE M&O / FFRDC | 35% | 95% | 12% | 8% | **3.18x** | 3.0-3.4x |
| R&D / BAA CR | 32% | 90% | 12% | 8% | **3.03x** | 2.9-3.3x |
| OCONUS / hostile theater | 35% | 120% | 14% | 12% | **3.79x** | 3.6-4.0x |

*Notes on vehicle selection:* GSA MAS commercial = SIN 520, 541611, ceiling-rate vehicle. Agency BPA/IDIQ cleared = TS/SCI in SCIF. DoE M&O/FFRDC = UT-Battelle, LANS, Sandia (higher fringe, lower profit). R&D/BAA CR carries lower profit; fee is separate on CR contracts.

**Math check:** Multipliers computed as `(1+fringe) × (1+OH) × (1+G&A) × (1+profit)`. Example GSA MAS commercial: 1.30 × 1.60 × 1.10 × 1.08 = 2.47x. Verify this arithmetic in your workbook; Methodology narrative must match the actual cell values, not a rounded guess.

**Sanity band is pinned to each preset row above.** Flag for user review only if the MID multiplier falls OUTSIDE the band shown in that row. A 3.17x Agency BPA cleared build lands in its 3.0-3.4x band (normal); a 3.17x GSA MAS commercial build is outside 2.3-2.7x (flag).

**Use the MID column as your scenario mid. Generate LOW as mid minus ~20% on each component, HIGH as mid plus ~20%.**

If the user doesn't specify a vehicle, ASK before defaulting. If the user provides explicit rates, use those (custom rate workflow below).

**Custom rate workflow:** When the CO provides explicit wrap rates (e.g., for cleared/SCIF environments), those rates ARE the mid-scenario estimate. Do NOT use skill defaults as mid and the CO's rates as a scenario variant. Instead:
- Use CO-provided rates as MID scenario
- Generate LOW as mid minus offset (e.g., 20% reduction on each component)
- Generate HIGH as mid plus offset (e.g., 20% increase on each component)
- Document the CO-provided rates as the authoritative basis

**CO-supplied DCAA-audited rates (override rule, stronger than Custom rate workflow).** When the contracting officer supplies DCAA-audited indirect rates from an approved Forward Pricing Rate Agreement (FPRA), a current disclosure statement review, or a bilateral rate agreement, USE THOSE RATES instead of the Vehicle Preset table AND do NOT generate fictional LOW/HIGH bookends around them. Audited rates are a single authoritative value (point estimate), not a midpoint. Apply the FPRA rates in a single column on Sheet 1 and Sheet 2; if a LOW/HIGH band is still required for scenario display, clearly label the band as "sensitivity display only; FPRA is authoritative" in Methodology rather than treating LOW and HIGH as plausible rate outcomes. Document the source: FPRA effective date, approving authority (e.g., DCAA Region), rate composition (fringe / OH / G&A / profit split). Audited rates are a stronger basis than generic vehicle-preset defaults; do not revert to defaults and do not reconcile the CO's number to the closest vehicle row even if it lands outside the table's expected bands. If the CO-supplied rate diverges materially from the vehicle preset for the stated environment, trust the CO-supplied rate and note the divergence in Methodology.

## Constants Reference

| Constant | Value | Source |
|----------|-------|--------|
| Standard work year | 2,080 hours | 40 hrs x 52 weeks; converts annual wages to hourly |
| Default productive hours | 1,880 hours/year | 2,080 minus holidays and avg leave |
| BLS wage cap (annual) | $239,200 | OEWS reporting ceiling; reconfirm each release |
| BLS wage cap (hourly) | $115.00 | OEWS reporting ceiling; reconfirm each release |
| BLS data vintage | May 2025 | Released April 2026; next release ~spring 2027 |
| GSA mileage rate | $0.70/mile | CY2025 GSA POV rate |
| First/last day M&IE | 75% of full day | FTR 301-11.101 |
| City Pair fare source | GSA City Pair Program | cpsearch.fas.gsa.gov; use YCA fare |

> **Verify the data vintage before pricing.** OEWS publishes annually in spring, and BLS
> withdraws the prior year when the new one lands. Call `detect_latest_year()` first and use
> what it returns as the vintage for the aging factor. If the vintage in the table above is
> older than that, the aging factor over-escalates every labor line. Do not age 2025 wages
> from a 2024 vintage.


## Orchestration Sequence

### Step 0: Requirements Decomposition (Workflow A+ Only)

Converts an unstructured SOW/PWS into the structured inputs needed for pricing.

**Process:**
1. **Sufficiency check.** Scan for six priceable elements: labor categories, staffing levels, performance location, period of performance, deliverables, and travel. Flag anything missing. Hard stop if performance location is absent. If 3+ elements are missing and the document is under 500 words, ask the user whether to proceed with flagged assumptions or get clarification first.

2. **Task decomposition.** Parse into discrete task areas. For each: one-sentence description, primary skill discipline, complexity (routine/moderate/complex), recurring vs. finite.

3. **Labor category mapping.** Map tasks to SOC codes using the heuristics in Step 1. When a task spans disciplines, map to multiple categories.

4. **Staffing estimation.** Estimate FTEs per category based on scope indicators (number of systems, shift coverage language, surge/on-call, site count). Present as ranges when scope is ambiguous.

5. **Present decomposition table** for user validation:
```
Task Area               | Labor Category      | SOC Code | Est. FTEs | Basis
Application Development | Software Developer  | 15-1252  | 2-3       | 3 apps, agile
Security Operations     | InfoSec Analyst     | 15-1212  | 1-2       | Continuous monitoring
Project Oversight       | Project Manager     | 13-1082  | 1         | Single contract
```

6. **User validation gate (CRITICAL) - two stages, not one.** Skip Stage A/B gate when user provides structured inputs: LCATs with discipline, location with metro, FTE counts, and PoP all specified. If any of those four are ambiguous or missing, run the gate. Do not conflate "confirm the decomposition" with "pick build parameters." Run them separately:

   **Stage A - Decomposition validation.** After presenting the decomposition table, ask the user to confirm or amend it. Use `AskUserQuestion` with options like "Decomposition looks right, proceed" / "Modify LCAT X" / "Add LCAT Y" / "Adjust FTE estimates." Response MUST END after this question. Wait for explicit confirmation before continuing.

   **Stage B - Build parameters.** Only after the decomposition is confirmed, ask the remaining parameter questions (vehicle preset, metro, contract start, NAICS/PSC, hour-allocation method for FFP-by-deliverable, shift coverage density if 24x7). Use a separate `AskUserQuestion` call. Response MUST END after this question.

   DO NOT self-approve either stage. DO NOT skip Stage A to go straight to parameters. Proceeding to Step 1+ before Stage B is also answered is a skill violation. The user must affirmatively validate BOTH the decomposition and the parameters before build work begins.

### Step 0.5: Shift Coverage Staffing (if PWS specifies 24x7, continuous, or on-call)

When the requirement specifies continuous coverage, convert to FTE using industry-standard backfill math:

```
24x7x365 single-seat coverage    = positions_per_shift x 4.2 FTE
24x7x365 double-seat coverage    = positions_per_shift x 8.4 FTE
8x5 single-seat coverage         = positions_per_shift x 1.2 FTE
```

Derivation: one shift covers 2,080 hrs/yr at ~95% availability. Four shifts cover 8,760 annual hours with 50% blended availability (leave, training, overlap, turnover). Industry convention. The 4.2 factor accounts for ~25% non-productive time: PTO (10%), federal holidays (4%), training (5%), sick leave/turnover buffer (6%). Do NOT staff 4.0 FTE for 24x7 - that undercovers leave. Do NOT staff 1.0 FTE - that only covers one shift.

Document shift-coverage FTE derivation in the Methodology sheet: "24x7x365 SOC coverage at single-seat: 4.2 FTE per covered position per industry standard accounting for leave and training backfill."

**Escalation overlay.** Add on-call or overtime reserve for surge-driven work beyond base coverage. Typical on-call premium: 10-15% of base labor hours for incident response positions.

**Travel for shift-coverage roles.** If the requirement includes travel, default to **1 representative per trip** (rotating shift lead or designated trip captain), NOT the full 4.2 FTE. Note the convention in Methodology: "Shift coverage uses a single traveler per trip; remaining shift members stay on site to maintain coverage." Ask the user only if they explicitly say "all staff travel" or the PWS requires multiple attendees.

**Tier 1 vs Tier 2 distinction.** When a PWS says "24x7 Tier 2" or "24x7 Tier 2 incident response" specifically, do NOT blindly apply 4.2 FTE as if it were full 24x7 SOC coverage. Tier 2 is often an on-call overlay on existing Tier 1 monitoring rather than a separate round-the-clock seat. Ask the user to clarify via `AskUserQuestion`:

- "Tier 2 as a standalone 24x7 coverage layer (4.2 FTE single-seat)"
- "Tier 2 as on-call overlay on existing Tier 1 (typically 2-3 FTE with on-call premium)"
- "Tier 1 + Tier 2 both contractor-provided (4.2 FTE Tier 1 + 2-3 FTE Tier 2)"

Document the choice in Methodology with the FTE derivation.

**TS/SCI compliance overhead (optional).** On cleared contracts (TS/SCI, SCIF-based, or DoE M&O), NIST SP 800-53 continuous monitoring, STIG remediation, and accreditation maintenance typically consume 5-10% of staff time. This is NOT captured in the BLS wage data. If the requirement references cleared operations, ask the user whether to:

- Absorb compliance overhead into base FTE counts (default, no action needed)
- Add a 5-10% overhead buffer as a separate labor line, with CO confirmation on the percentage

Document the choice. Do not apply the buffer silently.

### Step 1: Map Labor Categories to SOC Codes

Map user job titles to Standard Occupational Classification codes.

**Domain triage first.** Before mapping, confirm: is this an IT/software requirement, a non-IT engineering requirement, a scientific/research requirement, a medical requirement, or a professional services requirement? This single branch prevents the most common mis-mapping (using 15-1211 Computer Systems Analyst for non-IT systems engineers).

**IT and software (15-12xx):**

| Common Title | SOC Code | BLS Title |
|-------------|----------|-----------|
| IT / Program Manager (technology) | 11-3021 | Computer and Information Systems Managers |
| Management Analyst | 13-1111 | Management Analysts |
| Project Manager | 13-1082 | Project Management Specialists |
| Systems Engineer / Analyst (IT) | 15-1211 | Computer Systems Analysts |
| Cybersecurity / InfoSec Analyst | 15-1212 | Information Security Analysts |
| Network Architect | 15-1241 | Computer Network Architects |
| Database Administrator | 15-1242 | Database Administrators |
| Sysadmin | 15-1244 | Network and Computer Systems Administrators |
| Software Developer | 15-1252 | Software Developers |
| QA Tester | 15-1253 | Software QA Analysts and Testers |
| Help Desk / User Support | 15-1232 | Computer User Support Specialists |
| Data Scientist | 15-2051 | Data Scientists |

**Physical and non-IT engineering (17-2xxx):** Use these for reactors, aerospace, civil infrastructure, chemical, mechanical, and any "Systems Engineer" that integrates hardware rather than software.

| Common Title | SOC Code | BLS Title |
|-------------|----------|-----------|
| Aerospace Engineer | 17-2011 | Aerospace Engineers |
| Biomedical Engineer | 17-2031 | Biomedical Engineers |
| Chemical Engineer | 17-2041 | Chemical Engineers |
| Civil Engineer | 17-2051 | Civil Engineers |
| Electrical Engineer | 17-2071 | Electrical Engineers |
| Industrial Engineer | 17-2112 | Industrial Engineers |
| Mechanical Engineer | 17-2141 | Mechanical Engineers |
| Nuclear Engineer | 17-2161 | Nuclear Engineers |
| Petroleum Engineer | 17-2171 | Petroleum Engineers |
| Systems Engineer (non-IT) | 17-2199 | Engineers, All Other |

Use 17-2199 when the role doesn't cleanly fit one engineering discipline (RF, antenna, radar, systems integration specialties). Pull alongside a specific engineering SOC for comparison.

**Science, research, and medical:**

| Common Title | SOC Code | BLS Title |
|-------------|----------|-----------|
| Physicist | 19-2012 | Physicists |
| Chemist | 19-2031 | Chemists |
| Medical Scientist | 19-1042 | Medical Scientists, Except Epidemiologists |
| Registered Nurse | 29-1141 | Registered Nurses |
| Physician Assistant | 29-1071 | Physician Assistants |

**Program / Project Management — context-dependent:**

Program Manager SOC depends on the contract type:
- **Operations / administrative contracts:** 11-1021 (General and Operations Managers) — help desk, logistics, facilities, admin support
- **Engineering / technical contracts:** 11-9041 (Architectural and Engineering Managers) — reactor design, aerospace, infrastructure, R&D
- **IT / software contracts:** 11-3021 (Computer and Information Systems Managers) — software development, cybersecurity, enterprise IT

The engineering variant (11-9041) runs 20-40% higher than 11-1021 and is more defensible for technical programs. Document the choice in the Methodology sheet.

**Technical writing and support:**

| Common Title | SOC Code | BLS Title |
|-------------|----------|-----------|
| Technical Writer | 27-3042 | Technical Writers |
| Contracting Specialist | 13-1020 | Buyers and Purchasing Agents |

When mapping is ambiguous, query multiple SOC codes and present the range.

### Step 2: Pull BLS Wage Data

Call `mcp__bls-oews__get_wage_data(occ_code, scope, area_code, datatypes)` for each labor category. Pass a 6-char SOC, scope `metro|state|national`, and area_code (5-digit MSA for metro, 2-digit FIPS for state). Request datatypes `["04", "11", "12", "13", "14", "15"]` for mean + P10/P25/P50/P75/P90. Valid datatypes accepted by the MCP are `01, 03, 04, 08, 11, 12, 13, 14, 15` only; do NOT pass `02` or `05` (the MCP rejects them).

The MCP builds the 25-char series ID, handles footnote code 5 (cap) vs. code 8 (suppression), and exposes the current MSA list via `list_common_metros` with OMB Bulletin 23-01 renumbering notes. You do not need to hedge against Cleveland 17410 or Dayton 19430 yourself. If the target metro is not in `list_common_metros`, resolve the MSA code via https://www.bls.gov/oes/current/msa_def.htm and pass the 7-char code directly to `get_wage_data`. Do not fall back to state-level wages without first checking the MSA directory.

**Geography fallback (caller's job):** metro first; if the MCP returns "series does not exist" on every datatype, try state; fall back to national. Recommend the median as the default basis and present the full distribution.

**Known-fragile SOCs at metro level.** Some specialty SOCs suppress at metro level; fall through to state without treating it as a data quality signal.

**Shortcut:** for a single-LCAT single-location sanity check, `mcp__bls-oews__igce_wage_benchmark(occ_code, scope, area_code, burden_low, burden_high)` returns annual and hourly mean/median/P10/P90 with a burdened range in one call. Use for Workflow B rate checks; use `get_wage_data` when building the full workbook.

**Seniority modeling when BLS lacks granularity.** BLS does not break out junior / mid / senior variants within a single SOC. When a PWS specifies seniority tiers, use percentile positioning as a documented convention:

- Junior / entry: P25
- Mid / journeyman: P50
- Senior: P50 to P75 depending on scope and distribution shape
- Principal / director / SME: P75 to P90

**No tiers specified.** When the user gives an N-person team with no seniority breakdown (e.g., "3-person dev team"), default all N members to P50 (mid/journeyman) and note this in Methodology as "no seniority tiers specified, all members priced at mid-level P50 convention." Do NOT invent a 25/50/25 Jr/Mid/Sr split unless the user asks.

Document this in Methodology as a convention, not a BLS standard.

**Wage cap ($239,200 annual / $115.00 hourly).** When the MCP flags a value as capped, use the cap as a lower bound and flag in the narrative. If the chosen percentile lands within 10% of the cap (≥ $215,280 annual / ≥ $103.50 hourly), note in Methodology that the local market may exceed the stated value and flag for CO review.

**BLS flat-tail detection.** If P75 equals P90 in the BLS return AND neither hits the $239,200 cap, the local top-tail is sample-constrained (single dominant employer, thin high-end pool). Flag in Methodology: "Local P75/P90 collapsed; top-tail data sparse, local market may run higher than stated."

**Cap decision tree when P75 ALSO caps.** In single-employer-dominated metros (ORNL/Y-12 Knoxville Nuclear, certain LANL/INL physicists), P90 and sometimes P75 both cap. When P75 is capped:
1. Use BLS Mean (datatype 04) as the senior-tier anchor. Document as "P75 capped, Mean used as uncapped senior anchor."
2. Cross-reference commercial compensation surveys (Radford, Mercer, Payscale) for the specialty market.
3. Apply national P75/median ratio to the local median as a derived P75. Document as derivation, not BLS figure.
4. Never use $239,200 as the point estimate; it is a floor, not the value.

**Compressed distributions (P25 equals P10).** In the same single-employer metros, the lower half of the distribution can also compress: P25 and P10 return identical values because the dominant employer anchors even the lowest-paid workers at its own scale. When P25 = P10:
- The local P50 itself is likely pulled toward the dominant employer's mid-tier, not a genuine market median.
- Document in Methodology: "distribution compressed (P25=P10=$X); P50 reflects dominant-employer scale, not broader market."
- For Junior-tier pricing, do NOT use P25. Use national P25 × (local P50 / national P50) ratio to reconstruct a defensible junior anchor.

### Step 2B: Age BLS Wages to Contract Start Date

BLS OEWS data publishes about a year in arrears (May 2025 estimates released April 2026). If the contract Period of Performance starts after the data reference period, the base wages must be aged forward to avoid understating costs.

```
months_gap = months between BLS data vintage (May 2025) and contract PoP start date
aging_factor = (1 + escalation_rate) ^ (months_gap / 12)
aged_annual_wage = annual_median * aging_factor
```

**Compute months_gap at build time** from the contract start date the user provides. Do NOT copy the 29-month example from this skill. Contract start dates vary; aging factors must be current.

Example: if the contract start is 29 months after the BLS data vintage, at 2.5% escalation the aging_factor = 1.025^(29/12) = ~1.061. A $100,000 BLS median becomes $106,100 before wrap rate buildup.

Use the aged wage as the basis for all subsequent calculations. Document the aging adjustment in the Methodology sheet: "BLS OEWS wages (data vintage: [BLS_vintage]) aged forward [X] months to [contract start] at [escalation rate]%/yr to account for data lag."

**Contract start date default.** If the user does not specify, default to October 1 of the next federal fiscal year (computed at build time). Surface the assumption in the Summary sheet as a blue-font editable cell. If the user clarifies later, changing the cell recalculates the aging factor and the entire workbook. Do NOT invent a start date silently without noting it in the output.

**The aging factor must be a cell-referenced formula in the workbook, not hardcoded.** See Step 8 assumption block layout.

The escalation applied in Step 7 across option years starts AFTER this aging adjustment. Step 2B ages the base wage to the contract start; Step 7 escalates from that adjusted base across the period of performance. These are not double-counted.

### Step 3: FFP Wrap Rate Buildup

Build the fully burdened rate layer by layer for each labor category:

```
1. Direct Labor Rate    = aged_annual_wage / 2080
2. Fringe               = Direct Labor * fringe_rate
3. Labor + Fringe       = Direct Labor + Fringe
4. Overhead             = Labor_Fringe * overhead_rate
5. Subtotal             = Labor_Fringe + Overhead
6. G&A                  = Subtotal * ga_rate
7. Total Cost           = Subtotal + G&A
8. Profit               = Total_Cost * profit_rate
9. Fully Burdened Rate  = Total_Cost + Profit
```

**Implied wrap rate:** `implied_multiplier = fully_burdened_rate / direct_labor_rate`. For default rates: 1.0 x 1.32 x 1.80 x 1.12 x 1.10 = ~2.93x. FFP rates are typically higher than T&M because the contractor absorbs cost risk.

**Three-scenario approach:** Vary each component, not a single multiplier:

| Component | Low | Mid | High |
|-----------|-----|-----|------|
| Fringe | 25% | 32% | 40% |
| Overhead | 60% | 80% | 120% |
| G&A | 8% | 12% | 18% |
| Profit | 7% | 10% | 15% |

**Sanity band applies to MID only.** The mid-scenario implied multiplier should fall within 2.2x-3.5x for commercial-item CONUS services. The high-scenario multiplier naturally hits 4.18x from arithmetic (1.40 x 2.20 x 1.18 x 1.15) - that's expected, not an outlier, and does not trigger the "SCIF/niche" flag. Flag only the MID multiplier for review against the 2.2x-3.5x band.

For SCIF, cleared, or OCONUS environments, the mid multiplier routinely hits 3.0x-3.8x. That is not an outlier either - it's the actual market. When overhead is user-specified above 85% or the prompt references SCIF/cleared/OCONUS, document the elevated multiplier in methodology regardless of whether it falls inside or outside the nominal band.

### Step 4: Cross-Reference Against CALC+

Follow a discovery-first pattern. The MCP returns clean aggregation stats; your job is picking the right tool for the pool you want.

**Decision tree:**

1. **Discover buckets.** Call `mcp__gsa-calc__suggest_contains(field="labor_category", term=<LCAT term>)`. Returns up to 100 buckets with `doc_count` per bucket plus a `likely_truncated` flag. If truncated, narrow the term.
2. **If the top 2-3 buckets have combined records >=50:** call `mcp__gsa-calc__exact_search(field="labor_category", value=<exact bucket name>)` for each, then aggregate. This avoids the wildcard-match contamination that `keyword_search` produces (it also matches vendor_name and idv_piid).
3. **If buckets are fragmented** (every bucket under ~30 records, common for niche cleared cyber / specialty engineering): fall back to `mcp__gsa-calc__keyword_search(keyword=<term>)`. Document the contamination caveat in Methodology.
4. **Default for Workflow A rate validation:** use `mcp__gsa-calc__igce_benchmark`. Call `keyword_search` only when you need the example-rate or labor-category buckets. `mcp__gsa-calc__igce_benchmark(labor_category=<exact>, experience_min=N, education_level=X)` returns count, min/max/mean, std dev, and P10/P25/P50/P75/P90 in one call, without the 50KB+ labor_category/current_price aggregation buckets that blow up response size. `page_size=0` is no longer accepted by the MCP. Use `page_size=1` minimum when aggregation stats are needed; prefer `mcp__gsa-calc__igce_benchmark` for stats-only access (no corpus, trimmed return shape).

The MCP returns canonical stats at the top level of the response dict (count, min_rate, max_rate, avg_rate, p25, p50, p75). No JSON-path archaeology required.

Match the vendor's tier in the keyword, not the aggregate title. For 'Mid Software Developer' query `Software Developer II` not `Software Developer` — the aggregate pool mixes interns through Senior levels and can falsely flag rates as +70% divergent when the tier-matched pool is +11%.

**Rate validation positioning (data only, not a determination).** Present the vendor's / IGCE's FBR against CALC+ P25/P50/P75 as a positional statement. Do NOT assert "reasonable," "defensible," "outlier requiring justification," or "within expected band." Those are CO determinations. The skill describes WHERE the rate sits and documents the stacked factors that place it there.

**Narrative positioning language (use this, not evaluative verbs):**
- "Rate sits at CALC+ P77 (n=7, thin-corpus directional only)."
- "Above P50 by X%; stacked factors: [metro, seniority tier, aging, wrap vs commercial]."
- "Below P25; pool composition or LCAT alignment may warrant CO review."
- "Premium factors not captured by this data: [TS/SCI clearance premium, SCIF overhead, specialty market]. CO sets the relevant premium band if one applies."

**Stacked premium: show the math, do not conclude.** When divergence above CALC+ P50 looks large (40%+), decompose the divergence into source factors (metro ratio, seniority tier, aging, wrap vs commercial) and present the compounded ratio in Methodology. Do NOT write "this is defensible"; present decomposition and let the CO conclude. If actual FBR is significantly above the stacked-factor expectation, flag which factor is larger than data supports.

**Calibration guidelines for Sheet 4 Status column (positioning only, not determinations):**

- **0-15% above P50:** "Within CALC+ FFP premium range"
- **15-40% above P50:** "Above P50 by 15-40%; typical FFP risk premium range"
- **40-70% above P50:** "Above P50 by 40-70%; expected in high-cost metros vs nationwide CALC+. See Methodology for factor decomposition."
- **>70% above P50:** "Position outside ±70% band; document stacked factors in Methodology."
- **Below P25:** "Below P25; CO review recommended."

The Sheet 4 Status column labels position the rate; it does NOT say "reasonable" or "outlier." If the user asks the skill to assert reasonableness, refer them to the ai-boundaries principle at the top of this skill.

**Dual-pool analysis for senior LCATs.** For "Senior X" requirements, the MCP does not auto-dual-pool. Query both title-match (`suggest_contains` then `exact_search` on "Senior X") and experience-match (`igce_benchmark` with `experience_min=8`) and present both medians. They often differ by 10-15%; the CO picks which better matches the vendor's LCAT description.

**Known-fragmented LCAT terms.** Some common job titles return fragmented CALC+ buckets (no single bucket with enough records for clean stats). Use these canonical queries instead:
- "SOC analyst" / "cyber analyst" → query `Information Security Analyst I/II/III` (15-1212 pool has tiered buckets)
- "Software engineer" as a generic role → query `Software Developer I/II/III` tiers
- "Data engineer" → often returns <10 records; fall back to `igce_benchmark` on Data Scientist with experience filter

**Workflow B shortcut:** `mcp__gsa-calc__price_reasonableness_check(labor_category, proposed_rate, education_level, experience_min)` returns z-score and percentile position directly. Use for vendor rate validation without a full workbook.

### Step 5: Pull Per Diem Rates (If Travel Required)

Call `mcp__gsa-perdiem__estimate_travel_cost(city, state, num_nights, travel_month=None, fiscal_year=None)` per destination. The MCP returns `nightly_lodging`, `lodging_total`, `daily_mie`, `first_last_day_mie`, `mie_total`, `grand_total`, and `travel_days`. First/last day 75% M&IE and the day-trip (0 nights) edge case are handled internally per FTR 301-11.101. If `travel_month` is omitted, the MCP uses the max monthly lodging rate as a conservative ceiling.

**Annual travel math:** `annual_travel = grand_total * trips_per_year * travelers`.

**Installation → GSA locality crosswalk.** GSA keys per diem by civilian locality, not by military installation or research lab. Looking up "Fort Meade" or "Pentagon" directly returns empty. Translate the installation to its GSA locality BEFORE calling the MCP:

| DoD installation | GSA locality | Metro |
|---|---|---|
| Fort Meade, MD | Annapolis / Anne Arundel County, MD | Baltimore |
| Fort Belvoir, VA | Fairfax / Alexandria, VA | DC |
| Pentagon, VA | Arlington, VA (use DC rate) | DC |
| Joint Base Andrews, MD | District of Columbia | DC |
| NSA Bethesda / Walter Reed, MD | District of Columbia (composite) | DC |
| Fort Liberty (Bragg), NC | Fayetteville, NC | Fayetteville |
| Peterson SFB / Schriever SFB / Fort Carson, CO | Colorado Springs, CO | Colorado Springs |
| Wright-Patterson AFB, OH | Dayton, OH | Dayton |
| Eglin AFB, FL | Fort Walton Beach, FL | Pensacola-Crestview |
| JB San Antonio / Randolph / Lackland, TX | San Antonio, TX | San Antonio |
| Hanscom AFB, MA | Bedford / Boston, MA | Boston |
| Redstone Arsenal, AL | Huntsville, AL | Huntsville |
| Offutt AFB, NE | Omaha / Bellevue, NE | Omaha |
| Cape Canaveral / Patrick SFB, FL | Cocoa Beach / Cape Canaveral, FL | Palm Bay-Melbourne |
| JB Lewis-McChord, WA | Tacoma / Pierce County, WA | Seattle-Tacoma |
| Oak Ridge National Lab / Y-12, TN | Knoxville, TN | Knoxville |
| Los Alamos National Lab, NM | Santa Fe / Los Alamos County, NM | Santa Fe |
| Hanford / PNNL, WA | Richland, WA | Kennewick-Richland |
| Sandia National Labs, NM | Albuquerque, NM | Albuquerque |
| Lawrence Livermore National Lab, CA | Livermore / Oakland, CA | Oakland-Fremont |
| Idaho National Lab, ID | Idaho Falls, ID | Idaho Falls |
| White Sands Missile Range, NM | Las Cruces, NM | El Paso |
| NAWS China Lake, CA | Ridgecrest / Kern County, CA | Bakersfield |
| Edwards AFB, CA | Lancaster / Palmdale, CA | Los Angeles |
| Dugway Proving Ground, UT | Salt Lake City metro (std rate) | Salt Lake City |
| Nellis AFB / Creech AFB, NV | Las Vegas, NV | Las Vegas |
| Point Mugu / NBVC, CA | Oxnard / Ventura County, CA | Oxnard |

If the installation is not on this list, query `mcp__gsa-perdiem__lookup_city_perdiem` with the nearest civilian city and cross-check the result's `county` field.

**"Between sites" travel canonical interpretation.** When user says "quarterly travel between sites" or "monthly travel between sites" with multiple locations, default to: trips/year TOTAL **split evenly across destinations**, NOT trips/year each way. Example: "quarterly travel between Fort Meade and Colorado Springs" = 4 trips total (2 MD→CO, 2 CO→MD), not 8. Confirm via `AskUserQuestion` only if the user says "each way" explicitly, or if the split would exceed reasonable burn rate (more than one trip per month per destination).

**Same-metro TDY proximity check.** If `performance_location` MSA equals `travel_destination` MSA (same metro, <50 mi), overnight lodging per diem may not qualify under FTR 301-7.103. Flag in Methodology: "Same-MSA travel; if this is not overnight TDY, zero the lodging line and use mileage only."

**City Pair airfare (optional):** When origin and destination are known, look up YCA fares at cpsearch.fas.gsa.gov. Skip if origin is unknown, OCONUS, local travel, or user provides their own airfare.

**Fiscal-year fallback.** The MCP returns EITHER an empty rates array OR an explicit error string containing "No rates found for FY{year}" when the requested FY is not yet published. Trigger fallback on both cases:

```python
if response == [] or (isinstance(response, dict) and "No rates found for FY" in response.get("error", "")):
    # retry with fiscal_year = requested_year - 1
```

Note the fallback in Methodology: "FY{requested} per diem not yet published; FY{fallback} rates used as conservative baseline." Default FY policy: use contract-start FY when available; if that FY is not yet published, fall back to current FY.

If the contract PoP start is within 6 months of the next federal fiscal year, query both FYs; if the target FY is not yet published (FY{N+1} publishes mid-August {N}), use current FY as conservative baseline and note in methodology: 'refresh on FY{N+1} publication.'

**Absorbed vs discrete low-effort tasks.** The skill does not have a hard rule for when to break out quarterly tabletops, annual audits, monthly reports, or similar low-effort recurring tasks as separate labor lines vs absorbing them into base FTE counts. Convention:

- **Absorb** when the task is <5% of an existing LCAT's time and the LCAT already has the skill set to perform it (e.g., tabletop facilitation absorbed into a Senior IR LCAT's hours).
- **Break out as separate line** when the task requires a distinct skill set, has its own deliverable cadence the CO will track, or exceeds 5% of any single LCAT's time.

Document the choice in Methodology. If the user asks, offer both options via `AskUserQuestion`.

**When no travel, include the sheet with a single 'Travel Not Applicable' text block. Do not skip the sheet — Sheet 1 Travel row still needs a cell reference target.** See Step 8 workbook structure. Also include a Travel row on Sheet 1 Summary with `0` value and "Not Applicable" note (see Step 8 Sheet 1 layout for no-travel handling).

### Step 6: Handle Multi-Location Weighting

**When the user provides EXPLICIT headcount per location (e.g., "4 FTE Fort Meade, 3 FTE Colorado Springs"):** use Option C by default. The user has already answered the weighting question by structuring the input that way. Do NOT prompt for A/B/C; proceed.

**When staff allocation across sites is unspecified or ambiguous:** ask the user, with defaults:

- **Option A (fallback, conservative):** Use highest median across locations per category. Preserves information when allocation is truly unknown.
- **Option B (weighted):** `weighted_wage = (wage_A * pct_A) + (wage_B * pct_B)` if user provides split.
- **Option C (separate lines):** Dedicated staff per location get separate rows. Preferred when headcount is explicit.

Option C is the information-preserving choice when data is available. Option A discards real geographic wage differentials and should only be used when allocation is genuinely unknown.

### Step 7: Calculate Fixed Prices and Apply Escalation

**Two FFP pricing structures (ask user which applies):**

**Structure A: FFP by Period (default for services)**
```
period_labor = sum(fully_burdened_rate * productive_hours * headcount) per category
period_travel = travel costs from Step 5
period_fixed_price = period_labor + period_travel + ODCs
```

**Structure B: FFP by Deliverable/CLIN**

Three legitimate hour allocation approaches. Ask which applies when user provides scope weights:

- **Uniform allocation (default):** Apply scope percentage uniformly across all labor categories. `deliverable_hours = total_hours * scope_weight`.
- **Per-LCAT matrix:** Different allocation per labor category. Technical Writer may concentrate 75% of hours on D4 final report; Nuclear Engineer may spread evenly. User provides an N x M matrix (N labor categories by M deliverables).
- **Staffing-profile-driven:** Effort ramps (e.g., Technical Writer at 25% effort months 1-12, 75% effort months 13-18). Compute hours per deliverable from the overlap of staffing effort with deliverable date ranges.

**Validate scope percentages sum to 100%.** If they do not, flag and ask: normalize, reject, or use as-is with documentation. Default to flag-and-ask.

**Deliverable-timing escalation (by-deliverable only):**
- **Single-period PoP (e.g., 18-month feasibility study):** age wages once to contract start; hold flat across deliverables. No escalation between CLINs.
- **Multi-year milestone structures (e.g., 3-year OT with annual milestones):** age wages to contract start, then escalate each deliverable to its midpoint date. Rationale: midpoint tracks burn-weighted cost better than start or completion date.

**Partial-year proration:**
```
prorated_hours = productive_hours * (months_in_period / 12)
prorated_travel = annual_travel * (months_in_period / 12)
```

**Escalation across option years (Structure A):** `year_N_cost = base_year_cost * (1 + escalation_rate) ^ N`

**Scenario math:** Calculate three scenarios using low/mid/high wrap rate components:
```
low_burdened  = direct_rate * (1+fringe_low) * (1+oh_low) * (1+ga_low) * (1+profit_low)
mid_burdened  = direct_rate * (1+fringe_mid) * (1+oh_mid) * (1+ga_mid) * (1+profit_mid)
high_burdened = direct_rate * (1+fringe_high) * (1+oh_high) * (1+ga_high) * (1+profit_high)
```

Travel is identical across scenarios (per diem is a published rate, not affected by wrap rates).

### Step 8: Produce the FFP IGCE Workbook

Generate a multi-sheet .xlsx workbook using openpyxl. Use Excel formulas for all calculations. Run the recalc script (`python /mnt/skills/public/xlsx/scripts/recalc.py <file>`) before presenting.

**Workbook structure (7 sheets):**

**Sheet 1: IGCE Summary.** Labor categories as rows, periods as columns (Structure A) OR deliverables as columns (Structure B). Rate/Hr shows fully burdened FFP rate. Extra column for implied multiplier. Travel rows below labor. Placeholder rows for Airfare, Ground Transportation, ODCs with `0` value and "TBD" in an adjacent note column - NEVER put "TBD" text in cells that feed into SUM formulas (breaks the grand total with #VALUE!). Grand total with SUM formulas.

**When travel is not required:** still include a single Travel row on Sheet 1 with value `0` and "Not Applicable" in the adjacent note column (so the grand total formula stays stable and a reviewer sees travel was actively excluded, not forgotten). Sheet 5 gets the full "Travel Not Applicable" block per Step 8 Sheet 5 layout.

**Assumption cell layout (Sheet 1, rows 1-11):**
```
A1:  "IGCE Assumptions (FFP)"        (bold, merged A1:B1)
A2:  "Fringe Rate"                   B2: 0.32      (blue font, percentage)
A3:  "Overhead Rate"                 B3: 0.80      (blue font, percentage)
A4:  "G&A Rate"                      B4: 0.12      (blue font, percentage)
A5:  "Profit Rate"                   B5: 0.10      (blue font, percentage)
A6:  "Escalation Rate/Yr"            B6: 0.025     (blue font, percentage)
A7:  "Productive Hours/Year"         B7: 1880      (blue font)
A8:  "Base Year Months (or PoP Months)" B8: 12       (blue font; for single-period PoPs like an 18-month study, relabel "Period Months" and set to total PoP length, e.g. 18)
A9:  "BLS Vintage"                    B9: =DATE(2025,5,1)    (blue font, real date)
A10: "Contract Start"                 B10: =DATE(2026,10,1)   (blue font, real date, user-editable)
A11: "Months Gap"                     B11: =DATEDIF(B9,B10,"m")
A12: "Aging Factor"                   B12: =(1+B6)^(B11/12)   (formula)
A13: (blank row separator)
A14: header row for data table
```

All labor formulas reference these cells, including the aging factor. If the user changes escalation rate, contract start, or BLS vintage, the entire workbook recalculates correctly.

**Sheet 2: Cost Buildup.** One block per labor category. **Block spacing is 19 rows** (18 rows of content + 1 blank separator). First block starts at row 1; block N starts at row `1 + (N-1) * 19`. FBR is at `row(N) + 17` = `18 + (N-1) * 19`. Implied multiplier at `row(N) + 18` = `19 + (N-1) * 19`.

**All `$B$N` references below are literal Excel cell addresses with integer row numbers.** Copy them verbatim into workbook formulas. Each row number refers to a specific row in the Sheet 1 assumption block (see Step 8 Assumption cell layout).

**The block-1 formulas shown below are templates for `block N` at `base_row = 1 + (N-1) * 19`.** For block 2 (starts at row 20), replace `B2` with `B21`, `B5` with `B24`, `B12` with `B31`, etc. Add `(N-1) * 19` to every in-block row index. Cross-sheet references to `IGCE Summary!$B$N` do NOT get shifted; they always point to the Summary assumption block. Worked example for block 2:

- Row 21: `B=[annual median from BLS]` (was row 2 for block 1)
- Row 24: `B==B23*B22` (was `B==B5*B4` - wait that's wrong; re-derive cleanly)

Cleaner: think of it as `formula relative to base_row`. Block 1 base = 0; block 2 base = 19; block 3 base = 38. Every `B{n}` in the template becomes `B{n + base}`. Only in-block references shift; `IGCE Summary!$B$N` cross-sheet refs stay fixed.

Per-block layout (first block, rows 1-19):

```
Row 1:  "Cost Buildup: [Labor Category]"                     (bold header)
Row 2:  A="BLS Base Wage (Annual, raw)"  B=[annual median from BLS]
Row 3:  A="Aging Factor"                 B=='IGCE Summary'!$B$12  (formula ref)
Row 4:  A="Aged Annual Wage"             B==B2*B3                  (formula)
Row 5:  A="Direct Labor Rate (Hourly)"   B==B4/2080                (formula)
Row 6:  (blank separator)
Row 7:  A="Fringe Rate"                  B==IGCE Summary'!$B$2     (formula ref, blue font)
Row 8:  A="Fringe Amount"                B==B5*B7                  (formula)
Row 9:  A="Labor + Fringe"               B==B5+B8                  (formula)
Row 10: A="Overhead Rate"                B==IGCE Summary'!$B$3     (formula ref, blue font)
Row 11: A="Overhead Amount"              B==B9*B10                 (formula)
Row 12: A="Subtotal (Labor+Fringe+OH)"   B==B9+B11                 (formula)
Row 13: A="G&A Rate"                     B==IGCE Summary'!$B$4     (formula ref, blue font)
Row 14: A="G&A Amount"                   B==B12*B13                (formula)
Row 15: A="Total Cost"                   B==B12+B14                (formula)
Row 16: A="Profit Rate"                  B==IGCE Summary'!$B$5     (formula ref, blue font)
Row 17: A="Profit Amount"                B==B15*B16                (formula)
Row 18: A="Fully Burdened Rate"          B==B15+B17                (formula, bold)
Row 19: A="Implied Multiplier"           B==B18/B5                 (formula, 0.00"x")
```

Cross-sheet references from Sheet 1 point to the FBR row: `='Cost Buildup'!$B$X` where X = `18 + (labor_category_index - 1) * 19`.

The Aged Annual Wage gets its own row so the aging math is visible on the sheet; a reviewer can see BLS Base and Aged side by side. Sheet 2 blocks compute hourly rates. Sheet 1 Summary multiplies by productive hours × FTE × period duration for annual figures. Formula: `Sheet 1 annual = 'Cost Buildup'!FBR_cell * $B$7 * FTE * ($B$8/12)`.

**Cell format conventions:**
- **Blue font (RGB 0,0,255):** hardcoded inputs (BLS raw wage in row 2; assumption cells B2:B10 on Sheet 1)
- **Black font:** all formula cells and formula-referenced cells
- **Annotation text:** cells containing source notes (e.g., "Source: BLS OEWS May 2025") MUST NOT start with `=`, `+`, `-`, or `@`. Excel interprets those as formula triggers. Lead with a space or prefix with `Source:`.

**Sheet 3: Scenario Analysis.** Three columns (low/mid/high), each using its own fringe/overhead/G&A/profit rates. Display component rates at top of each column. Travel identical across scenarios. Summary row: "Range: $X (low) to $Y (high), Mid estimate: $Z." Note that scenarios do NOT respect Sheet 1's Base Year Months proration (B8) - scenarios always use full-year hours. Document this in Methodology to prevent a reviewer surprise.

**Sheet 4: Rate Validation.** BLS burdened rate (mid scenario) vs. CALC+ P25/P50/P75, min/max range, divergence percentage (formula), Status column. Use the calibrated flag thresholds from Step 4:

```
=IF(divergence_pct>0.70,"Position outside +70% band; document in Methodology",
  IF(divergence_pct<-0.25,"Below P25 - review under-pricing",
    IF(divergence_pct>0.40,"Metro geographic premium - document in methodology",
      IF(divergence_pct>0.15,"FFP risk premium - within expected 15-40% band",
        "Competitive"))))
```

**Sheet 5: Travel Detail.** Formula-driven per-destination block. For M destinations, block N starts at row `1 + (N-1) * 17` with a 16-row content layout and 1-row separator. In-block row indices shift by `(N-1) * 17` the same way Sheet 2 blocks shift by 19. Sheet 1 Summary travel rows sum across all destination blocks:

```
Annual travel (Sheet 1) = SUM across destinations of (block_N_row_14 * block_N_row_12 * block_N_row_13)
                        = SUM('Travel Detail'!$B$14, 'Travel Detail'!$B$31, 'Travel Detail'!$B$48, ...)
```

If no travel is required, Sheet 5 contains a single "Travel - Not Applicable" declaration and note:

```
Row 1: "Travel Detail: Not Applicable"
Row 3: "No travel required per PWS/SOW. Placeholder retained for contract file completeness."
Row 4: "If travel scope is added via modification, populate this sheet with destination, nights,"
Row 5: "trips/year, travelers, and the Summary travel rows will pull through automatically."
```

When travel IS required, use the full per-destination block:
```
Row 3:  A="Fiscal Year"           B=<current federal FY>          (blue font)
Row 4:  A="Nightly Lodging Rate"  B=[max monthly]                 (blue font)
Row 5:  A="M&IE Daily Rate"       B=[rate]                        (blue font)
Row 6:  A="First/Last Day M&IE"   B==B5*0.75                      (formula)
Row 7:  A="Nights per Trip"       B=[nights, 0 for day trip]       (blue font)
Row 8:  A="Travel Days"           B==IF(B7=0,1,B7+1)              (formula)
Row 9:  A="Lodging per Trip"      B==B4*B7                        (formula, 0 when nights=0)
Row 10: A="M&IE per Trip"         B==IF(B7=0,B6,B5*MAX(0,B8-2)+B6*2)  (formula)
Row 11: A="Trip Total"            B==B9+B10                       (formula)
Row 12: A="Trips per Year"        B=[trips]                       (blue font)
Row 13: A="Travelers"             B=[count]                       (blue font)
Row 14: A="Annual Travel Cost"    B==B11*B12*B13                  (formula, bold)
```

**Day-trip branch required.** Without the `IF(B7=0,...)` branches on rows 8 and 10, a day trip (Nights=0) produces 150% M&IE instead of the correct 75% single-partial-day per FTR 301-11.101. This is a silent wrong-answer bug at the workbook level; do not skip the IF branches even if all planned trips are overnight.

**M&IE double-discount trap.** The MCP `mcp__gsa-perdiem__get_mie_breakdown` returns `mie_first_last_day` already discounted to 75%. Use that value directly. Do NOT multiply by 0.75 again or you ship 25% low M&IE on day trips. Formula on MCP output: `mie_per_trip = mie_first_last_day` for 0-night trips.

**Sheet 6: Methodology.** FFP-specific narrative for the contract file. Target length: 8-12 sections, 2-4 sentences each, readable in 3 minutes. Longer than 14 sections usually means restating data that already lives in Sheet 1-4.

**Formula-reference rule (mandatory).** Any derived numeric figure in the Methodology prose (implied multiplier, aging factor, months gap, fully burdened rate, total hours) MUST be a cell reference, not a hardcoded string. Use `=TEXT(Sheet1!B12,"0.0000")` for the aging factor, `=TEXT('Cost Buildup'!$B$19,"0.00""x""")` for implied multiplier, etc. If you hardcode "1.0615" or "2.47x" as text and the user later changes B6 (escalation) or B10 (contract start) or any wrap rate cell, the Methodology goes silently stale while the workbook numbers update. This is a workbook-consistency trap; no exceptions.

Include:
- Wrap rate buildup with each cost pool explained
- FAR 15.404-1(a), 15.404-4, 16.202 citations
- Implied multiplier basis (note: 2.93x at defaults, within 2.2-3.5x sanity band for commercial-item CONUS)
- Note that FFP rates exceed T&M because contractor absorbs cost risk
- Data sources with dates
- Aging methodology (use `=TEXT(Sheet1!B12,"0.0000")` formula references so numeric values update when inputs change, not hardcoded strings)
- Escalation basis
- Travel methodology
- Seniority percentile convention (if applied) with disclosure
- SOC mapping decisions (e.g., "Systems Engineer mapped to 17-2199 Engineers All Other vs. 15-1211 because this is reactor engineering, not IT")
- Multi-location weighting choice (A/B/C) with rationale
- Shift-coverage FTE derivation (if 24x7)
- CALC+ query mode used (exact-match vs keyword) with contamination caveat if keyword mode
- Rate validation interpretation (FFP premium expected, not outlier)
- Exclusions (airfare TBD, ODCs TBD, subs not included, OCONUS not covered)
- NAICS/PSC if provided

**Sheet 7: Raw Data.** All MCP tool call parameters and responses. If the MCP does not surface the full 25-char BLS series ID in its response, record the series-ID equivalent: MSA code + SOC + datatypes queried + `year` parameter. A reviewer should be able to reproduce the BLS query from what is recorded. Also record: CALC+ keywords and exact-match buckets with record counts, per diem city/state/FY/month parameters, and City Pair fares if retrieved. Record summary tables (count, percentiles, series IDs, query parameters) — NOT raw JSON dumps. A reviewer should reproduce the query from the parameters, not wade through 50KB of aggregation buckets.

**Sheet 1 Summary column presentation:**

Drop the "Implied Multiplier" column from the Summary if all labor categories use the same wrap rates (all rows will show identical 2.93x, which looks like a copy-paste error to a reviewer). Retain the implied multiplier on Sheet 2 per-block and on Sheet 3 per-scenario. If retained on Summary, add a note: "Identical across rows because wrap rates are uniform; varies by scenario - see Scenario Analysis."

**Formatting standards:**
- Blue font (RGB 0,0,255) for all user-adjustable inputs and assumptions
- Black font for all formula cells
- Currency: $#,##0 with negatives in parentheses
- Percentage: 0.0%
- Bold headers with light gray fill
- Freeze panes below assumptions block on Sheet 1 (below row 13)
- Auto-size column widths
- Burden/multiplier display format: `0.00"x"`

When base year is partial, prorate: `=burdened_rate*$B$7*(B8/12)*headcount`. Travel prorates the same way. Full option years ignore B8.

Never output as .md or HTML unless explicitly requested.

### Step 8.5: Post-Build Sanity Check (Required)

Before presenting, run a dimensional sanity check on the grand total:

```
expected_total ≈ avg_FBR × total_productive_hours × total_FTE_count
```

Where `total_productive_hours` = Sheet 1 B7 × Sheet 1 B8 / 12 for partial-year periods (full year just uses B7). Multiply by number of periods (Base + OYs) for Structure A.

If the workbook grand total is more than **2x** different from the expected band, the most likely cause is the **row 4 vs row 5 DL reference trap**: Summary formulas referencing `Cost Buildup!$B$4` (Aged Annual Wage, ~$100K+) instead of `Cost Buildup!$B$5` (Hourly DL rate, ~$50) produce totals in the billions because hours × annual wage is dimensionally wrong. Fix the cross-sheet reference and re-recalc.

Also spot-check: open the file with `openpyxl.load_workbook(path, data_only=True)` and read the grand total cell. If it comes back as `None`, the recalc step didn't run.

**Environment-specific recalc handling:**
- **claude.ai web chat:** rerun `python /mnt/skills/public/xlsx/scripts/recalc.py <file>`.
- **Claude Code CLI (no LibreOffice):** the recalc script is unavailable. Instead, compute the expected grand total in Python against the raw inputs and wrap rates:

```python
expected = sum(
    fbr * hours * fte * scenario_months / 12
    for lcat in lcats
    for fbr, hours, fte in [(lcat.fbr_mid, productive_hours, lcat.fte)]
)
```

Verify the computed total lands within 1% of your Python-side expected total. If yes, dimensional correctness is confirmed; Excel/Numbers will recalculate cell formulas on open. If no, the row 4 vs row 5 DL reference trap or block-indexing shift is likely the cause.

- **macOS Claude Desktop with Numbers installed:** Numbers auto-recalculates on file open; no script needed. Numbers may show a brief "updating formulas" indicator.

### Step 9: Present the File

**Required final step. Do NOT skip.**

**Environment-specific delivery:**
- **claude.ai web chat:** copy to `/mnt/user-data/outputs/<name>.xlsx` and call `present_files([...])`.
- **Claude Code CLI:** write to `$PWD` or user-supplied path. Print the absolute path. On macOS also run `open <path>`; on Linux `xdg-open <path>`; on Windows `start "" <path>`. Do NOT try `/mnt/user-data/outputs/` — does not exist outside claude.ai.
- **macOS Claude Desktop with Numbers:** write path, run `open <path>`. Numbers auto-recalculates on open.
- **macOS Claude Code CLI with Excel or Numbers installed:** write to `$PWD`, then run `open <path>`. The system default handler triggers recalc on open; no Python-side expected-total check is needed.

Do NOT skip delivery. A workbook in the sandbox that isn't surfaced looks like a silent failure.

**Recalc script availability is also environment-specific.** The `python /mnt/skills/public/xlsx/scripts/recalc.py <file>` script exists on claude.ai; on Claude Code CLI, either skip recalc (Excel recalculates on open) or use `openpyxl`'s formula parser and write the computed values back if recalc-on-save matters for the consumer.

## Edge Cases

**Implied multiplier sanity check:** If the MID-scenario implied multiplier falls outside 2.2x-3.5x, flag for user review. Below 2.2x suggests unrealistically low overhead. Above 3.5x suggests SCIF/OCONUS/niche conditions requiring documentation. The high-scenario naturally exceeds 3.5x; do NOT flag it.

**Silent-wrong-answer traps (workbook-level):**
- **Text starting with `=`, `+`, `-`, or `@` in ANY cell** is parsed as a formula by Excel. This applies to Methodology prose, labels, and source citations, not just Sheet 2 annotations. Prefix with a space or lead with a non-operator character.
- **Cross-sheet row index off-by-one on the DL hourly reference.** Row 4 of each Cost Buildup block is Aged Annual Wage; row 5 is Direct Labor Rate (Hourly). Scenario formulas and rate validation formulas that reference the DL hourly rate must use `5 + (i-1)*19`, NOT `4 + (i-1)*19`. Indexing off row 4 produces workbook totals in the billions because annual wage × hours is dimensionally wrong.
- **Day-trip M&IE.** Sheet 5 per-destination block needs the `IF(B7=0,...)` branches on rows 8 and 10. Without them, a 0-night day trip produces 150% M&IE instead of the correct 75% single partial day per FTR 301-11.101.

## What This Skill Does NOT Cover

Include as placeholder rows or methodology notes:
- **Airfare:** Use City Pair YCA fares when origin/destination known; otherwise TBD
- **Ground transportation:** Rental cars, mileage ($0.70/mile), taxi, rideshare
- **ODCs:** Equipment, licenses, materials, subscriptions (user must provide)
- **Subcontractor costs:** Requires separate estimate or vendor input
- **Fee/profit negotiation:** This skill estimates costs, not negotiation targets
- **OCONUS travel:** Per diem covers CONUS only; State Dept rates apply for OCONUS
- **T&M/LH contracts:** Use IGCE Builder LH/T&M
- **Cost-reimbursement:** Use IGCE Builder CR
- **Grant budgets:** Use Grant Budget Builder
- **Clearance processing / DCSA fees:** Require agency-specific input
- **Tempest, SCIF build-out, COMSEC equipment:** Require specialized quotes

## Quick Start Examples

**Basic FFP:** "Build an FFP IGCE for a 3-person dev team in DC, base plus 2 OYs" → map SOC codes, pull DC BLS wages, build layered wrap rates at low/mid/high, validate against CALC+, apply 2.5% escalation, produce 7-sheet xlsx.

**SOW-driven:** "Here's my PWS, I need an FFP cost estimate" → run Step 0 decomposition, PAUSE at validation gate, then full Workflow A with FFP buildup.

**Rate validation:** "Vendor proposes $185/hr for a Software Dev, FFP contract. Reasonable?" → Workflow B. Dual-pool CALC+ analysis, position within both pools, produce validation summary (no determination).

**FFP by deliverable:** "18-month feasibility study, 4 milestones at 15/30/25/30 scope weight, Oak Ridge TN" → ask allocation method, age wages once to contract start, produce by-deliverable workbook with Summary columns = CLINs.

---

*MIT © James Jenrette / 1102tools. Source: github.com/1102tools/federal-contracting-skills*
