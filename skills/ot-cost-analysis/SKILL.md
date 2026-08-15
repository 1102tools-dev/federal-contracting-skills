---
name: ot-cost-analysis
description: >
  Build should-cost estimates and price reasonableness analyses for Other
  Transaction (OT) agreements under 10 USC 4021/4022. Produces milestone-
  based cost analysis workbooks with cost-sharing breakdowns, per-milestone
  funding profiles, and price reasonableness memos. Orchestrates BLS OEWS,
  GSA CALC+, and GSA Per Diem skills for labor benchmarking. Trigger for:
  OT cost analysis, OTA cost estimate, OT price reasonableness, prototype
  cost estimate, OT should-cost, OT milestone pricing, OT cost-sharing
  analysis, OT funding profile, prototype IGCE, 10 USC 4021 cost analysis,
  milestone payment schedule, build an OT cost analysis. Also trigger when
  user has an OT project description and needs cost analysis or a performer
  proposed price needing reasonableness assessment. Do NOT use for FAR IGCEs
  (use IGCE Builder FFP, LH/T&M, or CR), OT project descriptions (use OT
  Project Description Builder), or grant budgets (use Grant Budget Builder).
---

# OT Cost Analysis

## Overview

This skill produces should-cost estimates and price reasonableness analyses for OT agreements. Unlike FAR-based IGCEs that structure costs around contract type pricing mechanisms (wrap rates, burden multipliers, cost pools), OT cost analysis structures the estimate around milestones and cost-sharing arrangements. The performer proposes a price per milestone; the government's job is to determine whether that price is reasonable and how much of it the government pays vs. the performer.

**Why this is one skill, not three:** The existing IGCE builders (FFP, LH/T&M, CR) are split because each has a structurally different calculation engine -- FFP uses layered wrap rates, LH/T&M uses a single burden multiplier, CR uses cost pools plus three fee subtypes. OTs don't have that divergence. The pricing mechanism is consistently milestone-based: estimate should-cost per milestone, apply cost-sharing ratio, compare to proposed price. Fixed-price milestones vs. cost-type milestones change one column, not the engine. Cost-sharing is a ratio, not a multi-subtype fork.

**Required L1 skills (must be installed):**
1. **BLS OEWS API** -- market wage data for labor benchmarking
2. **GSA CALC+ Ceiling Rates API** -- market rate validation
3. **GSA Per Diem Rates API** -- federal travel rates

**Required API keys (must be in user memory):**
- BLS API key (v2) for BLS OEWS
- api.data.gov key for GSA Per Diem
- CALC+ requires no key

If a key is missing, prompt the user to register: BLS at https://data.bls.gov/registrationEngine/, api.data.gov at https://api.data.gov/signup/

**Statutory basis:** 10 USC 4021 (prototype project authority), 10 USC 4022 (OT authority, cost-sharing requirements, follow-on production). NOT FAR 15.404 -- OTs are outside the FAR. Price reasonableness for OTs is based on the agreements officer's judgment informed by market data, analogous pricing, and parametric analysis, not certified cost or pricing data.

## Workflow Selection

### Workflow A: Full OT Cost Analysis (Default)
User has a milestone table (from OT Project Description Builder or user-provided) and needs a complete should-cost estimate with cost-sharing and price reasonableness analysis. Execute Steps 1 through 9.
Triggers: "build the OT cost analysis," "price this OT," "estimate costs for this prototype," "milestone cost estimate."

**Pre-solicitation mode (Workflow A default when no performer price exists).** When the user has no proposed price yet, this is pre-solicitation should-cost, the most common first-pass use case. Run Workflow A but skip the variance/reasonableness comparison steps. The workbook becomes a government internal budget estimate. Set the Proposed Price column to blank (not "TBD" text; use an empty cell with conditional variance formulas `=IF(H[row]="","",H[row]-E[row])` so variance auto-populates when a price is later entered). State in methodology: "This is a pre-solicitation should-cost estimate; no performer price has been proposed. Variance formulas will activate when the Proposed Price column is populated." The Sheet 6 price reasonableness section becomes a "price reasonableness framework" rather than a determination.

### Workflow A+: From Concept (No Milestone Table)
User has a prototype concept but no structured milestone table. Execute Step 0 (milestone decomposition) first, validate, then Steps 1-9.
Triggers: "estimate costs for this prototype concept," "how much should this OT cost," or when the user provides a block of prototype description text rather than a milestone table.

### Workflow B: Price Reasonableness Check
User has a performer's proposed price and wants to assess reasonableness against a should-cost estimate.
Triggers: "is this OT price reasonable," "validate this proposed price," "check this prototype proposal," "price reasonableness for OT."

**Workflow B steps:**
1. Collect the performer's proposed price (total and/or per-milestone).
2. Run Steps 1-7 to build the government's independent should-cost estimate.
3. Compare proposed vs. should-cost per milestone and in total.
4. Position each milestone: below should-cost (aggressive), within 10% (competitive), 10-25% above (premium), above 25% (requires justification).
5. Produce the full workbook with emphasis on the price reasonableness memo (Sheet 6).

## Information to Collect

Ask for everything in a single pass. Provide defaults where noted.

### Required Inputs

| Input | Description | Example |
|-------|-------------|---------|
| Milestone table | Milestone IDs, descriptions, durations, deliverables, TRL | From OT Project Description Builder or user |
| Performer proposed price | Total and/or per-milestone | $2.4M total, or $300K/M1, $500K/M2, etc. |
| Performer type | NDC, traditional, small business, consortium | NDC startup |
| Performance location | City/state or metro area | San Diego, CA |
| Period of performance | Total and per-milestone/phase | 24 months total |

### Optional Inputs (Defaults Applied If Not Provided)

| Input | Default | Notes |
|-------|---------|-------|
| Cost-sharing ratio | 1/3 performer for traditional; 0% for NDC/SB | Per 10 USC 4022(d) path |
| Cost-sharing type | Cash | Cash or in-kind |
| Burden multiplier | 2.0x | For labor benchmarking; market context, not binding |
| Escalation rate | 2.5%/yr | Applied across milestone periods |
| Consortium management fee | 5% | Only if consortium-brokered |
| Travel destinations | None | City/state per destination |
| Travel frequency | None | Trips/year per destination |
| Travel duration | None | Nights per trip |
| Materials/hardware BOM | None | Categories and estimated costs per milestone |
| Labor categories | Derived from milestone scope | SOC codes for benchmarking |
| Staffing per milestone | Derived from scope and duration | FTEs or level of effort |
| FY for per diem | Current federal FY | Oct-Sep cycle |
| Milestone payment type | Fixed-price | Fixed-price, cost-type, or mixed |
| Analogous OT pricing | None | Prior OT awards for similar prototypes |

### Cost-Sharing Guidance

**Authority gate (check first).** 10 USC 4022(d) cost-sharing paths apply ONLY to prototype OTs issued under 10 USC 4022. They do NOT apply to:
- **10 USC 4021 research OTs.** No statutory cost-share trigger. Government funds 100% of allowable cost. State in methodology: "This agreement is issued under 10 USC 4021 research authority; 10 USC 4022(d) cost-sharing paths are statutorily inapplicable."
- **10 USC 4022(f) production follow-on OTs.** The follow-on inherits the path determination from the predecessor prototype agreement (e.g., if the prototype used path (D) competition commitment, the follow-on satisfies that path without re-triggering cost-share). Government funds 100% of production.

For prototype OTs under 10 USC 4022, cost-sharing requirements depend on the 10 USC 4022(d) eligibility path:

| Performer Type | Cost-Share Required? | Typical Arrangement |
|---------------|---------------------|---------------------|
| NDC (significant participation) | No | Government funds 100% |
| Small business (significant participation) | No | Government funds 100% |
| Traditional + NDC team | No (NDC participation satisfies) | Government funds 100% |
| Traditional, sole (no NDC/SB) | Yes, per 4022(d)(1)(C) | 1/3 performer typical |
| Traditional (competition commitment) | No, per 4022(d)(1)(D) | Government funds 100% but must compete follow-on |

"Significant participation" is not defined by statute. It is an agreements officer determination. Common thresholds: 33%+ of work, meaningful technical contribution (not just pass-through subcontracting).

If the user doesn't know the cost-sharing arrangement, ask the performer type and derive the requirement from the table above. Default to 1/3 performer cost share for traditional contractors without NDC/SB participation.

## Constants Reference

| Constant | Value | Source |
|----------|-------|--------|
| Standard work year | 2,080 hours | 40 hrs x 52 weeks; converts annual wages to hourly |
| Default productive hours | 1,880 hours/year | 2,080 minus holidays and avg leave |
| Default burden multiplier | 2.0x | Mid-range; for benchmarking only |
| Low scenario burden | 1.8x | Lower bound |
| High scenario burden | 2.2x | Upper bound |
| Default escalation rate | 2.5% annually | Standard federal assumption |
| BLS wage cap (annual) | $239,200 | OEWS reporting ceiling; reconfirm each release |
| BLS wage cap (hourly) | $115.00 | OEWS reporting ceiling; reconfirm each release |
| OEWS data year | 2025 | May 2025 estimates |
| GSA mileage rate | $0.70/mile | CY2025 GSA POV rate |
| First/last day M&IE | 75% of full day | FTR 301-11.101 |
| Default cost share (traditional) | 33% performer | Common OT practice per 4022(d)(1)(C) |
| Default consortium fee | 5% | Typical consortium management fee |

> **Verify the data vintage before pricing.** OEWS publishes annually in spring, and BLS
> withdraws the prior year when the new one lands. Call `detect_latest_year()` first and use
> what it returns as the vintage for the aging factor. If the vintage in the table above is
> older than that, the aging factor over-escalates every labor line. Do not age 2025 wages
> from a 2024 vintage.


## Orchestration Sequence

### Step 0: Milestone Decomposition (Workflow A+ Only)

Converts an unstructured prototype concept into a milestone table suitable for cost analysis.

**Process:**
1. **Sufficiency check.** Scan for: prototype objective, technology area, TRL indicators, schedule, deliverables, performer information. Flag anything missing. Hard stop if prototype objective is absent.

2. **Performer location gate.** Labor benchmarking is entirely location-driven. If the user has not stated a performer location (MSA, city/state, or "national"), ASK before proceeding. If the user says "unknown performer" or "location TBD," either pick one defensible default based on the scope (e.g., Huntsville for Army ground systems, Arlington for DC-area software, Dayton for AFRL-adjacent) AND FLAG THE CHOICE, or default to "national" scope and note that metro adjustment may change rates 15-30%. Do not silently infer.

3. **TRL mapping (inline reference; do not depend on other skills being loaded):**

| TRL | Description | Typical phase |
|-----|-------------|---------------|
| 1-2 | Basic principles / concept formulated | Research OT (4021) |
| 3 | Analytical and experimental proof of concept | Early prototype |
| 4 | Component validation in lab | Prototype: design/build |
| 5 | Component validation in relevant environment | Prototype: build/test |
| 6 | System demo in relevant environment | Prototype: test/demo |
| 7 | System prototype demo in operational environment | Late prototype / pre-production |
| 8-9 | System complete and qualified / proven in operational use | Production (4022(f)) |

4. **Milestone derivation (inline heuristic):**
   - TRL 2 → 3: theoretical refinement, initial experimentation
   - TRL 3 → 4: PDR, detailed design, benchtop validation
   - TRL 4 → 5: prototype build, component test, subsystem integration
   - TRL 5 → 6: system integration, relevant-environment demo
   - TRL 6 → 7: operational-environment demo, production readiness review
   - TRL 7 → 9: production (LRIP lots, first-article qual, full-rate production)

5. **Present milestone table** for user validation:
```
Milestone | Phase | Description                  | Est. Duration | TRL In/Out | Payment Type
M1        | 1     | Preliminary Design Review    | 3 months      | 3/4        | Fixed
M2        | 2     | Prototype Build Complete     | 4 months      | 4/5        | Fixed
M3        | 3     | System Demonstration         | 3 months      | 5/6        | Fixed
```

5. **User validation gate.** Confirm before proceeding to Step 1.

### Step 1: Validate Milestone Structure

Before costing, verify the milestone table is internally consistent:

- TRL progression has no gaps (each milestone's exit TRL equals the next milestone's entry TRL or is within the same phase)
- Total duration of milestones sums to within 10% of stated total PoP (if not, apply the Step 6 duration-vs-PoP reconciliation rule)
- Each milestone has at least one deliverable
- Each milestone has a payment type (fixed or cost-type) tagged in the Payment Type column
- No single milestone exceeds 40% of total estimated value. If any does, recommend splitting into two milestones (one pre-gate, one post-gate). If the user declines the split, flag as intentional front-loading in methodology and require a written basis in the agreement file.

Flag any issues for user resolution before proceeding.

### Step 2: Labor Benchmarking

**Use the BLS OEWS API skill.** OT labor benchmarking serves a different purpose than FAR IGCE labor pricing. In a FAR IGCE, BLS wages are the basis for the government's cost estimate. In an OT cost analysis, BLS wages provide market context for evaluating whether the performer's proposed staffing costs are reasonable. The government is not setting rates; it is checking whether proposed rates are within market range.

**Step 2a: Map labor categories to SOC codes.** Use the expanded mapping table below. If the milestone table includes labor categories, map those. If not, infer from milestone scope.

**Common role to SOC mapping (inline reference; do not assume the IGCE Builder skills are loaded):**

| Role family | SOC | Notes |
|-------------|-----|-------|
| Systems engineer | 17-2199 | Engineers, all other |
| Software developer | 15-1252 | |
| Software QA / test | 15-1253 | |
| Mechanical engineer | 17-2141 | |
| Electrical engineer | 17-2071 | |
| Aerospace engineer | 17-2011 | |
| Materials engineer | 17-2131 | |
| Industrial engineer | 17-2112 | |
| Electronics engineer | 17-2072 | |
| Program manager | 13-1082 | |
| Principal investigator (industrial) | 15-1221 or 15-2051 | Research scientist; use 15-2051 for data/ML-centric PI |
| Autonomy / ML / RL engineer | 15-2051 | Data Scientist is the closest SOC proxy; document in methodology |
| Robotics / mechatronics engineer | 17-2199 | Engineers, all other; no dedicated SOC |
| Acoustics / sonar engineer | 17-2199 | Engineers, all other |
| Cybersecurity engineer | 15-1212 | Information Security Analyst |
| Manufacturing engineer (production OTs) | 17-2112 | Industrial Engineer |
| Quality engineer (production OTs) | 17-2112 | Industrial Engineer (QA specialty) |
| Production technician | 17-3029 | Engineering technicians, other |
| Test engineer | 17-2199 or 17-3029 | Engineer vs technician level |
| Logistics manager (production OTs) | 13-1081 | |
| **Academic / FFRDC / UARC performers:** | | Use the academic branch below |
| Senior research scientist (PI) | 19-1021 or 25-1032 | Biological/physical scientist, or postsecondary engineering teacher for university-affiliated PIs |
| Postdoctoral researcher | 19-1099 | Life, physical, and social scientists, all other |
| Graduate research assistant | Not a BLS SOC | University institutional rate applies (tuition remission + stipend); typically $55-75/hr loaded; do NOT derive from BLS 25-9044 teaching assistant wages, which understate actual billing rate |
| Lab technician | 17-3023 | Electrical and electronics engineering technicians |

For AI/autonomy/robotics roles not in BLS, document the proxy choice in methodology and note that defense-specialty premiums may push actual rates 20-30% above BLS medians (consider P75 as practical floor).

**Milestone-type to labor inference (use when user provides only milestone descriptions):**

| Milestone type | Typical labor |
|----------------|---------------|
| Design phase | Systems engineer, software architect, mechanical engineer |
| Build / fabrication | Software developer, hardware engineer, technician |
| Component or lab test | Test engineer, QA analyst, data analyst |
| Integration | Systems integrator, middleware engineer, DevOps |
| Demonstration | Test engineer, systems engineer + travel team |
| Project oversight | Program manager, principal investigator |
| Production LRIP (4022(f)) | Manufacturing engineer, quality engineer, production technician, test engineer, logistics manager |
| Research (4021) | PI, postdoc, grad RA, lab technician |

**Step 2b: Pull BLS wages.** For each labor category, query BLS OEWS at the performance location. Use metro-level prefix (OEUM) when available. If the MSA returns no data (small metro suppression), fall back to state-level (OEUS), then national (OEUN). Document the fallback in the methodology: "BLS OEWS data for [MSA] was suppressed for [SOC codes]. [State/National] median used as benchmark." Use median (50th percentile) as the default benchmarking basis.

**Step 2c: Age wages.** Same aging methodology as IGCE builders:
```
months_gap = months between BLS data vintage (May 2025) and agreement start
aging_factor = (1 + escalation_rate) ^ (months_gap / 12)
aged_wage = annual_median * aging_factor
```

**Step 2d: Apply burden multiplier.** Convert to burdened rates for benchmarking:
```
hourly_base    = aged_wage / 2080        # paid hours: the denominator for deriving an hourly rate from an annual salary
burdened_rate  = hourly_base * burden_multiplier
```

**Paid hours (2080) vs. productive hours (1880) rule.** The 2080 figure in the rate derivation is the denominator for converting an annual salary to an hourly rate. It is NOT the effort hours per FTE. Effort hours per FTE-year are 1880 (2080 minus holidays and average leave). The 200-hour gap is absorbed in the burden multiplier (idle-paid overhead). Do NOT apply 1880 both as the rate denominator and the effort multiplier; that double-counts the leave/holiday burden.

**Multi-location performers.** If prime and subcontractor (or multiple work sites) sit in different MSAs, pull BLS separately for each MSA and tag every labor row with its MSA in the workbook. Do NOT average MSA rates. Query each MSA through BLS, document the SOC and MSA used per role, and carry a "Location" column into Sheet 4 Labor Benchmarking and Sheet 2 Milestone Detail.

**Important caveat for OTs:** Document in the methodology that BLS wages and burden multipliers are market benchmarks, not the pricing basis. OT performers -- especially NDCs -- may have cost structures that differ significantly from traditional defense contractors. A startup may have low overhead but high equity-based compensation. A university lab may have high fringe but no profit margin. The burden multiplier is a sanity-check tool, not an audit standard. OTs do not require DCAA-auditable indirect rates.

**Academic / FFRDC / UARC / university-affiliated performer branch.** Research OTs under 4021 are frequently performed by universities, FFRDCs (MIT Lincoln Lab, MITRE, SEIs, national labs), and UARCs (APL, GTRI). Their cost structures differ from industrial defense contractors. When the performer is one of these:
- **Burden scenarios shift.** Use 1.65 / 1.85 / 2.05 instead of 1.8 / 2.0 / 2.2 to reflect F&A (facilities and administrative) rate + fringe structure typical of on-campus research. Document as "academic/research-institute burden; see institutional NICRA if provided."
- **Grad research assistants and postdocs** are priced at institutional billing rates, not BLS wages. Grad RAs typically load at $55-75/hr (stipend + tuition remission + fringe). Postdocs at $80-110/hr. Use the user-provided institutional rate if available; otherwise note the assumption and flag for validation.
- **Institutional overhead vs. industrial wrap.** F&A is a federal negotiated rate (often 50-60% on-campus, 25-30% off-campus) applied to modified total direct costs. This is not the same as the industrial burden multiplier and should be documented as such in methodology.

**Production follow-on (4022(f)) branch.** For production OTs under 4022(f), labor shifts from R&D/engineering to manufacturing, materials dominate, and the time horizon typically crosses multiple fiscal years.
- **Labor mix** per the SOC table above: manufacturing engineer, quality engineer, production technician, test engineer, logistics manager. PI and research staff are absent.
- **Unit economics matter.** Per-unit cost (total should-cost / unit count) and learning curve are load-bearing. Expect per-unit cost to drop across lots (typical 85-90% learning curve for hardware LRIP). Flag a flat per-unit cost across lots as unrealistic.
- **FY obligation profile.** If PoP crosses more than one federal fiscal year (Oct 1 - Sep 30), Sheet 5 must include an FY-by-FY obligation table in addition to the cumulative profile. This is the document the PEM/budget officer consumes. **Default convention: obligate-at-start.** Map each milestone's START-date month to the FY it falls in and assign the full milestone government obligation to that FY. Rationale: cost-type milestones obligate at kickoff (funds committed when work begins), and fixed-price milestones are typically obligated at award or milestone kickoff under OT agreements, not at completion. Document the convention explicitly in methodology. If the user prefers obligate-at-completion, that can be stated as an override and the mapping recomputed; do not silently pick either convention.

- **Learning curve for LRIP production.** For multi-lot production OTs (2+ lots of 6+ units each), apply a default learning-curve multiplier to the BOM line of each lot beyond Lot 1: `lot_BOM = base_BOM × 0.95^(lot_index - 1) × (1 + B9_materials_escalation)^(years_from_PoP_start)`. The 95% (Crawford model) is a conservative default; aerospace and electronics LRIP run 85-92%, simple assembly 95-98%. State the applied curve in methodology and flag if the performer's proposed price shows FLAT per-unit cost across lots (unrealistic) or INCREASING per-unit cost (escalation compounding without learning; signals either escalation is too high or learning is not being captured). Per-unit cost should decline across lots even after escalation.
- **Path determination inherits from predecessor; cost-share ratio does NOT propagate.** Production follow-on under 4022(f) inherits the authorization basis from the prototype (e.g., if the prototype used path (D) competition commitment, the follow-on is authorized under that path). The follow-on itself does not re-trigger 4022(d) analysis. **However, the cost-share ratio does not carry over to production.** Production government obligation = 100% per the Authority Gate, regardless of what cost-share ratio applied to the predecessor prototype. If the prototype was path (C) with 1/3 performer share, the production follow-on still has $B$7 = 0. State this explicitly in methodology to avoid confusion: "Predecessor prototype used 10 USC 4022(d)(1)([X]) with [Y]% performer cost share. Production follow-on under 10 USC 4022(f) inherits the path determination but not the cost-share ratio; government funds 100% of production."

### Step 3: Cross-Reference Against CALC+

**Use the GSA CALC+ Ceiling Rates API skill.** Same methodology as IGCE builders. Call the MCP with `page_size=1` (the MCP rejects `page_size=0`; you only need the aggregations block, not per-result rows). Read from `histogram_percentiles`, NOT `wage_percentiles`:

```python
aggs = response_json["aggregations"]
median   = aggs["histogram_percentiles"]["values"]["50.0"]
p25      = aggs["histogram_percentiles"]["values"]["25.0"]
p75      = aggs["histogram_percentiles"]["values"]["75.0"]
```

Compare BLS burdened rate to CALC+ median. Flag divergence >25% in methodology with remediation: for NDC performers keep BLS as primary (CALC+ reflects GSA MAS ceilings that NDCs are not bound by); for traditional primes widen the burden scenario to capture the gap. Never silently adjust a rate. CALC+ empty results for a role (0 hits): try one broader keyword (e.g., "software" instead of "ML"); if still empty, mark "No CALC+ data, BLS only" in methodology and do not flag divergence for that role.

### Step 4: Materials and Hardware Estimation

For prototype OTs, materials and hardware are often the dominant cost element (40-70% for hardware prototypes). This is a first-class estimation step, not an afterthought.

**If user provides a BOM or materials list:**
- Create rows per materials category per milestone
- Apply escalation across milestones if multi-year
- Materials are at cost (no burden applied)

**If user provides milestone scope but no materials specifics:**
Estimate materials using prototype-type heuristics:

| Prototype Type | Materials as % of Total | Common Categories |
|---------------|------------------------|-------------------|
| Software only | 10-20% | Cloud hosting, licenses, test infrastructure |
| Software + hardware integration | 20-40% | Components, test equipment, cloud, licenses |
| Hardware prototype (single unit) | 40-60% | Raw materials, components, fabrication, test equipment |
| Hardware prototype (multiple units) | 50-70% | All above, scaled by unit count |
| Process/workflow prototype | 5-15% | Software tools, test environments |

Present the estimated materials breakdown for user validation. Mark as "estimated from prototype-type heuristic; refine with performer input" in methodology.

**If user says materials exist but has no estimates:** Include placeholder rows with "TBD" per milestone. Note that cost analysis is incomplete without materials estimates for hardware prototypes.

### Step 5: Travel Estimation (If Applicable)

**Use the GSA Per Diem Rates API skill.** Same methodology as IGCE builders.

**FY fallback rule.** GSA typically publishes each new FY's per diem rates in August of the preceding FY. If the OT's PoP starts in a fiscal year whose rates have not yet been published (MCP returns empty or error for target FY), fall back to the most recently published FY. Document the substitution explicitly in Sheet 6 methodology Section 7: "GSA per diem for FY[target] not yet published at analysis date; rates drawn from FY[fallback] and marked for refresh when new FY rates are released." Do not silently query the wrong year.

OT travel is typically lighter than traditional contract travel but may include:
- Technical interchange meetings (performer site to government site)
- Test events (travel to government test ranges or facilities)
- Demonstrations (travel to operational environments)
- Program reviews

Allocate travel costs to specific milestones rather than spreading evenly across the PoP. Test milestones typically have higher travel costs than design milestones.

### Step 6: Should-Cost Buildup per Milestone

Build the government's independent should-cost estimate for each milestone:

```
milestone_labor = sum(burdened_rate * hours_per_category) for each labor category in that milestone
milestone_materials = sum(materials_costs) allocated to that milestone
milestone_travel = travel_costs allocated to that milestone
milestone_odcs = other direct costs allocated to that milestone

milestone_should_cost = milestone_labor + milestone_materials + milestone_travel + milestone_odcs
```

**Labor cost method: per-category is canonical.** Build labor cost per milestone by summing individual category lines, not by applying a single blended rate:
```
# For each labor category present in the milestone:
category_hours  = 1880 * (milestone_duration_months / 12) * FTE_for_category
category_cost   = category_hours * burdened_rate_for_category

milestone_labor = sum(category_cost) across all categories in that milestone
```

A blended rate (weighted-average burdened rate across the staffing mix) is acceptable only as a quick pre-solicitation approximation when no milestone-level staffing detail exists, and it must be disclosed in methodology. For any real workbook, use the per-category method so users can adjust individual FTE allocations and see the dollar impact.

**Labor cost cell formula (for the workbook).** Per-category labor cells must be Excel formulas so changes to burden multiplier, FTE, or duration cascade:
```
labor_cell = FTE * (Duration_months / 12) * Productive_Hours * Burdened_Rate_Ref
```
where Productive_Hours references the assumption cell ($B$6) and Burdened_Rate_Ref points to the Sheet 4 Labor Benchmarking row for that category. Sheet 4 holds burdened rates as the single source of truth; Sheet 2 references Sheet 4. Never hardcode a rate into a Sheet 2 labor cell.

**Milestone duration vs. PoP reconciliation.** If milestone durations sum to a value more than 10% different from the stated total PoP: default to scaling labor to the PoP (continuous staffing model; labor FTE_months = PoP_months × peak_FTE × ramp_factor). Flag the gap in methodology and note that if the user intends the difference as unstaffed gaps, the workbook can be rebuilt with milestone-duration labor only (which produces a materially lower should-cost). Do not silently pick either interpretation; state the one applied.

**Multi-performer structures (prime + subcontractor).** When a traditional prime carries an NDC subcontractor at significant participation (path (A) satisfied via sub), the workbook treats each performer as a labor block within each milestone. Sheet 2 per-milestone labor rows get a "Side" column tagging Prime vs. NDC Sub (or Sub-1, Sub-2 for multi-sub structures). Rate benchmarking is per-performer: prime labor benchmarked against prime's MSA, sub labor against sub's MSA. Sheet 1 adds a Performer Structure block below the assumption block documenting: prime name, sub name(s), sub work-share percentage, and the 4022(d) path claimed. Work-share percentage is what the agreements officer uses to justify the "significant participation" determination; carry it in the methodology memo.

If the user provides per-milestone staffing, use it directly. If not, derive from scope heuristics:

| Milestone Type | Typical Team Size | Notes |
|---------------|------------------|-------|
| Design review | 2-4 engineers + 1 PM | Shorter duration, intensive effort |
| Build/fabrication | 3-8 engineers + 1-2 techs + 1 PM | Depends on complexity |
| Component test | 2-4 test engineers + 1-2 subject matter experts | May overlap with build |
| System integration | 3-6 engineers + 1 PM | Cross-discipline team |
| System demonstration | 2-4 engineers + 1 PM + travel team | Often shorter but high-tempo |

Present the per-milestone should-cost breakdown for user review before applying cost-sharing.

### Step 7: Cost-Sharing Calculation

Apply cost-sharing based on the performer type and arrangement:

**No cost share (NDC/SB participation or competition commitment path):**
```
government_obligation = milestone_should_cost
performer_share = $0
```

**Cost share required (traditional, sole, no NDC/SB):**
```
performer_share = milestone_should_cost * cost_share_ratio    # default 0.33
government_obligation = milestone_should_cost * (1 - cost_share_ratio)
```

**In-kind cost share:**
```
# In-kind means performer contributes resources not charged to the agreement
# The agreement value reflects only the government's obligation
# Document the in-kind contribution description but don't subtract from should-cost
government_obligation = milestone_should_cost * (1 - cost_share_ratio)
in_kind_value = milestone_should_cost * cost_share_ratio
# Note: in-kind requires the performer to track and report their contribution
```

**Consortium-brokered OT:**
```
consortium_fee = milestone_should_cost * consortium_fee_rate    # default 0.05
government_obligation = (milestone_should_cost * (1 - cost_share_ratio)) + consortium_fee
```

**Cumulative funding profile:** Sum government obligations across milestones in chronological order. This is the government's funding requirement, showing when money needs to be available.

### Step 8: Scenario Analysis

Three scenarios varying labor burden and materials estimates:

```
low_should_cost  = labor_at_low_burden + materials_low + travel + odcs
mid_should_cost  = labor_at_mid_burden + materials_mid + travel + odcs
high_should_cost = labor_at_high_burden + materials_high + travel + odcs
```

**Scenario multipliers:**

| Component | Low | Mid | High |
|-----------|-----|-----|------|
| Labor burden | 1.8x | 2.0x | 2.2x |
| Materials | Estimate * 0.85 | Estimate * 1.0 | Estimate * 1.20 |
| Travel | Same across scenarios | Same | Same |

Materials variance is wider for hardware prototypes (fabrication uncertainty) and narrower for software (cloud costs are more predictable). Adjust the multiplier if the user specifies prototype type.

Apply cost-sharing to each scenario:
```
low_govt_obligation  = low_should_cost * (1 - cost_share_ratio)
mid_govt_obligation  = mid_should_cost * (1 - cost_share_ratio)
high_govt_obligation = high_should_cost * (1 - cost_share_ratio)
```

Add consortium fees if applicable.

### Step 9: Produce the OT Cost Analysis Workbook

Generate a multi-sheet .xlsx workbook using openpyxl. Run the recalc script (`python /mnt/skills/public/xlsx/scripts/recalc.py <file>`) before presenting if available; otherwise use openpyxl's calculation capabilities.

**CRITICAL: ALL calculated cells MUST use Excel formula strings, not Python-computed values.** Write `ws.cell(row=r, column=c, value='=H11-E11')`, NOT `ws.cell(row=r, column=c, value=121675)`. The entire point of the assumption block is that changing a blue-font input (burden multiplier, cost-share ratio, escalation rate) recalculates every dependent cell in the workbook. A workbook with hard-coded values is useless as an analytical tool because the user cannot adjust assumptions. This applies to: all cost subtotals (SUM formulas), all cost-sharing calculations (reference $B$7), all variance calculations (reference Proposed - Should-Cost), all scenario calculations (reference $B$2/$B$3/$B$4), all cumulative funding profile cells (running SUM), and all labor cost cells (rate * hours). The only cells that should contain literal numbers are: blue-font assumption inputs (rows 2-8), text labels, milestone durations, FTE counts, BLS wage data, CALC+ data, and per diem rates.

**Workbook structure (7 sheets):**

**Sheet 1: Cost Analysis Summary.** Milestones as rows. Columns: Phase, Duration, Should-Cost (Mid), Government Share, Performer Share, Proposed Price, Variance ($), Variance (%).

**Assumption cell layout (Sheet 1, rows 1-12).** Cell references are inlined in the label text so the model building the workbook cannot confuse row position with cell address:

```
Row 1:  A1 "OT Cost Analysis Assumptions" (bold, merged A1:B1)
Row 2:  A2 "Burden Multiplier Low [$B$2]"           B2: 1.8   (blue)
Row 3:  A3 "Burden Multiplier Mid [$B$3]"           B3: 2.0   (blue)
Row 4:  A4 "Burden Multiplier High [$B$4]"          B4: 2.2   (blue)
Row 5:  A5 "Labor Escalation Rate [$B$5]"           B5: 0.025 (blue, %)
Row 6:  A6 "Productive Hours/Year [$B$6]"           B6: 1880  (blue)
Row 7:  A7 "Cost-Share Ratio Performer [$B$7]"      B7: 0.00  (blue, %; 0 if no share)
Row 8:  A8 "Consortium Fee Rate [$B$8]"             B8: 0.00  (blue, %; 0 if direct)
Row 9:  A9 "Materials Escalation Rate [$B$9]"       B9: 0.025 (blue, %; defense-electronics often 3-5%)
Row 10: A10 "Cost-Type Ceiling Margin [$B$10]"      B10: 0.15 (blue, %; applies only to cost-type milestones)
Row 11: (blank row separator)
Row 12: header row for milestone data
```

All formulas reference these cells. Changing any assumption recalculates the entire workbook. Freeze panes below row 11.

**Materials escalation is separated from labor escalation** because BOM escalation rates differ structurally from wage escalation. Defense electronics BOMs have run 3-5%+ while labor escalation has been 2-3%. For a materials-dominant estimate, a single-knob escalation misstates the answer.

**Materials escalation time-basis (required prescription).** Compound materials escalation per milestone using milestone-start month from PoP start, not per calendar year. Formula: `escalated_materials = base_materials × (1 + $B$9)^(months_from_PoP_start_to_milestone_start / 12)`. Labor escalation uses the same month-based compounding from the BLS data vintage date. Do not mix year-boundary escalation with month-based escalation across the workbook; pick one and state in methodology. The month-based approach is the default because milestones rarely start on FY boundaries.

**Summary table layout (starting row 12):**
```
Columns: A=Milestone ID | B=Phase | C=Description | D=Duration (mo) | E=Payment Type | F=Should-Cost (Mid) | G=Ceiling (Cost-Type only) | H=Govt Obligation | I=Performer Share | J=Proposed Price | K=Variance ($) | L=Variance (%)

Payment Type (E): "Fixed" or "Cost-Type" per milestone (blue font, user-editable)
Ceiling (G): =IF(E[row]="Cost-Type", F[row]*(1+$B$10), "")
Govt Obligation (H): =IF(E[row]="Cost-Type", F[row]*(1+$B$10)*(1-$B$7), F[row]*(1-$B$7))
Performer Share (I): =IF(E[row]="Cost-Type", F[row]*(1+$B$10)*$B$7, F[row]*$B$7)
Variance ($) (K): =IF(J[row]="","",J[row]-F[row])
Variance (%) (L): =IF(OR(J[row]="",F[row]=0),"",(J[row]-F[row])/F[row])

Totals row at bottom with SUM formulas for F through K.
```

**Critical: Performer Share must branch on Payment Type.** For cost-type milestones, the performer's share of financial exposure is against the ceiling, not against should-cost. If Performer Share uses `F*$B$7` while Govt Obligation uses `F*(1+$B$10)*(1-$B$7)` for cost-type, Sheet 1 totals will not reconcile with Sheet 5 cost-sharing detail, and the cost-share ratio documented in methodology will be wrong. Both H and I columns use the same IF branch.

**Payment type rule.** For cost-type milestones, the government obligates at ceiling (should-cost × (1 + ceiling margin)), not at should-cost. The performer reports actuals against ceiling; any overrun past ceiling is the performer's exposure unless the agreement is modified. The funding profile on Sheet 5 MUST use ceiling for cost-type milestones so the FY obligation numbers reflect the maximum government exposure, not the optimistic estimate.

**Sheet 2: Milestone Detail.** One block per milestone showing the cost element breakdown.

**Deterministic block placement (required).** Variable labor category counts make fixed per-milestone block heights unreliable. Before writing any cross-sheet reference, compute each milestone's block size dynamically: `block_height = 6 (metadata + labor header/subtotal) + labor_rows + 3 (materials header/subtotal/blank) + materials_rows + 3 (travel) + travel_rows + 3 (ODC) + odc_rows + 4 (totals). Store each milestone's start_row and subtotal_row positions in a dict before writing Sheet 1 and Sheet 3 references. The alternative is to name each milestone's key cells (Should-Cost, Govt Obligation, Performer Share) with Excel defined names (e.g., `M1_should_cost`, `M1_ceiling`, `M1_govt_oblig`) and reference by name rather than by row number. Either approach works; what does NOT work is assuming a fixed row spacing.

```
"Milestone [ID]: [Description]"                               (bold header)
A="Duration"                  B=[months]                      (blue font)
A="TRL Entry/Exit"            B=[X/Y]

A="LABOR"                                                     (bold subheader)
  [Labor category]            [Hours]   [Rate]   [Cost]       (formula rows)
  Labor Subtotal                                  [SUM]        (formula)

A="MATERIALS"                                                  (bold subheader)
  [Materials category]                            [Cost]       (blue font or formula)
  Materials Subtotal                              [SUM]        (formula)

A="TRAVEL"                                                     (bold subheader)
  [Destination]                                   [Cost]       (formula ref to Sheet 5 if applicable)
  Travel Subtotal                                 [SUM]        (formula)

A="ODCs"                                                       (bold subheader)
  [ODC category]                                  [Cost]       (blue font)
  ODC Subtotal                                    [SUM]        (formula)

A="MILESTONE SHOULD-COST"     B==labor+materials+travel+odcs   (formula, bold)
A="Government Share"          B==should_cost*(1-$B$7)          (formula)
A="Performer Share"           B==should_cost*$B$7              (formula)
A="Consortium Fee"            B==should_cost*$B$8              (formula; $0 if direct)
A="Total Govt Obligation"     B==govt_share+consortium_fee     (formula, bold)
```

For cost-type milestones, add a "Ceiling" column next to Should-Cost. For fixed-price milestones, the should-cost is the benchmark against the fixed payment.

**Sheet 3: Scenario Analysis.** Three columns (low/mid/high) for total should-cost. Apply cost-sharing to each scenario. Summary: "Government obligation range: $X (low) to $Y (high), Mid estimate: $Z."

Per-milestone scenario rows if milestone count is small enough (10 or fewer). Otherwise, summary level only.

**Sheet 4: Labor Benchmarking.** BLS burdened rate (mid), CALC+ 25th/50th/75th percentiles, min/max range, divergence percentage. Include caveat row: "OT labor benchmarks are market context for price reasonableness, not binding pricing constraints. NDC and non-traditional performers may have different cost structures."

**Sheet 5: Cost-Sharing Detail.** Per-milestone breakdown:
```
Columns: Milestone ID | Should-Cost | Govt Share ($) | Govt Share (%) | Performer Share ($) | Performer Share (%) | Consortium Fee | Total Govt Obligation

Cumulative row: running total of government obligations across milestones (funding profile)
```

Cash vs. in-kind distinction if applicable.

**Sheet 6: Methodology / Price Reasonableness Memo.**

This is the narrative document for the agreement file. Structure:

1. **Authority and Basis.** "This cost analysis supports a price reasonableness determination for an Other Transaction agreement under 10 USC 4021. OT agreements are outside the Federal Acquisition Regulation; price reasonableness is determined by the Agreements Officer's judgment based on market data, analogous pricing, and independent cost analysis. This analysis does not constitute a FAR 15.404 cost or price analysis."

2. **Methodology.** Describe the should-cost buildup approach: labor benchmarking (BLS OEWS + CALC+ market data), materials estimation, travel costs, milestone structure.

3. **Labor Benchmarking Basis.** BLS data vintage, CALC+ query date, performance location, burden multiplier rationale. Note that BLS/CALC+ data reflects traditional contractor market rates; NDC performers may price differently.

4. **Materials Basis.** Source of materials estimates (BOM, performer input, heuristic), escalation applied, major cost drivers.

5. **Cost-Sharing Analysis.** 10 USC 4022(d) eligibility path, cost-sharing ratio, cash vs. in-kind, per-milestone distribution.

6. **Price Reasonableness Determination.** Compare proposed price to should-cost estimate:
   - Per-milestone variance analysis
   - Position within scenario range (below low = aggressive, within low-mid = competitive, within mid-high = premium, above high = requires additional justification)
   - Overall assessment: "The proposed price of $X falls [within/above/below] the government's should-cost estimate range of $Y (low) to $Z (high), with a mid-point of $W. The proposed price represents a [X%] variance from the mid-point estimate."

7. **Data Sources.** BLS series IDs, CALC+ keywords, per diem FY, any analogous pricing sources.

8. **Exclusions and Limitations.** What is not included, caveats about non-traditional cost structures, areas where the estimate could be refined with additional performer data.

**Sheet 7: Raw Data.** All API query parameters and responses: BLS series IDs, CALC+ keywords and record counts, per diem query details.

**Formatting standards (same as IGCE builders):**
- Blue font (RGB 0,0,255) for all user-adjustable inputs and assumptions
- Black font for all formula cells
- Currency: $#,##0 with negatives in parentheses
- Percentage: 0.0%
- Bold headers with light gray fill
- Freeze panes below assumptions block on Sheet 1 (below row 9)
- Auto-size column widths

Never output as .md or HTML unless explicitly requested.

## Edge Cases

**No performer proposed price yet (pre-solicitation):** Produce should-cost estimate only. The workbook becomes a government internal estimate for budget planning. Set Proposed Price column to "TBD." Variance columns MUST use conditional formulas, not static "N/A" text: `=IF(J[row]="TBD","",J[row]-E[row])` for dollar variance, `=IF(J[row]="TBD","",IF(E[row]>0,(J[row]-E[row])/E[row],0))` for percentage. This way, when the user later enters a proposed price in column J, the variance auto-calculates without editing formulas. Note in methodology that this is a pre-solicitation estimate and instruct the user to enter the proposed price in the Proposed column when available.

**Performer provides total price but not per-milestone breakdown:** Allocate the proposed total across milestones proportionally to the should-cost estimate (each milestone's share of proposed = proposed_total * (milestone_should_cost / total_should_cost)). Document this in the methodology: "The performer's proposed total of $X was allocated across milestones in proportion to the government's should-cost estimate. Per-milestone proposed pricing was not provided. This allocation is an analytical assumption; actual milestone payments may differ." Flag this as a limitation in Sheet 6 Section 8 (Exclusions). If the proportional allocation produces per-milestone variances that are uniformly identical (all milestones show the same % variance), note that this is an artifact of the allocation method, not evidence that every milestone is equally over/under-priced.

**Performer is an NDC with no historical pricing:** BLS/CALC+ benchmarks are the primary tool. Note in methodology that NDC cost structures may differ from market data. If the performer provides a cost breakdown with their proposal, use it alongside market benchmarks.

**Materials dominate the estimate (hardware prototype):** If materials exceed 60% of should-cost, flag that the labor benchmarking has limited influence on the total. Price reasonableness for hardware prototypes often relies on BOM validation and vendor quotes more than labor rate analysis.

**Cost-type milestones:** Add a ceiling column to the milestone detail. The should-cost is the estimated cost; the ceiling is typically should-cost plus a contingency margin (10-20%). Note in methodology that cost-type milestones require the performer to track and report actual costs.

**Consortium-brokered OT:** Add consortium management fee (default 5%) to government obligation. The fee is on top of the performer's cost, not deducted from it. Some consortiums charge a flat fee instead of a percentage; handle as a fixed cost per milestone or as a one-time upfront fee.

**Multiple performers (competitive prototype):** If the government is funding 2-3 performers to compete on the same prototype, the cost analysis may need to be run per performer. Each gets its own workbook. Note the total program cost = sum of all performer obligations.

**Analogous pricing available:** If the user provides prior OT awards for similar prototypes (from USASpending or internal records), add an analogous pricing comparison in Sheet 6. This strengthens the price reasonableness narrative.

**BLS wage at reporting cap:** Same handling as IGCE builders -- use $239,200/$115.00 as lower bound, flag in methodology.

**No CALC+ results:** Same handling as IGCE builders -- try broader keywords, note unavailable, mark "No CALC+ data."

## What This Skill Does NOT Cover

Include as placeholder rows or methodology notes:
- **OT project description** -- use OT Project Description Builder
- **Traditional FAR IGCEs** -- use IGCE Builder (FFP, LH/T&M, CR)
- **Agreement terms and conditions** -- legal review required
- **NDC eligibility determination** -- agreements officer determination per 10 USC 3014
- **DCAA audit or indirect rate validation** -- not applicable to OTs with NDC performers
- **Production follow-on under FAR contract** -- only if the follow-on is issued as a FAR-based production contract rather than an OT, use the appropriate IGCE Builder. Production follow-on OTs under 10 USC 4022(f) ARE in scope for this skill (they are issued as OTs, not FAR contracts, and inherit the cost-share determination from the predecessor prototype agreement)
- **Subcontractor cost analysis** -- requires separate estimate or sub-tier cost data
- **OCONUS travel** -- per diem covers CONUS only; State Dept rates for OCONUS
- **Grant budgets** -- use Grant Budget Builder

## Quick Start Examples

**From milestone table:** "Build the OT cost analysis" (after running OT Project Description Builder)
Claude will: consume the milestone handoff table, collect proposed price, benchmark labor, estimate materials, apply cost-sharing, produce 7-sheet workbook.

**From concept:** "How much should a TRL 4-6 cyber prototype cost in DC, 18 months, small team?"
Claude will: Workflow A+. Decompose into milestones, benchmark labor (cybersecurity SOC codes), estimate materials (software-dominant), produce should-cost estimate. No proposed price comparison unless provided.

**Price reasonableness:** "Performer proposes $3.2M for a 5-milestone prototype. Reasonable?"
Claude will: Workflow B. Collect milestone details, build should-cost, compare per-milestone and total, produce price reasonableness memo.

**Cost-sharing analysis:** "Traditional prime, no NDC or SB, prototype OT in Huntsville. What does cost-sharing look like?"
Claude will: apply 1/3 performer cost share per 4022(d)(1)(C), show government vs. performer obligations per milestone, cumulative funding profile.

**Consortium OT:** "DIU prototype, NDC performer, 4 milestones. Price this."
Claude will: no cost share (NDC path), add 5% consortium management fee, show government obligation including fee per milestone.

**Hardware prototype:** "Estimate should-cost for a 3-unit sensor prototype, TRL 4-6, 24 months"
Claude will: flag materials-heavy estimate, derive BOM categories from prototype type, benchmark labor, produce workbook with materials as dominant cost element.


---

*MIT James Jenrette / 1102tools. Source: github.com/1102tools/federal-contracting-skills*
