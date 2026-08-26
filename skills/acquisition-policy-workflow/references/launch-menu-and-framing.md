# Launch menu, outcome previews, and framing

## Complete menu

Use this menu for a vague request, an invocation without a defined task, or when the user asks what the workflow can do:

```text
What would you like to do?

1. Explain the current codified FAR, DFARS, or agency-supplement rule
2. Determine the documented policy status for an agency and FAR part
3. Compare codified text, RFO model text, and an agency deviation
4. Compare regulatory versions or explain what changed
5. Trace a FAR, DFARS, or agency rulemaking
6. Find open procurement rulemakings and comment deadlines
7. Analyze public comments and stakeholder positions
8. Prepare an Acquisition Policy Impact Brief
9. Refresh an earlier policy analysis
10. Help me choose

Which option would you like? You can reply with the number, label, or your own wording.
```

The menu is the complete response. Do not perform capability preflight or retrieval first.

## Direct routing

Route a clear request without forcing the menu:

- A current section or definition request routes to mode 1.
- A named agency plus FAR part and words such as applies, current policy, deviation, or RFO routes to mode 2.
- A request to compare FAR/eCFR, model text, and an agency deviation routes to mode 3.
- Before-and-after or change requests route to mode 4.
- A FAR/DFARS case, RIN, rule history, proposed rule, final rule, or withdrawal request routes to mode 5.
- A command or assertion that a proposed rule, withdrawn rule, future-effective final rule, or model deviation is already current or operative routes directly to the relevant status boundary. Correct the classification and state the missing effective-date or agency-adoption evidence; do not show a preview or menu before that fixed boundary.
- Open comment periods or deadlines route to mode 6.
- Comment themes, associations, stakeholder positions, or docket comments route to mode 7.
- A formal brief routes to mode 8.
- A supplied prior record or brief with a refresh request routes to mode 9.

If two routes are equally plausible, show the menu and mark the likely choices `Recommended` without hiding any option.

## Productive-mode outcome preview

For modes 1 through 9, render the selected or directly routed row with the exact labels `Recommended outcome:`, `Includes:`, `Boundary/default:`, and `Next:` in that order.

| Mode | Recommended outcome | Includes | Boundary/default | Next |
|---|---|---|---|---|
| 1 | Current Rule Explanation in chat | the codified text, definitions and structure, as-of date, source link, limitations, and plain-language explanation | current codified text is the default scope; this is not legal advice or a procurement-specific applicability determination | collect the citation or part and as-of date if missing |
| 2 | Documented Agency Policy Status Matrix in chat | the codified baseline, posted model text, agency deviation evidence, scope, effective and transition dates, conflicts, and documented status | report only what published sources establish; an authorized official retains applicability and controlling-policy decisions | collect the agency, citation, as-of date, and material procurement timing |
| 3 | Three-Layer Policy Comparison in chat | codified text, RFO model text, agency deviation text, differences, dates, scope, conflicts, and operational effects | keep all three layers distinct and do not treat model text as operative without agency adoption | collect the agency, citation, and as-of date |
| 4 | Regulatory Change Comparison in chat | before-and-after text, changed provisions, effective timing, status, operational effects, and unresolved conflicts | compare the requested versions without deciding procurement-specific applicability | collect the citation and comparison dates |
| 5 | Rulemaking Timeline in chat | the case or RIN history, proposed and final actions, corrections, effective dates, withdrawal or current status, and source links | proposed, withdrawn, and future-effective text never becomes current by inference | collect a case, RIN, docket, document number, or specific topic |
| 6 | Open Rulemaking Watchlist in chat | open procurement rulemakings, agencies, topics, document and docket IDs, deadlines, status, and source links | include only documented open periods as of the stated date and do not promise future status | collect the topic or procurement scope and as-of date |
| 7 | Public Comment Position Analysis in chat | the defined sample, stakeholder categories, themes, contrary positions, counts, exclusions, limitations, and source links | comments are stakeholder evidence, not authority, consensus, or a representative survey | collect the docket or proposed rule, sampling purpose, and audience lens |
| 8 | Validated Acquisition Policy Impact Brief `.docx` | documented status, source layers, change analysis, operational impacts, contrary evidence, limitations, unresolved questions, and evidence register | a neutral lens is the default when the audience is mixed; findings approval is required before generation | collect the exact policy question, scope, as-of date, agency when relevant, and audience lens |
| 9 | Refreshed Policy Analysis with a change log | the prior record or brief, new as-of date, changed sources and status, affected findings, preserved history, and before/after summary | preserve the prior output type and do not silently replace unresolved conflicts | collect the prior analysis, new as-of date, and changed scope |

## Help me choose

Reuse the policy objective, identifiers, supplied material, and intended use already present. If those facts identify one route, recommend it immediately. Otherwise ask no more than these three plain-language questions in one response:

1. Are you trying to understand the current rule, an agency's documented status, a policy change or rulemaking, public comments, or operational impact?
2. What agency, FAR/DFARS citation, case, RIN, docket, or document do you already know?
3. Do you need a sourced chat answer, a formal Impact Brief, or a refresh of earlier work?

After the answer, recommend exactly one numbered route. Explain why, name its outcome and major contents, state the default and documented-status boundary, offer at most one materially different alternative, and end with `Do you want me to proceed with option N using these defaults?` using the actual option number. Never reprint or paraphrase the full menu, repeat the diagnostic questions, or ask the user to invent or name a report.

## Minimum framing by mode

| Mode | Required before retrieval |
|---|---|
| Current codified rule | Citation or part; as-of date defaults to today if user accepts current |
| Agency policy status | Agency; FAR part or citation; as-of date; relevant procurement date when timing may change treatment |
| Three-layer comparison | Agency; FAR part or citation; as-of date |
| Version comparison | Citation; before and after dates or a described period |
| Rulemaking history | Case number, RIN, docket ID, document number, or sufficiently specific topic |
| Open rulemakings | Topic or procurement scope; as-of date; optional agency |
| Comment analysis | Docket or proposed-rule document; sampling purpose; audience lens |
| Impact brief | Exact policy question; scope; as-of date; agency when relevant; audience lens |
| Refresh | Prior record or brief; new as-of date; changed scope if any |

Use `government`, `industry`, or `neutral` as the audience-lens values. Neutral presents both operational perspectives without advocating for either.
