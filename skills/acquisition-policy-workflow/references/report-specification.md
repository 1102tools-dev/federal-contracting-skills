# Acquisition Policy written-product specification

## Route-specific written products

Use a distinct product name and lead form for each route. The first page states the policy question, as-of date, governing source layers, documented status, practical acquisition impact, key uncertainty, and next responsible action. Keep evidence in an appendix or source note, not in the opening view.

| Route | Product | Lead form |
|---|---|---|
| Current text | Current Rule Explanation | annotated rule card |
| Agency status | Agency Policy Status Matrix | status dashboard and confirmation list |
| Three-layer comparison | Three-Layer Policy Comparison | comparison table and adoption test |
| Change comparison | Regulatory Change Briefing | before/after change map |
| Rulemaking | Rulemaking Timeline | dated milestone sequence |
| Comment periods | Open Rulemaking Watchlist | deadline watchlist |
| Comments | Public Comment Position Analysis | sample-method panel and theme map |
| Refresh | Policy Analysis Refresh | change log and carry-forward decisions |

The product name is a substantive promise, not merely a heading:

- A Regulatory Change Briefing requires matched before-and-after text, a clause- or section-level delta, operational consequences, and evidence IDs.
- An Open Rulemaking Watchlist requires live matter or docket identifiers, stage, verified deadline or an explicit no-open-window result, next event, owner, and recommended action.
- A Public Comment Position Analysis requires an approved sample frame, returned and reviewed counts, stakeholder segments, coded themes, contrary positions, limitations, and acquisition implications.
- A Policy Analysis Refresh requires a dated prior baseline, current retrievals, changed and unchanged conclusions, consequences, and refresh actions.

If the approved record lacks the evidence that makes the selected product useful, provide a short evidence-acquisition note in chat. Do not turn an evidence gap into a six-page report that resembles a completed analysis.

## Product-first reader contract

Every written product must lead with the operational meaning of the approved evidence, not a recap of the request or a research-process summary. Before the detailed source sections, the opening view must provide:

1. **Planning posture:** a plain-English posture such as proceed from the codified baseline, implement within documented agency scope, monitor pending rulemaking, or hold a disputed implementation point for authorized resolution.
2. **Immediate implications:** what the posture changes for acquisition planning, solicitation timing, file support, industry communication, or monitoring. Use only implications supported by the approved findings.
3. **Owners and decision gates:** identify who must supply the next decision-ready evidence and when it is needed. Prefer roles such as policy office, contracting officer, counsel, program office, or policy analyst over vague next steps.
4. **Planning scenarios:** show how the treatment changes if the baseline holds, agency adoption is confirmed, rulemaking changes status, or a material conflict remains unresolved. Include only scenarios relevant to the route and record.
5. **Proportionate boundary:** reserve legal advice, procurement-specific applicability, deviation approval, and other official determinations in a compact note. Do not let boundary language displace the practical answer.

When the approved record supplies `validation.planning_posture`, `validation.decision_gates`, or `validation.planning_scenarios`, use those approved fields. Otherwise the builder derives conservative route-appropriate content from policy statuses, conflicts, open questions, and evidence IDs. Never invent an agency adoption, effective date, controlling value, owner commitment, or procurement fact to make the product appear decisive.

## Impact Brief required sections

1. Planning Posture and Implications
2. Owners and Decision Gates
3. Question and Scope
4. Documented Current Status
5. Source Hierarchy and Authorities
6. Planning Scenarios
7. Change Timeline
8. Government and Industry Impacts
9. Open Issues and Comment Deadlines
10. Operational Considerations
11. Evidence Register
12. Limitations and Reserved Determinations

Use the `standard_business_brief` visual preset with a restrained memo masthead. Use US Letter portrait, one-inch margins, Calibri 11-point body text, blue heading hierarchy, quiet running header/footer, real list styles, and fixed-width tables with repeating header rows.

The title block states the agency or scope, as-of date, audience lens, and preparation status. Do not call the brief a legal opinion, authoritative policy determination, or contract-file approval.

## Evidence presentation

- Put evidence IDs beside every consequential finding and impact statement.
- Preserve canonical public hyperlinks in the evidence register.
- Keep codified text, agency deviations, model text, rulemaking, guidance, and public comments visually distinguishable.
- Use tables only for repeated comparable records such as policy layers, timelines, and the evidence register.
- Do not place internal prompts, tool names, filesystem paths, credentials, or raw private text in the document.

## Impacts

Government and industry lenses use the same evidence. They may differ only in operational framing:

- Government: acquisition planning, solicitation timing, internal policy confirmation, transition treatment, and file documentation.
- Industry: solicitation interpretation questions, proposal assumptions, compliance planning, timing, and monitoring.
- Neutral: both lenses without advocacy.

Impacts are considerations, not directives or legal conclusions.

## Validation

The builder requires `validation.findings_approved` and `validation.brief_approved` to be true. The validator checks that planning posture is the first substantive section, owners/gates and scenarios are present, section order, evidence-ID coverage, live hyperlinks, as-of date, decision-boundary language, fixed table geometry, repeating headers, prohibited internal content, and policy-record validity.

Validation is a floor, not the release decision. After validation, convert the DOCX through LibreOffice, extract text, confirm live links, render every page, and inspect the rendered product as the intended reader. Reject and revise any output whose first page does not answer what the reader should do, whose tables crowd or clip, whose boundaries overwhelm the recommendation, or whose owners and scenarios are too generic to use. Repeat validation and rendering after each material revision.
