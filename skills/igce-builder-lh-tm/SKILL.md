---
name: igce-builder-lh-tm
description: >
  Build IGCEs for Labor Hour (LH) and Time-and-Materials (T&M) federal
  contracts using burden multiplier pricing. Orchestrates BLS OEWS, GSA
  CALC+, and GSA Per Diem. T&M adds materials at cost (FAR 16.601(b)).
  Supports SOW/PWS decomposition and CALC+ rate validation. Trigger for:
  LH IGCE, T&M IGCE, labor hour estimate, time and materials estimate,
  burden multiplier, burdened rate, IGCE with travel or materials,
  CALC+ rate comparison. Do NOT use for FFP (use IGCE Builder FFP),
  cost-reimbursement CPFF/CPAF/CPIF (use IGCE Builder CR), or grant
  budgets (use Grant Budget Builder). Requires the bls-oews, gsa-calc,
  and gsa-perdiem MCP servers.
---

# IGCE Builder: Labor Hour & Time-and-Materials (LH/T&M)

## Overview

This skill produces Independent Government Cost Estimates for Labor Hour and Time-and-Materials contracts. It uses a burden multiplier model: take the BLS base wage, multiply by a single factor that rolls up fringe, overhead, G&A, and profit into one number. This is the most common IGCE pricing approach for federal professional services. T&M adds a materials estimation step for non-labor costs reimbursed at cost.

**LH vs. T&M:** The only structural difference is materials. LH contracts pay hourly rates for labor only. T&M contracts pay hourly rates for labor plus reimburse materials at cost (FAR 16.601(b)). Both use the same burden multiplier for the labor component. If the user says "IGCE" without specifying a contract type, default to LH unless they mention materials, supplies, licenses, cloud hosting, or similar non-labor costs, in which case default to T&M.

**Required MCP servers:**
1. **bls-oews** -- market wage data by occupation and geography. Key tools: `get_wage_data`, `igce_wage_benchmark`, `list_common_metros`, `list_common_soc_codes`.
2. **gsa-calc** -- awarded GSA MAS ceiling hourly rates. Key tools: `suggest_contains`, `exact_search`, `keyword_search`, `igce_benchmark`, `price_reasonableness_check`.
3. **gsa-perdiem** -- federal CONUS travel lodging and M&IE. Key tools: `lookup_city_perdiem`, `estimate_travel_cost`, `get_mie_breakdown`.

**Regulatory basis:** FAR 15.402 (cost/pricing data). FAR 15.404-1(b) (price analysis). FAR 16.601 (T&M/LH contracts and limited-use criteria).

## Operating Principle (ai-boundaries)

This skill **assembles data** and **formats documents** from reasoning the contracting officer supplies. It does NOT originate evaluative conclusions. Specifically:

- The skill pulls BLS wages, CALC+ ceiling rates, and Per Diem rates, and formats them into a workbook.
- The skill does NOT determine whether a rate is "fair and reasonable" under FAR 15.404-1. That determination is the CO's.
- The skill does NOT assert premiums (TS/SCI, OCONUS, SCIF, specialty labor) that are outside BLS/CALC+/Per Diem data. If a premium is needed and the data does not support it, the skill names the gap and hands the decision back to the CO.
- The skill does NOT draft a price reasonableness memo, a responsibility determination, or any FAR-citing signature document unless the CO has already supplied the rationale and conclusion, in which case the skill formats the CO's text into the template.
- Narrative prose (chat summaries, Methodology sheet, Rate Validation status) avoids evaluative verbs: "defensible," "reasonable," "acceptable," "competitive," "outlier." Replace with neutral positioning: "at P77 of CALC+ pool (n=X)," "within BLS P90 burdened equivalent," "above P50 by Y%, document stacked factors in Methodology."

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

### Workflow A-LH: Labor Hour IGCE (Default)
User needs a cost estimate for a Labor Hour contract. Labor only, no materials. Execute Steps 1 through 9.
Triggers: "build an IGCE," "labor hour IGCE," "LH estimate," "estimate costs for," "price a requirement."

### Workflow A-TM: Time-and-Materials IGCE
Same as A-LH for labor, plus Step 5B for materials. T&M contracts reimburse materials at cost.
Triggers: "T&M IGCE," "time and materials estimate," or when user mentions materials, supplies, licenses, cloud hosting alongside hourly rates.

### Workflow A+: SOW/PWS-Driven Build
User provides a requirement document instead of structured labor inputs. Execute Step 0 first, validate, then route to A-LH or A-TM based on whether materials are needed.
Triggers: "build an IGCE from this SOW," "price this statement of work," or when user provides a block of requirement text.

### Workflow B: LH/T&M Rate Positioning (Data Only, No Determination)

User has proposed rates and wants to see where they sit against market data. The skill returns the data and the CO decides reasonableness. **The skill does not produce a "fair and reasonable" determination, a signed memo, or advisory text telling the CO how to negotiate.**

Triggers: "is this rate reasonable," "validate these rates," "compare vendor pricing," "check this proposal."

**Step 0 / GATE (MANDATORY FIRST — runs before any other Workflow B step).**

**Workflow B entry = gate fires unconditionally.** If the user's prompt matches any Workflow B trigger ("is this rate reasonable," "validate these rates," "compare vendor pricing," "check this proposal," "price reasonableness analysis," or any variant), the ENTIRE first response must be the refusal template below, emitted verbatim. No rate analysis. No CALC+ pull. No BLS pull. No "let me start with the analysis" preamble. No offer to continue with the memo if the user provides more info in the same response. Emit the template. Stop. Wait for the user's explicit Option A or Option B choice. This applies whether or not the prompt contains memo-drafting tokens; the gate is not token-gated.

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

1. Collect the vendor's proposed labor categories, hourly rates, and any scope context (metro, clearance, experience tier).

2. For each LCAT, call `mcp__gsa-calc__price_reasonableness_check(labor_category, proposed_rate, experience_min, education_level)`. The MCP returns count, min/max, median, IQR bounds, z-score, and percentile position. If sample size is below ~25 records, label the pool "directional only, not statistical validation."

3. For senior LCATs, also run the dual-pool flow (title-match + experience-match) and present both medians side-by-side.

4. If metro context matters (DC, SF, NYC, Boston, etc.), pull BLS OEWS for that metro via `mcp__bls-oews__get_wage_data` and present the P50/P75/P90 burdened equivalent at the relevant multiplier. This shows how the rate sits against local market labor independent of the CALC+ nationwide pool.

5. **Present a neutral positioning summary** using non-evaluative language:
   - "Rate sits at CALC+ P77 (n=7, thin-corpus directional only)."
   - "Above P50 by X%; stacked factors: [metro, seniority tier, aging, burden assumption]."
   - "Below P25; pool composition or LCAT alignment may warrant CO review."
   - "Premium factors not captured by this data: [TS/SCI clearance premium, SCIF overhead, specialty market]. CO sets the relevant premium band if one applies."

6. **Stop.** Do not write "the rate is fair and reasonable." Do not recommend negotiation positions. Do not suggest "push back only if..." text. Do not label rates "competitive," "aggressive," "outlier requiring justification."

7. **Memo output (Option B path only).** If the user selected Option B at the Step 0 gate and supplied rationale + determination text, fill the memo template: benchmark tables from Steps 2-4, the user's rationale text verbatim in the findings section, the user's determination text verbatim in the Determination section. Do NOT paraphrase, do NOT add hedging, do NOT originate any conclusion text. Mark DRAFT. Use `[Contracting Officer Name]` and `[Agency]` placeholders. If Option A was selected, skip this step entirely.

## Information to Collect

Ask for everything in a single pass. Provide defaults where noted. If any Required Input is ambiguous or missing for Workflow A (e.g., labor count without discipline, location without metro, fee type not specified), use `AskUserQuestion` to collect before pulling data. Do not guess.

### Required Inputs

| Input | Description | Example |
|-------|-------------|---------|
| Labor categories | Job titles or SOC codes | Software Developer, InfoSec Analyst, PM |
| Performance location | City/state or metro area | Washington, DC |
| Staffing | Headcount per labor category | 2 developers, 1 analyst, 1 PM |
| Hours per year | Productive hours per person (default: 1,880; user input wins, see rule below) | 1,880 |
| Period of performance | Base year + option years | Base + 2 OYs |
| Contract start date | For wage aging | 2026-10-01 |

### Optional Inputs (Defaults Applied If Not Provided)

| Input | Default | Notes |
|-------|---------|-------|
| Burden multiplier | 2.0x | Mid scenario; low (1.8x) and high (2.2x) also produced |
| Escalation rate | 2.5%/yr | Applied to labor, travel, and materials |
| Shift coverage | Business hours (8x5) default | Specify 24x7 / 16x7 / 12x5 if applicable; Step 0.5 computes FTE |
| Travel destinations | None | City/state per destination |
| Travel frequency | None | Trips/year per destination |
| Travel duration | None | Nights per trip (0 = day trip) |
| Number of travelers | All staff | Travelers per trip |
| Travel months | Max monthly rate | Specific months if known |
| FY for per diem | Current federal FY | Compute at build time (Oct-Sep cycle) |
| Duty station / origin | Performance location | For City Pair airfare lookup |
| NAICS code | None | Include in output if provided |
| PSC code | None | Include in output if provided |
| Partial start | Full year (12 months) | Specify months if base year is partial |
| Materials (T&M only) | None | Categories and estimated annual costs |

### Productive Hours Reconciliation (user input wins)

When the user provides productive hours per FTE (commonly 1,920 = 48 × 40, or 1,860 for heavy leave environments), USE THE USER VALUE. Do NOT silently replace with 1,880.

- If user gives `total_hours` and `fte` but not `productive_hours`, back-solve: `productive_hours = total_hours / fte`. If result deviates from 1,880 by more than 5%, flag in methodology.
- If user gives `productive_hours` directly in the handoff, use verbatim.
- Example formulas in this skill use 1,880 for illustration only. Do NOT hardcode 1,880 in your Sheet 1 formulas; reference `$B$6` (the user-provided or default value) instead.

### Contract Vehicle Usage Rule (burden multiplier tuning)

The vehicle collected in Required Inputs is NOT metadata only. It tunes the burden scenario range:

| Vehicle | Low | Mid | High | Notes |
|---------|-----|-----|------|-------|
| GSA MAS IT Schedule 70 (commercial) | 1.8 | 2.0 | 2.2 | Standard commercial IT services |
| OASIS+ (services-centric, commercial) | 1.9 | 2.1 | 2.3 | Slightly higher due to multi-agency overhead |
| Agency-specific IDIQ (cleared / DoD) | 2.0 | 2.2 | 2.4 | Cleared personnel, security overhead |
| DoD Secret cleared (SCIF-adjacent but not SCIF) | 2.2 | 2.4 | 2.6 | Facility clearance, compartmented work |
| SCIF-only (TS/SCI, compartmented) | 2.4 | 2.6 | 3.0 | SCIF facility overhead, TS/SCI eligibility premium |
| DoE M&O contract | 2.2 | 2.4 | 2.6 | M&O overhead structure |
| OCONUS | 2.6 | 2.9 | 3.2 | Hardship, foreign deployment |

If the user provides a vehicle not in the table, default to GSA MAS commercial and flag the assumption in methodology. If the user provides a custom burden multiplier, use it as mid and set low = custom - 0.2, high = custom + 0.2. **DoD-cleared work: pick the Secret row (2.0/2.2/2.4) unless the requirement specifies TS/SCI or SCIF, in which case use the SCIF-only row (2.4/2.6/3.0).**

**CO-supplied DCAA-audited rates (override rule).** If the contracting officer supplies a DCAA-audited burden multiplier from an approved Forward Pricing Rate Agreement (FPRA), a current disclosure statement review, or a bilateral rate agreement, USE THAT RATE instead of the vehicle-table range. Audited rates are a stronger basis than generic vehicle defaults; do not revert to the table and do not "reconcile" the CO's number to the closest vehicle row. Apply the CO-supplied multiplier as a point estimate (single authoritative column on Sheet 1 and Sheet 2); do NOT bookend with ±0.2 sensitivity offsets because the audited rate IS the rate, not a midpoint. If a Low/High band is still required for scenario display, clearly label the band as "sensitivity display only; FPRA is authoritative" in Methodology. Document the source: FPRA effective date, approving authority (e.g., DCAA Region), rate composition if disclosed (fringe / OH / G&A / profit split). If the CO-supplied rate sits outside the vehicle-table range for the stated environment, trust the CO-supplied rate and note the divergence in Methodology rather than reconciling to the table.

## Constants Reference

| Constant | Value | Source |
|----------|-------|--------|
| Standard work year | 2,080 hours | 40 hrs x 52 weeks; converts annual wages to hourly |
| Default productive hours | 1,880 hours/year | 2,080 minus holidays and avg leave |
| Annual coverage hours (24x7) | 8,760 hours | 24 x 365; divide by 2,080 × availability for FTE |
| Default burden multiplier | 2.0x | Mid-range professional services |
| Low scenario burden | 1.8x | Lower bound for scenario analysis |
| High scenario burden | 2.2x | Upper bound for scenario analysis |
| Default escalation rate | 2.5% annually | Standard federal IGCE assumption |
| BLS wage cap (annual) | $239,200 | OEWS reporting ceiling; reconfirm each release |
| BLS wage cap (hourly) | $115.00 | OEWS reporting ceiling; reconfirm each release |
| OEWS data year | 2025 | May 2025 estimates |
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

Converts an unstructured SOW/PWS into structured pricing inputs.

**Process:**
1. **Sufficiency check.** Scan for six priceable elements: labor categories, staffing levels, performance location, period of performance, deliverables, and travel. Flag anything missing. Hard stop if performance location is absent. If 3+ elements missing and document is under 500 words, ask user whether to proceed with assumptions or get clarification.

2. **Task decomposition.** Parse into discrete task areas with description, skill discipline, complexity, and recurring vs. finite classification.

3. **Domain triage.** Identify agency domain (DoD / IC / DOE / civilian IT / research / medical) BEFORE SOC mapping. Domain signals which SOC block applies: DOE → 17-2xxx physical engineering; IC/DoD cyber → 15-1212; civilian IT → 15-125x software/systems; research → 19-1xxx / 15-2xxx; medical → 29-xxxx.

4. **Labor category mapping.** Map tasks to SOC codes using Step 1 heuristics with domain triage result. When a task spans disciplines, map to multiple categories.

5. **Staffing estimation.** Estimate FTEs per category based on scope indicators (system count, shift coverage, surge language, site count). If 24x7 coverage is required, invoke Step 0.5. Present as ranges when ambiguous.

6. **Present decomposition table** for user validation:
```
Task Area               | Labor Category      | SOC Code | Est. FTEs | Basis
Application Development | Software Developer  | 15-1252  | 2-3       | 3 apps, agile
Security Operations     | InfoSec Analyst     | 15-1212  | 1-2       | Continuous monitoring
Project Oversight       | Project Manager     | 13-1082  | 1         | Single contract
```

7. **User validation gate (CRITICAL) - two stages, not one.** Skip Stage A/B gate when user provides structured inputs: LCATs with discipline, location with metro, FTE counts, and PoP all specified. If any of those four are ambiguous or missing, run the gate. Do not conflate "confirm the decomposition" with "pick build parameters." Run them separately:

   **Stage A - Decomposition validation.** After presenting the decomposition table, ask the user to confirm or amend it. Use `AskUserQuestion` with options like "Decomposition looks right, proceed" / "Modify LCAT X" / "Add LCAT Y" / "Adjust FTE estimates." Response MUST END after this question. Wait for explicit confirmation before continuing.

   **Stage B - Build parameters.** Only after the decomposition is confirmed, ask the remaining parameter questions in a separate `AskUserQuestion` call: LH vs. T&M ("Does this requirement include materials the contractor will procure (software licenses, cloud hosting, hardware)? If yes, I'll build a T&M IGCE with materials. If labor only, I'll build LH."), vehicle preset, metro confirmation, contract start, NAICS/PSC, shift coverage density if 24x7. Response MUST END after this question.

   DO NOT self-approve either stage. DO NOT skip Stage A to go straight to parameters. Proceeding to Step 1+ before Stage B is also answered is a skill violation. The user must affirmatively validate BOTH the decomposition and the parameters before build work begins.

### Step 0.5: Shift Coverage Staffing (If 24x7 or Multi-Shift)

If the requirement specifies 24x7 coverage, around-the-clock SOC, NOSC, help desk, or continuous monitoring, headcount must be grossed up from productive hours to coverage hours.

**Single-seat 24x7 (one analyst always on duty):** 4.2 FTE.

Derivation: one shift covers 2,080 hrs/yr at ~95% availability. Four shifts cover 8,760 annual hours with 50% blended availability (leave, training, overlap, turnover). Industry convention.

```
annual_coverage_hours = 24 * 365 = 8,760
productive_hours_per_fte = 2,080
single_seat_fte = 4.2 FTE   # industry convention
```

**Double-seat 24x7 (two analysts always on duty):** 8.4 FTE.

**12x5 coverage (business hours, weekdays only):** 60 hrs/wk × 52 = 3,120 annual hrs. 3,120 / 1,880 = 1.66 FTE single-seat, ~2 FTE with overlap.

**16x7 coverage (extended hours, every day):** 16 × 365 = 5,840 annual hrs. 5,840 / 1,880 × availability = ~3.1 FTE single-seat.

Document the FTE math in Sheet 5 Methodology. Do NOT quietly use 3 FTE for 24x7 coverage: that understaffs by 28%.

### Step 1: Map Labor Categories to SOC Codes

Map user job titles to SOC codes. Apply domain triage from Step 0 first.

**IT and Professional Services (most common):**

| Common Title | SOC Code | BLS Title |
|-------------|----------|-----------|
| Program Manager (general ops) | 11-1021 | General and Operations Managers |
| Program Manager (IT) | 11-3021 | Computer and Information Systems Managers |
| Program Manager (engineering) | 11-9041 | Architectural and Engineering Managers |
| Project Manager | 13-1082 | Project Management Specialists |
| Management Analyst | 13-1111 | Management Analysts |
| Systems Engineer / Analyst (IT) | 15-1211 | Computer Systems Analysts |
| Software Developer | 15-1252 | Software Developers |
| Cybersecurity / InfoSec | 15-1212 | Information Security Analysts |
| Network Architect | 15-1241 | Computer Network Architects |
| DBA | 15-1242 | Database Administrators |
| Sysadmin | 15-1244 | Network and Computer Systems Administrators |
| QA Tester | 15-1253 | Software QA Analysts and Testers |
| Help Desk | 15-1232 | Computer User Support Specialists |
| Data Scientist | 15-2051 | Data Scientists |
| Technical Writer | 27-3042 | Technical Writers |
| Contracting Specialist | 13-1020 | Buyers and Purchasing Agents |

**Physical / DOE / Defense Engineering (use these for hardware, labs, weapons systems, DOE M&O, physical infrastructure):**

| Common Title | SOC Code | BLS Title |
|-------------|----------|-----------|
| Aerospace Engineer | 17-2011 | Aerospace Engineers |
| Biomedical Engineer | 17-2031 | Biomedical Engineers |
| Chemical Engineer | 17-2041 | Chemical Engineers |
| Civil Engineer | 17-2051 | Civil Engineers |
| Electrical Engineer | 17-2071 | Electrical Engineers |
| Electronics Engineer | 17-2072 | Electronics Engineers, Except Computer |
| Environmental Engineer | 17-2081 | Environmental Engineers |
| Industrial Engineer | 17-2112 | Industrial Engineers |
| Mechanical Engineer | 17-2141 | Mechanical Engineers |
| Nuclear Engineer | 17-2161 | Nuclear Engineers |
| Petroleum Engineer | 17-2171 | Petroleum Engineers |
| Engineers, All Other (fallback) | 17-2199 | Engineers, All Other |

Use 17-2199 when the role doesn't cleanly fit one engineering discipline (RF, antenna, radar, systems integration specialties). Pull alongside a specific engineering SOC for comparison.

When mapping is ambiguous, query multiple SOC codes and present the range.

**PM SOC decision.** Pick by what the PM actually manages:

| PM manages... | Default SOC |
|---|---|
| IT infrastructure / platform / software systems | 11-3021 Computer and Information Systems Managers |
| Services team (cyber/IR/SOC, managed services, analytics, specialty) | 13-1082 Project Management Specialists |
| Physical engineering / hardware / lab | 11-9041 Architectural and Engineering Managers |
| Non-IT operations (logistics, admin) | 11-1021 General and Operations Managers |

Do NOT default to 15-1299 (Computer Occupations, All Other) for IT PM — under-represents DoD IT PM wages by ~20% vs CALC+.

**Network Engineer:** default 15-1241 (Computer Network Architects) for design/architecture scope; use 15-1244 (Network and Computer Systems Administrators) when PWS scope is operations/NOC sysadmin.

**Seniority default (no tier label):** P50 (median). Exceptions:
- Cleared-contract PM → P75 (cleared PM pool skews senior; P50 understates)
- Small cleared team (<5 FTE total) → temper PM to P60-P70, not full P75
- "Tech Lead," "Principal," "Chief" → P90

Document percentile choice in methodology.

**Divergence-triggered SOC re-pick.** If an LCAT's BLS burdened rate diverges >15% vs CALC+ median AND the SOC was a judgment call, pull alternative SOCs, pick the one validating within ±15%. If both candidates exceed 15%, pick smaller absolute divergence and label "cite range, dual-pull blended" in methodology. Retain every queried SOC (winners and rejected alternatives) in the Raw Data sheet with wages and divergence so the decision is reproducible.

### Step 2: Pull BLS Wage Data

**Use the BLS OEWS API skill.** For each labor category, query datatypes 04 (annual mean), 11-15 (10th through 90th percentiles) at the performance location.

**BLS series ID component breakdown (25 chars total):**
```
prefix(4) + area(7) + industry(6) + SOC(6) + datatype(2) = 25
OEU  M  +  0047900 +  000000  +  151212 +  13  = OEUM004790000000015121213
```
- Prefix OEUM = metro; OEUS = state; OEUN = national
- Area must be 7 chars (pad with leading zeros)
- SOC must be exactly 6 chars (no trailing zeros: 151212 not 15121200)
- Industry 000000 for cross-industry

Use metro-level prefix (OEUM) when available. Fall back to state (OEUS), then national (OEUN). Present the full wage distribution. If the target metro is not in `list_common_metros`, resolve the MSA code via https://www.bls.gov/oes/current/msa_def.htm and pass the 7-char code directly to `get_wage_data`. Do not fall back to state-level wages without first checking the MSA directory.

**Seniority modeling via percentiles:** When an LCAT is explicitly Junior / Mid / Senior, map to wage percentiles rather than pulling three separate SOCs:
- Junior → P25 (datatype 12)
- Mid → P50 median (datatype 13)
- Senior → P75 (datatype 14)

Pull all 5 percentiles (P10/P25/P50/P75/P90) for any multi-level LCAT. Cite which percentile was used per LCAT in methodology.

**Silent-wrong-answer traps:**
- **MSA renumbering (2024 OMB Bulletin 23-01).** If a metro query returns NO_DATA across EVERY SOC (not just one), the metro was renumbered, not suppressed. Cleveland moved from 17460 to 17410. Dayton may also have moved. Verify against the current BLS MSA list: `https://www.bls.gov/oes/current/oessrci.htm`. Do NOT fall back to state assuming occupation suppression until you've checked the code.
- **Wrong trailing zeros.** 151212 is the 6-char SOC. 15121200 is a Standard SOC 8-digit format that will fail the 25-char series ID assertion AFTER several queries have already constructed.

If BLS returns "-" with footnote code 5, the wage exceeds the $239,200 cap. Use the cap as a lower bound and flag in the narrative. If the chosen percentile lands within 10% of the cap (≥ $215,280 annual / ≥ $103.50 hourly), note in Methodology that the local market may exceed the stated value and flag for CO review.

**BLS flat-tail detection.** If P75 equals P90 in the BLS return AND neither hits the $239,200 cap, the local top-tail is sample-constrained (single dominant employer, thin high-end pool). Flag in Methodology: "Local P75/P90 collapsed; top-tail data sparse, local market may run higher than stated."

### Step 2B: Age BLS Wages to Contract Start Date

BLS OEWS data publishes about a year in arrears (May 2025 estimates released April 2026). If the contract Period of Performance starts after the data reference period, the base wages must be aged forward to avoid understating costs.

```
months_gap = months between BLS data vintage (May 2025) and contract PoP start date
aging_factor = (1 + escalation_rate) ^ (months_gap / 12)
aged_annual_wage = annual_median * aging_factor
```

Example: if the contract start is 29 months after the BLS data vintage, at 2.5% escalation the aging_factor = 1.025^(29/12) = ~1.061. A $100,000 BLS median becomes $106,100 before burden multiplier.

**Aging factor must be a cell-referenced formula in the workbook, NOT hardcoded.** Use the assumption block rows to hold BLS_vintage, contract_start, months_gap, and aging_factor. If the user changes the contract start assumption, the whole sheet must recompute correctly. See Step 8 assumption block layout.

Use the aged wage as the basis for all subsequent calculations. Document the aging adjustment in the Methodology sheet: "BLS OEWS wages (data vintage: [BLS_vintage]) aged forward [X] months to [contract start] at [escalation rate]%/yr to account for data lag."

If the user does not provide a contract start date, ask for one. If unknown, default to 6 months from today and note the assumption.

The escalation applied in Step 7 across option years starts AFTER this aging adjustment. Step 2B ages the base wage to the contract start; Step 7 escalates from that adjusted base across the period of performance. These are not double-counted.

### Step 3: Apply Burden Multiplier (Three Scenarios)

Convert BLS base wages to estimated fully burdened hourly rates:

```
hourly_base = aged_annual_wage / 2080
burdened_low  = hourly_base * burden_low    # default 1.8
burdened_mid  = hourly_base * burden_mid    # default 2.0
burdened_high = hourly_base * burden_high   # default 2.2
```

Note: 2,080 converts annual to hourly. Productive hours (1,880) are used separately in Step 7 for annual cost and account for holidays and leave.

### Step 4: Cross-Reference Against CALC+

**Invoke the GSA CALC+ Ceiling Rates API skill per its own documentation for base URL, pre-flight endpoint check, and `keyword=` vs `search=` rules.** Do NOT hardcode a CALC+ URL in this skill's code blocks; the CALC+ skill is authoritative and has moved endpoints in the past.

**IGCE use case for CALC+:** directional sanity-layer validation of BLS-burdened rates against GSA MAS awarded ceiling pool. `keyword=` is acceptable here per the CALC+ skill (sanity layer, not formal rate statistics). Full endpoint base URL, response envelope shape, and corpus skew guidance all live in the CALC+ skill.

**Default for Workflow A rate validation:** use `mcp__gsa-calc__igce_benchmark`. Call `keyword_search` only when you need the example-rate or labor-category buckets. igce_benchmark returns trimmed stats (count, min/max/mean, P10-P90) without the 50KB+ labor_category/current_price aggregation buckets that blow up response size. `page_size=0` is no longer accepted by the MCP. Use `page_size=1` minimum when aggregation stats are needed; prefer `mcp__gsa-calc__igce_benchmark` for stats-only access (no corpus, trimmed return shape).

Match the vendor's tier in the keyword, not the aggregate title. For 'Mid Software Developer' query `Software Developer II` not `Software Developer` — the aggregate pool mixes interns through Senior levels and can falsely flag rates as +70% divergent when the tier-matched pool is +11%.

Example call pattern (resolve actual base URL from the CALC+ skill at invocation time):
```
GET {CALC_BASE_URL}?keyword=Software+Developer&page_size=1
```

**CRITICAL JSON paths for CALC+ statistics:**
```python
aggs = response_json["aggregations"]
count    = aggs["wage_stats"]["count"]
min_rate = aggs["wage_stats"]["min"]
max_rate = aggs["wage_stats"]["max"]
avg_rate = aggs["wage_stats"]["avg"]
median   = aggs["histogram_percentiles"]["values"]["50.0"]   # CORRECT median
p25      = aggs["histogram_percentiles"]["values"]["25.0"]
p75      = aggs["histogram_percentiles"]["values"]["75.0"]
```

**WARNING:** Do NOT read `wage_stats` or `histogram_percentiles` from the top level. They live under `aggregations.*`. Do NOT read from `wage_percentiles` (empty when page_size=1). Always use `histogram_percentiles`.

**Dual-pool analysis for senior LCATs:** When title-match alone returns N<10, add a second query with experience-anchored keyword:
- Pool A (title-match): `keyword=Senior+Software+Engineer`
- Pool B (experience-match): `keyword=Software+Engineer+10+years`

Report both counts and medians. Use Pool A primary if N≥10; otherwise blend or cite Pool B as sanity layer.

**Rate validation band for LH/T&M (BLS burdened mid vs CALC+ median):**

LH/T&M burdened rates are a DIRECT comparison to CALC+ ceiling rates (both represent total billable hourly labor). Tighter tolerance than FFP or CR.

| Divergence | Interpretation | Action |
|------------|---------------|--------|
| 0 to ±5% | Expected range | Accept without explanation |
| ±5 to ±15% | Cite range | Document in narrative, show distribution |
| > ±15% | Position outside ±15% band; document stacked factors in Methodology | Flag in Status column |

Divergence formula: `((bls_burdened - calc_median) / calc_median) * 100`. Divergence is a data point requiring explanation, not an error.

### Step 5: Pull Per Diem Rates (If Travel Required)

**Use the GSA Per Diem Rates API skill.** Query monthly lodging rates and M&IE for each destination.

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

**Same-metro TDY proximity check.** If `performance_location` MSA equals `travel_destination` MSA (same metro, <50 mi), overnight lodging per diem may not qualify under FTR 301-7.103. Flag in Methodology: "Same-MSA travel; if this is not overnight TDY, zero the lodging line and use mileage only."

**City Pair airfare (optional):** When origin and destination are known, look up YCA fares at cpsearch.fas.gsa.gov. Skip if origin unknown, OCONUS, local travel, or user provides own airfare.

**Per-trip cost by trip length:**

**Standard multi-night trip (2+ nights):**
```
lodging_per_trip = nightly_rate * nights
travel_days = nights + 1
full_day_mie = mie_rate * max(0, travel_days - 2)
partial_day_mie = mie_rate * 0.75 * 2    # first and last day at 75%
mie_per_trip = full_day_mie + partial_day_mie
trip_total = lodging_per_trip + mie_per_trip
```

**1-night trip:**
```
lodging_per_trip = nightly_rate * 1
mie_per_trip = mie_rate * 0.75 * 2   # both days partial
trip_total = lodging_per_trip + mie_per_trip
```

**0-night day trip (same-day return):**
```
lodging_per_trip = 0                 # no overnight stay
mie_per_trip = mie_rate * 0.75       # single partial day only
trip_total = mie_per_trip
```

The MCP `mcp__gsa-perdiem__get_mie_breakdown` returns `mie_first_last_day` already discounted to 75%. Use that value directly. Do NOT multiply by 0.75 again or you ship 25% low M&IE on day trips. Formula on MCP output: `mie_per_trip = mie_first_last_day` for 0-night trips.

```
annual_travel = trip_total * trips_per_year * travelers
```

Use max monthly lodging rate as conservative ceiling if specific months not provided.

If the contract PoP start is within 6 months of the next federal fiscal year, query both FYs; if the target FY is not yet published (FY{N+1} publishes mid-August {N}), use current FY as conservative baseline and note in methodology: 'refresh on FY{N+1} publication.'

**No travel case:** When no travel, include the sheet with a single 'Travel Not Applicable' text block. Do not skip the sheet — Sheet 1 Travel row still needs a cell reference target. Sheet 1 Travel row = 0 literal.

### Step 5B: Materials Estimation (T&M Only)

T&M contracts reimburse materials at cost per FAR 16.601(b). Skip this step for LH workflows.

**Common T&M materials categories:**

| Category | Examples | Estimation Approach |
|----------|---------|---------------------|
| Software licenses | JIRA, Confluence, IDE licenses | Per-seat annual cost x users |
| Cloud hosting / IaaS | AWS, Azure, GCP | Monthly spend x 12 |
| Hardware / equipment | Laptops, monitors, peripherals | Per-unit cost x quantity, typically year 1 only |
| Training / certifications | Cloud certs, security clearance | Per-person cost x staff |
| Subscriptions / SaaS | Monitoring tools, data services | Annual subscription cost |
| Lab / test environments | Test servers, sandbox environments | Monthly or annual cost |

**If user provides specifics:** Create Materials Detail rows with annual cost, apply escalation across option years (same rate as labor).

**If user says materials exist but no specifics:** Include placeholder rows with numeric 0 (NOT text "TBD") for each common category. Note in methodology that materials must be added before IGCE is complete. Text "TBD" in numeric cells breaks SUM formulas.

**CRITICAL: Materials are NOT affected by the burden multiplier.** They are reimbursed at cost. Burden only applies to labor. Keep materials and labor cost streams separate in all formulas.

**Materials Handling Fee Decision Gate (REQUIRED for T&M):**

FAR 16.601(b)(2) lets the contractor recover actual cost for materials. FAR 31.205-26(e) permits a reasonable material handling fee IF the contractor's indirect rates already include such costs. Most T&M IGCEs default to pure at-cost with no handling fee. But the decision must be surfaced, not silently defaulted. Before computing materials totals, explicitly state:

- **Default choice: pure at-cost (no handling fee).** Document in methodology: "Materials priced at cost per FAR 16.601(b)(2). No material handling fee applied. If the awarded contractor has a DCAA-approved material handling rate in their indirect pools, the government may apply it post-award; IGCE remains at cost as the cost-side baseline."
- **Alternative: include a handling fee** if the solicitation specifically contemplates one or the user asks. Handling fee cap: commonly 5-10% of materials cost; never apply G&A or profit on top of the fee. Cite FAR 31.205-26 in methodology.

Ask the user explicitly if the contract anticipates a handling fee before applying one. If not surfaced, default to at-cost with the methodology note above. Silent defaults are the failure mode.

**Materials in IGCE Summary (Sheet 1):**
```
Materials Subtotal       |     |         | $45,000    | $46,125    | $47,278    | $138,403
  Software Licenses      |     |         | $15,000    | $15,375    | $15,759    | $46,134
  Cloud Hosting          |     |         | $24,000    | $24,600    | $25,215    | $73,815
  Hardware               |     |         | $6,000     | $6,150     | $6,304     | $18,454
```

### Step 6: Handle Multi-Location Weighting

**Option A (default blend):** Use highest median across locations per category. Use when user does not specify per-location headcount.

**Option B (weighted):** `weighted_wage = (wage_A * pct_A) + (wage_B * pct_B)` if user provides split.

**Option C (separate lines, DEFAULT when headcount per location is explicit):** Dedicated staff per location get separate rows. Do NOT prompt for Option A/B/C when user gave headcount like "4 FTE Fort Meade, 3 FTE Colorado Springs": go straight to Option C.

### Step 7: Calculate Annual Costs, Prorate, and Apply Escalation

**Labor cost per category per year (full year):**
```
annual_labor = burdened_hourly * productive_hours * headcount
```

**Partial-year proration:**
```
prorated_hours = productive_hours * (months_in_period / 12)
prorated_labor = burdened_hourly * prorated_hours * headcount
prorated_travel = annual_travel * (months_in_period / 12)
prorated_materials = annual_materials * (months_in_period / 12)
```

**Escalation:** `year_N_cost = base_year_cost * (1 + escalation_rate) ^ N`

Apply to labor, travel, and materials. Default 2.5%.

**Scenario math (three burden levels across all periods):**
```
low_year_N  = (hourly_base * burden_low)  * productive_hours * headcount * (1+esc)^N
mid_year_N  = (hourly_base * burden_mid)  * productive_hours * headcount * (1+esc)^N
high_year_N = (hourly_base * burden_high) * productive_hours * headcount * (1+esc)^N
```

Travel and materials are identical across all three scenarios (per diem is published; materials are at cost). **Sheet 2 formula:** Each scenario's period total = labor(at that burden) + travel + materials. Do NOT apply burden to travel or materials.

### Step 8: Produce the IGCE Workbook

Generate a multi-sheet .xlsx workbook using openpyxl. Use Excel formulas for all calculations. Run the recalc script (`python /mnt/skills/public/xlsx/scripts/recalc.py <file>`) before presenting.

**Workbook structure (6 sheets for LH, 7 for T&M; subtract 1 if no travel):**

**Sheet 1: IGCE Summary.** Labor categories as rows, periods as columns. Qty, Rate/Hr, annual cost per period. Travel rows below labor. For T&M: Materials rows below travel. Placeholder rows for Airfare, Ground Transportation, ODCs as numeric 0 (NOT text "TBD") to prevent #VALUE! errors in SUM formulas. Grand total with SUM formulas.

**Assumption cell layout (Sheet 1, rows 1-11) — LOCK THIS EXACTLY:**
```
A1: "IGCE Assumptions"                         (bold, merged A1:B1)
A2: "Burden Multiplier (Low)"                  B2: 1.8     (blue)
A3: "Burden Multiplier (Mid)"                  B3: 2.0     (blue)
A4: "Burden Multiplier (High)"                 B4: 2.2     (blue)
A5: "Escalation Rate"                          B5: 0.025   (blue, pct)
A6: "Productive Hours/Year"                    B6: 1880    (blue)
A7: "Base Year Months"                         B7: 12      (blue; <12 for partial)
A8: "BLS Vintage"                              B8: =DATE(2025,5,1)           (blue, real date)
A9: "Contract Start"                           B9: =DATE(2026,10,1)          (blue, real date, user-editable)
A10: "Months Gap"                              B10: =DATEDIF(B8,B9,"m")      (formula)
A11: "Aging Factor"                            B11: =(1+B5)^(B10/12)         (formula)
A12: (blank row separator)
A13: header row for data table
```

**DOWNSTREAM CELL REFERENCES — MEMORIZE THESE; DO NOT DRIFT:**

```
$B$2 = Burden Low                    (Sheet 2 low scenario formulas)
$B$3 = Burden Mid                    (Sheet 1 burdened-rate formulas + Sheet 2 mid)
$B$4 = Burden High                   (Sheet 2 high scenario formulas)
$B$5 = Escalation Rate               (ALL option-year AND materials formulas)
$B$6 = Productive Hours/Year         (reference only; do NOT put in formulas)
$B$7 = Base Year Months              (base-year proration as $B$7/12)
$B$11 = Aging Factor                 (multiplies ALL raw BLS wages)
```

**Validation gate: before writing Sheet 1 formulas, paste the reference map above into your working notes.** Workers have shipped off-by-one bugs where `$B$4` was treated as escalation (actually High burden) and `$B$6` as Base Year Months (actually Productive Hours). One scenario produced a $105M/FTE base year before the worker caught the drift on value inspection. Recalc does not detect this because the formulas are syntactically valid; they just reference the wrong cells.

**Sheet 2: Scenario Analysis.** Three side-by-side tables (low/mid/high burden). Burden multiplier cells in blue font. Blocks are 15 rows each per LCAT (13 content + 2 separator).

**Block layout formula:** `row(N) = 1 + (N-1) * 15` where N is the LCAT index. Block 1 starts at row 1; block 2 at row 16. Each block is 15 rows (13 content + 2 separator).

**Offset convention (READ CAREFULLY — silent-wrong-answer trap).** `+K` means the K-th row of the block where `+1` is block_start itself (the LCAT header row), NOT one row below block_start. For block 1 (block_start=1), `+K = row K`. For block 2 (block_start=16), `+K = row 15 + K`. Concrete row numbers for block 1 are shown in parentheses below to disambiguate:
- +1 (row 1): LCAT header (merged)
- +2 (row 2): "Measure" | "Value" | blank | "Period" | Low | Mid | High
- +3 (row 3): BLS Base Annual Wage (raw BLS pull, hardcoded)
- +4 (row 4): Aged Annual Wage (= Row+3 * $B$11 aging factor)
- +5 (row 5): Direct Labor Rate Hourly (= Row+4 / 2080)
- +6 (row 6): Burdened Low (= hourly × $B$2)
- +7 (row 7): Burdened Mid (= hourly × $B$3)
- +8 (row 8): Burdened High (= hourly × $B$4)
- +9 (row 9): blank separator (1st of 2 separators per block)
- +10 through +13 (rows 10-13): period rows (Base, OY1, OY2, OY3) × three burden columns
- +14 (row 14): Total row (SUM of +10 through +13)
- +15 (row 15): trailing separator (2nd of 2 separators per block)

The Aged Annual Wage gets its own row so the aging math is visible on the sheet; a reviewer can see BLS Base and Aged side by side. Sheet 2 blocks compute hourly rates. Sheet 1 Summary multiplies by productive hours × FTE × period duration for annual figures. Formula: `Sheet 1 annual = 'Scenario Analysis'!burdened_mid * $B$6 * FTE * ($B$7/12)`.

Travel and materials identical across scenarios. Summary row at the bottom: "Range: $X (low) to $Y (high), Mid estimate: $Z."

**Annotation text gotcha:** Annotation cells (column C or D methodology notes) cannot START with `= + - @` or Excel tries to parse as a formula. Prefix with apostrophe (`'=2,080 hours/year`) or lead with a non-operator character (`"Note: 2,080 hours/year"`). Applies anywhere a cell value starts with those four characters.

**Sheet 3: Rate Validation.** BLS burdened rate (mid), CALC+ 25th/50th/75th percentiles, min/max range, divergence percentage (formula), Status column calibrated to LH/T&M bands.
```
Row 1: "Rate Validation (LH/T&M)"
Row 3: Headers: Category | BLS Burdened (mid) | CALC+ 25th | CALC+ 50th | CALC+ 75th | CALC+ Count | Divergence vs Median | Status
Row 4+: one row per category
  Divergence = (BLS_burdened - CALC_50th) / CALC_50th
  Status =
    IF(ABS(Divergence) <= 0.05, "Expected range",
    IF(ABS(Divergence) <= 0.15, "Cite range",
    "Position outside +-15% band; document stacked factors in Methodology"))
```

Dual-pool columns when title-match N<10: add "Pool A (Title)" and "Pool B (Experience)" median columns, cite N for each.

**Sheet 4: Travel Detail.** Formula-driven per destination. When no travel, include the sheet with a single 'Travel Not Applicable' text block. Do not skip the sheet; Sheet 1 Travel row still needs a cell reference target.

**Multi-destination parameterization.** For M destinations, block N starts at row `1 + (N-1) * 17` with a 16-row content layout and 1-row separator. In-block row indices shift by `(N-1) * 17`. Do NOT hard-code one city: if the user provides "2 trips/yr to Huntsville + 4 trips/yr to San Diego," build two blocks with distinct labeled headers ("Travel Cost Detail: Huntsville, AL" and "Travel Cost Detail: San Diego, CA") and have Sheet 1 Travel rows SUM across destinations:

```
Annual travel (Sheet 1) = SUM across destinations of annual_travel_cost cell
                        = SUM('Travel Detail'!$B$14, 'Travel Detail'!$B$31, ...)
```

Single-destination single-block layout (block 1, rows 1-14):

```
Row 1: "Travel Cost Detail: [Destination]"  (bold header)
Row 3: A="Fiscal Year"           B=<current federal FY>          (blue)
Row 4: A="Nightly Lodging Rate"  B=[max monthly]                 (blue)
Row 5: A="M&IE Daily Rate"       B=[rate]                        (blue)
Row 6: A="First/Last Day M&IE"   B==B5*0.75                      (formula)
Row 7: A="Nights per Trip"       B=[nights, 0 for day trip]       (blue)
Row 8: A="Travel Days"           B==IF(B7=0,1,B7+1)              (formula)
Row 9: A="Lodging per Trip"      B==B4*B7                        (formula, 0 when nights=0)
Row 10: A="M&IE per Trip"        B==IF(B7=0,B6,B5*MAX(0,B8-2)+B6*2)  (formula)
Row 11: A="Trip Total"           B==B9+B10                       (formula)
Row 12: A="Trips per Year"       B=[trips]                       (blue)
Row 13: A="Travelers"            B=[count]                       (blue)
Row 14: A="Annual Travel Cost"   B==B11*B12*B13                  (formula, bold)
```

**Sheet 5: Methodology.** Narrative for the contract file. Target length: 8-12 sections, 2-4 sentences each, readable in 3 minutes. Longer than 14 sections usually means restating data that already lives in Sheet 1-4.

**Important: do NOT merge section-header cells if you also write to column B on the same row.** openpyxl raises "'MergedCell' object attribute 'value' is read-only" when a merge covers A:C and then a write targets B of the merged range. Two-column label/value layout: put section headers on their own rows (no merge), then use adjacent A/B rows for label/value pairs.

**Required sections in methodology:**

- Contract type (LH or T&M) with FAR citation
- Regulatory basis (use the citation set below)
- Vehicle / NAICS / PSC (if provided)
- Performance location
- Period of performance
- Data sources with vintages (BLS OEWS [data vintage], CALC+ queried [date], Per Diem [current FY])
- SOC code mapping decisions (note any alternatives pulled and why the chosen one won)
- BLS aging adjustment (months_gap, aging_factor, formula reference)
- Productive hours assumption (cite PWS-provided value if applicable)
- Burden multiplier rationale plus scenario range
- Escalation basis
- Partial-year proration if applied
- Travel calculation methodology (including 0-night day trips if applicable)
- Rate validation (CALC+) with divergence explanations
- What is NOT included (airfare, ground, subcontractor, etc.)
- Limitations and caveats

**FAR citation set (use all applicable):**

- **FAR 15.402** (cost and pricing data): always cite for IGCE defensibility
- **FAR 15.404-1(b)** (price analysis): always cite
- **FAR 16.601** (T&M and LH contracts): always cite for this skill
- **FAR 16.601(b)(2)** (T&M only; materials reimbursed at cost): cite when materials present
- **FAR 16.601(c)(3)** (T&M surveillance requirement): REQUIRED in T&M methodology. Must explicitly acknowledge: "FAR 16.601(c)(3) requires appropriate government surveillance during performance to provide reasonable assurance that efficient methods and effective cost controls are used. The awarded contract file should document the surveillance plan."
- **FAR 31.205-46** (travel costs): REQUIRED when travel is in scope. Cite alongside FTR 301-11.101 for the 75% first/last-day M&IE rule.
- **FAR 31.205-26** (material costs): cite if a material handling fee is applied (see Step 5B).

**Labor Category Ceiling Hours requirement (LH and T&M per FAR 16.601(c)(2)):** Sheet 1 labor table already shows hours per LCAT. Methodology should annotate: "Labor Category Ceiling Hours presented per FAR 16.601(c)(2); contract ceiling hours per LCAT are binding NTE limits for solicitation purposes."

**Sheet 6: Raw Data.** All API query parameters and responses: BLS series IDs, CALC+ keyword + endpoint + record counts, per diem query details, City Pair fares if retrieved. Record summary tables (count, percentiles, series IDs, query parameters) — NOT raw JSON dumps. A reviewer should reproduce the query from the parameters, not wade through 50KB of aggregation buckets.

**Sheet 7: Materials Detail (T&M only).** One row per materials category with annual cost, escalation across periods, and subtotals. Blue font on all cost inputs. Note that materials are at cost, no burden applied. Use numeric 0 for unknown amounts (not text "TBD").

**Formatting standards:**
- Blue font (RGB 0,0,255) for all user-adjustable inputs and assumptions
- Black font for all formula cells
- Currency: `$#,##0` with negatives in parentheses
- Percentage: `0.0%`
- Bold headers with light gray fill
- Freeze panes below assumption block on Sheet 1 (below row 12)
- Auto-size column widths
- Burden multiplier display format: `0.0"x"`

When base year is partial, prorate: `=burdened_rate*$B$6*($B$7/12)*headcount`. Travel and materials prorate the same way. Full option years ignore $B$7.

Never output as .md or HTML unless explicitly requested.

### Step 8.5: Post-Build Sanity (REQUIRED before presenting)

`recalc.py` returning zero formula errors is necessary but NOT sufficient. Syntactically valid formulas can reference the wrong cells and produce wildly wrong values. Run ALL three gates below before calling `present_files`.

**Gate 1: Per-FTE annualized cost in defensible range.**

Pick the first LCAT. Compute its base-year cost divided by FTE count. Must fall in `[100,000, 1,000,000]`. Outside that range, formulas are referencing wrong cells.

```python
from openpyxl import load_workbook
wb = load_workbook(workbook_path, data_only=True)
summary = wb["IGCE Summary"]
# Adjust column letters to your actual Sheet 1 layout — FTE column and base-year total column
first_lcat_fte = summary["F14"].value   # qty column
first_lcat_base_cost = summary["H14"].value  # base-year total
per_fte = first_lcat_base_cost / first_lcat_fte if first_lcat_fte else 0
assert 100_000 <= per_fte <= 1_000_000, f"Per-FTE ${per_fte:,.0f} outside defensible range"
```

**Gate 2: Sheet 1 Grand Total == Sheet 2 Mid-Scenario Grand Total** within $0.01. Divergence = sheets pulling from different assumption cells.

**Gate 3: Burden multiplier cell on Sheet 2 equals `$B$3` on Sheet 1.** Block 1 Burdened Mid is at **`B7`** on Sheet 2 (offset `+7` per the block layout — see offset convention above; row 7 for block 1). For block N, the cell is `B{7 + (N-1)*15}`. Compare `wb["Scenario Analysis"]["B7"].value` to `wb["IGCE Summary"]["B3"].value` within 0.001. (Prior versions of this skill referenced `B9` here, which is the blank separator row — a silent-wrong-answer bug.)

**Environment-specific recalc handling:**
- **claude.ai web chat:** rerun `python /mnt/skills/public/xlsx/scripts/recalc.py <file>`.
- **Claude Code CLI (no LibreOffice):** the recalc script is unavailable. Compute the expected grand total in Python across base + option years:

```python
expected = 0
for lcat in lcats:
    base_year = lcat.burdened_mid * productive_hours * lcat.fte * (base_months / 12)
    expected += base_year
    for oy_index in range(1, num_oys + 1):
        expected += base_year * (1 + escalation_rate) ** oy_index
```

Verify the workbook grand total lands within 1% of `expected`. If not, aging-factor cross-reference or block-indexing shift is likely the cause.

- **macOS Claude Desktop with Numbers:** Numbers auto-recalculates on file open; no script needed.

**Pre-delivery critical checks (all must pass):**
- Cell references match the DOWNSTREAM CELL REFERENCES map (no drift between prose and layout)
- Aging factor is a cell-referenced formula, not a hardcoded multiplier
- Escalation not double-counted (option years escalate from base; base year does NOT)
- Placeholder rows use numeric 0, not text "TBD" — SUM formulas intact
- Travel math respects FTR 301-11.101 (75% first/last day M&IE; 0-night day trips = single partial day)
- FAR citations present: 16.601 (always), 16.601(b)(2) (T&M materials), 16.601(c)(2) (ceiling hours), 16.601(c)(3) (T&M surveillance), 31.205-46 (travel)
- CALC+ divergence >15% items justified in Methodology or SOC re-picked; Raw Data includes rejected alternatives

### Step 9: Present the File

**Environment-specific delivery:**
- **claude.ai web chat:** copy to `/mnt/user-data/outputs/<name>.xlsx` and call `present_files([...])`.
- **Claude Code CLI:** write to `$PWD` or user-supplied path. Print the absolute path. On macOS also run `open <path>`; on Linux `xdg-open <path>`; on Windows `start "" <path>`. Do NOT try `/mnt/user-data/outputs/` — does not exist outside claude.ai.
- **macOS Claude Desktop with Numbers:** write path, run `open <path>`. Numbers auto-recalculates on open.
- **macOS Claude Code CLI with Excel or Numbers installed:** write to `$PWD`, then run `open <path>`. The system default handler triggers recalc on open; no Python-side expected-total check is needed.

Do NOT skip delivery. A workbook in the sandbox that isn't surfaced looks like a silent failure.

## Edge Cases

**Silent-wrong-answer traps:**
- `q=` parameter on CALC+ returns the full 265K-record corpus silently. Always use `keyword=` or `search=`.
- `wage_stats` read from top level returns None. Always read from `aggregations.wage_stats`.
- MSA code renumbering (Cleveland 17460 → 17410) returns NO_DATA silently. Verify code if all datatypes return empty.
- BLS SOC with trailing zeros (151212 vs 15121200) fails the 25-char assertion AFTER you've already constructed several queries. Use exactly 6-char SOC.
- Annotation text starting with `= + - @` triggers Excel formula parse. Escape with apostrophe or lead with text.
- ODC / placeholder cells set to text "TBD" break SUM formulas. Use numeric 0 literal.

## What This Skill Does NOT Cover

Include as placeholder rows or methodology notes:
- **Airfare:** Use City Pair YCA fares when origin/destination known; otherwise numeric 0 placeholder
- **Ground transportation:** Rental cars, mileage ($0.70/mile), taxi, rideshare
- **ODCs (LH):** Equipment, licenses, materials for LH contracts (user must provide; placeholders as numeric 0)
- **Subcontractor costs:** Requires separate estimate or vendor input
- **Fee/profit analysis:** This skill estimates costs, not negotiation targets
- **OCONUS travel:** Per diem covers CONUS only; State Dept rates for OCONUS
- **FFP contracts:** Use IGCE Builder FFP for wrap rate buildup
- **Cost-reimbursement:** Use IGCE Builder CR for CPFF/CPAF/CPIF
- **Grant budgets:** Use Grant Budget Builder

## Quick Start Examples

**Simple LH:** "Build an IGCE for a Systems Analyst in DC, base plus 2 option years" → map SOC 15-1211, pull DC BLS with percentiles, age via cell-referenced formula, apply 1.8x/2.0x/2.2x burden, validate against CALC+, 2.5% escalation, 6-sheet xlsx.

**T&M with materials:** "T&M IGCE for a 4-person dev team in DC, AWS hosting + JIRA licenses, base plus 3 OYs" → run full labor sequence plus Step 5B for materials, 7-sheet xlsx with materials separate from burden.

**SOW-driven:** "Here's my SOW, build me an IGCE" → run Step 0 decomposition, domain triage, Stage A/B validation, determine LH vs T&M based on materials need, then run appropriate workflow.

**24x7 coverage:** "SOC analyst coverage 24x7x365, Cleveland, base plus 2 OYs" → compute 4.2 FTE single-seat per Step 0.5, pull BLS Cleveland (0017410 post-2023 OMB renumbering), build workbook.


---

*MIT © James Jenrette / 1102tools. Source: github.com/1102tools/federal-contracting-skills*
