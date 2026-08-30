# Route-specific GovCon Growth product specification

## Customer identity and reader-visible language

The customer organization name, size posture, and constraints used anywhere in the document must come verbatim from user intake. Never substitute a placeholder company, a different size profile, or invented constraints.

Internal harness vocabulary is prohibited in every reader-visible field, including headers, footers, titles, body text, tables, and the Source Register: never write "fictional", "test", "synthetic", "fixture", "bounded sample", or "archived record" where a reader can see it. When the user has not approved live research, honest illustrative labeling uses exactly one standard reader-facing line, placed in the limitations block only: "Illustrative analysis prepared without live-data confirmation". The brief validator rejects documents containing the banned tokens.

## Evidence classes render as reader labels

Evidence source classes are internal record vocabulary, not capture vocabulary. The research record, the record validator, and the evidence contract keep the internal tokens (`document`, `federal_mcp`, `official_web`, `other_web`, `user_statement`, `calculation`), but the builder renders each one as a reader-facing label wherever it reaches the page, including the Source Register: Supplied document, Federal data service, Official website, Public web source, Customer statement, Recorded calculation. These are the same labels the market research product uses, so the two deliverables speak one vocabulary. A raw class token must never appear anywhere in the document text, and the brief validator errors when one does.

## Verifiable locators

Every evidence row sourced from federal data (`federal_mcp`, `official_web`, `other_web`) must carry a checkable locator a reader can independently verify: a SAM.gov notice ID, award PIID, UEI, docket number, or public URL, plus the retrieval date. Never state that locators "were not preserved"; if a locator was not captured, the evidence row is not usable in the deliverable. The brief validator errors on federal evidence rows with an empty locator.

## Honest evidence basis and real retrieval times

The page-one evidence-basis line must match the research record. If the record logs any live source call (federal MCP, official web, or public web), the line may not claim "Supplied evidence only", "No public research performed", or "No external query recorded"; declining public web research does not make federal data calls disappear, and the correct line in that case acknowledges live federal data research while noting that no public web research was performed. Conversely, a line that claims live or public-source research is prohibited when the record logs no source calls. The brief validator errors on either contradiction.

Retrieval timestamps are the actual clock times of the source calls, never a placeholder. When the record carries three or more retrieval timestamps and every one of them is midnight-exact (T00:00:00Z or an equivalent), the brief validator errors and directs the author to record actual retrieval times. A single midnight value among real times is accepted.

## Design

Use US Letter, 0.75 to 1 inch margins, Aptos or Arial body text, restrained color, accessible contrast, page numbers, and real Word heading styles. First pages are decision pages, not generic covers: the title, business question, one decisive insight, and next action must be visible without turning a page. Use an appropriate route accent and layout: shortlist (pipeline cards), screen (decision dashboard), competitor (positioning map), recompete (radar table), teaming (decision card), account plan (market thesis), pricing (rate band), and refresh (delta ledger). Repeat table headers where the renderer preserves the printable margin. Use landscape only for wide evidence tables.

## Required outcomes, not a fixed generic section order

Every product delivers a decision-first opening, tailored analysis appropriate to the selected route, practical next moves when the record supports them, proportionate limitations, and a concise Source Register. Length follows the evidence and the management question. A one-page screen can be the right product; a nuanced landscape may need substantially more room. Do not target a page count, reuse the same title or section stack, or call every route an “Evidence Brief.” Internal query logs and internal evidence identifiers remain in the research sidecar and do not appear in the customer document.

The rendered product is the design authority. Passing a schema or structural validator is only a technical floor. A product fails if a reasonable executive still has to invent the decision, the next move, the owner, the proof needed, or the stop condition after reading it.

## Route-native paid-value contract

Each productive route must answer the route's management question and include the listed operating content. Do not substitute a generic findings-and-appendix brief.

Each route either answers its management question from the approved evidence or leads with an explicit shortfall statement that names what was not obtainable and the exact follow-up query plan. Padding a route with out-of-scope items is prohibited: a shortlist of one is a shortlist of one plus a shortfall statement, never a list inflated with rejected or off-scope candidates; a delta audit that could not examine the revised solicitation says so on page one; a competitor landscape covering one company is labeled a single-company profile with the queries still needed for a landscape.

Section content must be route-native. Within one engagement, never reuse an identical analysis paragraph, fit narrative, or stop-condition subtext across routes; every analysis statement comes from the approved record for that route, not from template boilerplate. No section may restate a list or table already shown on page one; later sections extend page one with status or remaining items instead of duplicating it.

| Route | Page-one decision | Paid-value body | Operational unknowns |
|---|---|---|---|
| Opportunity shortlist | Which opportunities deserve scarce capture attention now? | Ranked pipeline signals, timing, fit, confidence, and 48-hour qualification moves | Missing notice details, access, customer fit, and response-window facts |
| Opportunity screen | What bounded pursuit posture should management take? | Fit/access scorecard, decision gates, workshare thesis, and advance/hold/stop rule | Sponsor, eligibility, attachments, security, delivery, and economics gaps |
| Competitor landscape | How should the company position or engage? | Positioning implications, evidence-backed strengths/limits, and engagement moves | Entity ambiguity, unsupported claims, customer overlap, and role assumptions |
| Recompete pipeline | Which timing signals merit validation and when? | Radar, validation calendar, trigger owners, and confidence | End dates, options, modifications, vehicle constraints, and customer intent |
| Teaming card | What partner posture is justified? | Role-fit scorecard, diligence plan, next conversation, and stop conditions | Commitment, responsibility, financial health, conflicts, workshare, and trust |
| Agency or market plan | Where should the account team focus and what should it do next? | Market thesis, demand and buying patterns, whitespace, and 90-day account moves | Scope bias, customer access, budget timing, vehicles, and incomplete award data |
| Pricing context | What rate position and proposal guardrails are supportable? | Comparable rate bands, driver analysis, scenario implications, and guardrails | Paid-rate evidence, labor mapping, geography, escalation, and margin inputs |
| Delta audit | What changed and does it change the prior action? | Decision-impact ledger, stale assumptions, preserved prior record, and updated actions | Unrefreshed sources, unresolved conflicts, and changes that remain unverified |

Page one must show, without turning the page: the route-specific product title and business question; a plain-language management posture; up to three evidence-backed signals; the immediate moves; and the most consequential operational unknowns. For bid screens with incomplete internal context, the posture remains conditional and cannot become a bid/no-bid verdict.

Use `validation.decision_rule` when the approved record contains a route-specific advance/hold/stop or investment rule. When it is absent, do not invent approval thresholds; state the evidence still needed to make the decision.

Every consequential finding cites a reader-facing source marker such as `[S1]` or `[S1, S4]`. Number sources by first appearance, list them once in the Source Register with direct locators, and never expose internal `E001`-style identifiers. State the as-of date and distinguish public evidence from internal user context. If an opportunity screen lacks complete internal context, frame the result as a conditional pursuit posture rather than a bid/no-bid decision.

Do not include prompts, tool prefixes, local paths, credentials, or proprietary input beyond what the user approves for the deliverable.

## Human render gate

After structural validation and PDF conversion, inspect every rendered page at normal reading scale and at 100 percent. Reject and rebuild the product for any blank or near-empty artifact page, clipped or pinned table text, split decision block, unreadable evidence table, generic repeated section structure, or appendix that visually overwhelms the decision product.

The final review must answer yes to each question:

- Can the intended executive state the posture and next action from page one?
- Are public evidence, internal context, inference, and unknowns visibly distinguishable?
- Does the body provide route-native work product rather than repeated findings?
- Are owners, proof obligations, timing, and stop conditions explicit where the record supports them?
- Is the Source Register compact, honest about source preservation, and subordinate to the business decision?
- Are all pages clean when rendered, with no blank pages, overflow, clipping, or awkward page breaks?
