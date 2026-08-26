# Launch menu, outcome previews, and question blocks

## First response

Show the complete six-choice menu in `SKILL.md`. If the opening request clearly maps to one mode, append `Recommended` to that choice without removing or reordering any choice. End with: `Which option would you like? You can reply with the number, label, or your own wording.`

The whole first-turn response is the menu and selection question. Do not announce the skill, acknowledge the request, add a preamble, add substantive research, perform a capability check, or ask a second question.

## Productive-mode outcome preview

After options 1 through 5, output the selected route below using these exact labels and in this order. Keep each field concise. Do not add an alternative product unless it materially changes the route.

| Option | Recommended outcome | Includes | Boundary/default | Next |
|---|---|---|---|---|
| 1 | Sourced Market Research Findings in chat | the scoped question, traceable evidence, analysis, limitations, and open acquisition decisions | chat is the default; the user or Contracting Officer retains commerciality, competition, set-aside, contract-type, consolidation, responsibility, price-reasonableness, and final-strategy decisions | ask for existing acquisition documents |
| 2 | Validated FAR Part 10 Market Research Report `.docx` | the requirement and scope, methods and sources, market and vendor evidence, analysis, limitations, findings, decision register, and evidence register | the formal report is the default; generation occurs only after plan, findings, and acquisition-decision approvals | ask for existing acquisition documents |
| 3 | Refreshed Market Research Package with a change log | the prior record or report, stale or changed evidence, affected findings, preserved history, and a concise before/after summary | preserve the prior output type when supplied; otherwise default to refreshed sourced findings in chat | ask for the prior report or record and any other acquisition documents |
| 4 | Focused Acquisition Question Analysis in chat | one bounded issue, relevant evidence, analysis, limitations, and the decision left to the authorized user | chat is the default and the analysis does not expand into a complete report unless the user deliberately changes modes | ask for existing acquisition documents |
| 5 | Structured Pre-Award Market Research Handoff in chat | approved findings, requirement and market constraints, source references, assumptions, and unresolved acquisition decisions for downstream scope and pricing work | the handoff is an internal workpaper, not a substitute for Contracting Officer decisions or a separate report | ask for existing acquisition documents |

Render the row as:

```text
Recommended outcome: <value>
Includes: <value>
Boundary/default: <value>
Next: <value>
```

Immediately after the preview, ask exactly:

> Do you have existing acquisition documents I should review before I plan the research? You may attach files, provide accessible local paths, paste relevant text, or say that no documents are available. Useful materials include a current or previous acquisition plan or strategy; existing market research report; SOW, PWS, SOO, specification, statement of need, or requirements document; purchase request or requirements package; sole-source, limited-sources, brand-name, or exception-to-competition justification; sources-sought notice, RFI, draft solicitation, responses, or vendor capability statements; previous solicitation, contract, task order, award, or modification; IGCE, pricing memorandum, quote, catalog, or price research; QASP or performance standards; small-business coordination record; agency template, supplement, deviation, checklist, or approval record; and any other document you believe controls or informs the acquisition.

End there and wait. Do not add mode-specific intake, research, capability preflight, or generation in the same response. Never combine the menu and post-selection guidance in one response.

## Help me choose

Reuse objective, documents, and intended-use context already present in the conversation. If those facts identify one route, recommend it immediately. Otherwise ask no more than these three plain-language questions in one response:

When questions are needed, the entire response is exactly the numbered questions below. Do not preface them with a question, repeat a question, or add any other question.

1. What decision or work product are you trying to support?
2. Do you have an existing report or acquisition documents to use?
3. Will you use the result as quick chat guidance, a formal contract-file report, or a handoff into Pre-Award work?

After the answer, recommend exactly one numbered route. Explain why, name its outcome and major contents, state the default and reserved decisions, offer at most one materially different alternative, and end with `Do you want me to proceed with option N using these defaults?` using the actual option number. Never reprint the full menu, repeat the diagnostic questions, or ask the user to invent or name a report.
