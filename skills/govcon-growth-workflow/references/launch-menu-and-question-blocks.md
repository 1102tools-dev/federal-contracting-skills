# Launch menu, outcome previews, and question blocks

## First response

Show the complete nine-choice menu in `SKILL.md`. If the opening request clearly maps to a mode, append `Recommended` to that choice without removing or reordering any choice. End with: `Which option would you like? You can reply with the number, label, or your own wording.`

The whole first-turn response is the menu and selection question. Do not announce the skill, acknowledge the request, add a preamble, add research, perform capability preflight, or ask another question.

## Productive-mode outcome preview

After options 1 through 8, render the selected row with the exact labels `Recommended outcome:`, `Includes:`, `Boundary/default:`, and `Next:` in that order. Keep the preview concise.

| Option | Recommended outcome | Includes | Boundary/default | Next |
|---|---|---|---|---|
| 1 | Federal Opportunity Shortlist in chat | sourced notices, deadlines, agencies, set-asides, geography and vehicle constraints, fit rationale, material gaps, and confidence | sourced chat findings are the default; a validated Growth Brief is optional only after findings | collect the search focus and company eligibility constraints |
| 2 | Opportunity Evidence Screen in chat | solicitation facts, company-context coverage, strengths, gaps, risks, contrary evidence, and unresolved internal inputs | public evidence does not become a bid verdict; a recommendation requires complete internal context and stated tolerances | collect the opportunity package and missing company context |
| 3 | Competitor/Incumbent Intelligence Profile in chat | resolved entity identity, awards and obligations, customers, vehicles, public claims, comparison evidence, limitations, and inferences | sourced chat findings are the default and do not determine performance quality, intent, or financial health | collect the exact entity and comparison question |
| 4 | Recompete Pipeline in chat | candidate awards, incumbents, end and option signals, agencies, vehicles, timing uncertainty, and follow-up priorities | contract end dates are validation signals, not guaranteed recompete dates; a brief is optional after findings | collect the agency, service area, and pipeline horizon |
| 5 | Partner Shortlist or Due-Diligence Profile in chat | registration and exclusion evidence, certifications, awards, customer and vehicle overlap, apparent role fit, gaps, and limitations | default to a shortlist when no company is named and due diligence when one is named; public data does not establish trust, responsibility, or legal suitability | ask whether the user is finding partners or vetting named companies, unless context already answers it |
| 6 | Agency/Market Intelligence Snapshot in chat | spending and award patterns, recipients, customers, codes, geography, period, trends, limitations, and business implications | sourced chat findings are the default; government-wide and agency-specific scopes remain separate | collect the customer or market question and scope |
| 7 | Labor-Rate/Pricing Context Table in chat | labor-category context, experience and education, geography, year, CALC+ positioning, internal assumptions, sample limits, and source dates | neutral positioning is the default; CALC+ ceiling rates are not paid-rate evidence or a price determination | collect the labor categories and comparison basis |
| 8 | Refreshed Prior Research with a change log | the prior brief or register, stale sources, changed evidence and assumptions, affected findings, and a before/after summary | preserve the prior output type; do not silently rebuild unaffected research | collect the prior product, as-of date, and stated changes |

## Mode intake

After the preview, ask only for relevant missing context and optional files:

- Opportunity: notice or solicitation ID, agency, keywords, NAICS/PSC, geography, date window, vehicles, and eligibility constraints.
- Bid screen: solicitation package plus company capabilities, differentiators, past performance, clearances, certifications, vehicle access, staffing/geography, teaming, priorities, and risk/margin tolerances.
- Competitor/incumbent: exact entity, UEI/CAGE when known, agencies, offerings, dates, and comparison question.
- Recompete: agencies, incumbent/PIIDs, service area, contract end window, vehicles, and pipeline horizon.
- Teaming: whether the user is finding or vetting, required capabilities, named entities when any, socioeconomic or vehicle needs, geography, clearances, workshare intent, and exclusions.
- Agency/market: customer, problem, NAICS/PSC, geography, period, and market question.
- Pricing: labor categories, level, education, experience, geography, year, contract source, and internal assumptions.
- Refresh: prior brief or register, as-of date, and what changed.

Invite relevant documents listed in `SKILL.md`. If none exist, record that fact. Reuse supplied context, end with one concise question, and wait.

## Help me choose

Reuse objective, available materials, and intended-use context already present. If those facts identify one route, recommend it immediately. Otherwise ask no more than these three plain-language questions in one response:

When questions are needed, the entire response is exactly the numbered questions below. Do not preface them with a question, repeat a question, or add any other question.

1. What business decision or growth objective are you trying to support?
2. Do you already have a specific notice, company, prior brief, or internal company material?
3. Is the result for immediate screening, pipeline development, market understanding, or pricing context?

After the answer, recommend exactly one numbered route. Explain why, name its outcome and major contents, state its default and business-decision boundary, offer at most one materially different alternative, and end with `Do you want me to proceed with option N using these defaults?` using the actual option number. Never reprint the full menu, repeat the diagnostic questions, or ask the user to invent or name an output.
