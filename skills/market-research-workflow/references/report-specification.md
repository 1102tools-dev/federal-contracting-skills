# Market research report specification

## Design

Use US Letter, 0.75 to 1 inch margins, Aptos or Arial body text, restrained navy and green accents, accessible contrast, page numbers, repeating table headers, and real Word heading styles. Avoid decorative clutter. Use landscape pages only for wide evidence tables.

## Route-specific products

Select the lightest product that answers the selected route. Never force a refresh, one-question analysis, or Pre-Award handoff into the full-report template.

| Route | Product title pattern | Core reader need |
| --- | --- | --- |
| Complete report | `[Acquisition] Market Research Report` | Decision-ready evidence across the market-research scope. |
| Refresh | `Market Research Refresh` | What changed, what remains usable, and what must be rechecked. |
| One question | `[Question] Market Evidence Analysis` | A bounded answer, evidence limits, and useful next research options. |
| Pre-Award handoff | `Pre-Award Market Research Handoff` | Approved research observations that later scope and pricing work may consume. |

Every product begins with a useful first page: the acquisition question, what the evidence shows, decision implications, and the next practical action. Use a short decision callout rather than a cover page that consumes a full page. Put a concise Source Register at the end. Keep query logs and raw retrieval records in the research sidecar rather than the customer report. A complete report may include acquisition context, evidence, market options to test, method, and unresolved decisions, but only when each adds value. Other products use only the route-specific material needed to make the reader effective.

Render route-native paid-value content rather than the same compliance stack for every route:

- Complete report or desk-research draft: acquisition frame, supported findings, capability and packaging hypotheses, a usable market-engagement instrument, evidence-to-decision gates, an owned execution plan, and human-owned decisions and unknowns.
- Refresh: what changed, what remains usable, what must be rechecked, and an owned refresh plan.
- One-question analysis: bounded answer, evidence for and against, decision implications, and useful further-research options.
- Pre-Award handoff: approved observations, requirements implications, pricing-evidence boundaries, and explicit Pre-Award intake actions.

The selected product must contain the evidence that makes its title true:

- A refresh requires a dated prior baseline, current evidence, a field-by-field delta, and acquisition-strategy consequences. Do not generate a full refresh when the record contains only a rerun date.
- A small-business decision analysis requires named candidate concerns or an explicit search-result population, capability and delivery evidence, relevant vehicles or recent awards when available, contrary evidence, outreach actions, and a bounded Rule of Two assessment. Percentages alone are not a market conclusion.
- A Pre-Award handoff requires approved market observations translated into scope, packaging, performance, competition, pricing-input, and risk implications, with named intake owners and decision gates.

When required route evidence is unavailable, return a concise evidence-acquisition note in chat. Do not pad missing evidence into a three-page report that appears complete.

Use structured `validation` entries when the product needs them: `decision_implications`, `next_actions` (`owner`, `when`, `action`, `output`), `capability_model`, `packaging_hypotheses`, `market_engagement_instrument`, `decision_gates`, refresh-specific change fields, or `requirements_implications`. Promote unresolved items into the main product only when they are material to the decision. Name owners and gates when the approved record supplies them. Do not manufacture generic owners, meetings, gates, or process steps merely to fill a template.

## Reader-visible language

Every reader-visible field in the record is written as an acquisition-record statement, never as chat or session narration. Never place phrases such as "the user", "this session", tool or MCP names, or fixture and synthetic vocabulary in findings, unresolved items, conflicts, source titles, locators, facts, limitations, or `validation` narrative; label honest illustrative data as `Illustrative example data (not live research)`. Internal evidence-class tokens (for example `federal_mcp`, `user_statement`, `official_web`) and internal `E001`-style identifiers stay in the JSON contract only. The product cites reader-facing sources as `[S1]`, `[S1, S4]`, or `[S1-S3]`, numbered by first appearance and resolved in a Source Register. If action text references named firms or vendors, the document must actually name those concerns; otherwise rewrite the action. Do not repeat an identical closing action table after the opening actions.

When a compact action label is genuinely useful, it must read as intelligible English and never end mid-word or mid-citation. Do not add a second research-execution table when the opening action table already carries the complete owner, action, and output.

Every retrieval timestamp is the actual time of that source call. The report validator rejects a record whose retrieval stamps are a synthesized batch value: three or more stamps that are all midnight-exact, or five or more stamps that are all identical to each other.

Every consequential finding cites a reader-facing source marker. Document-derived claims also cite file and page, section, table, or paragraph. State the as-of date prominently. Label user-provided facts, public facts, interpretation, confidence, and unresolved questions where they affect a decision. Do not make the Source Register the main narrative.

## Completion label

Use `FAR Part 10 Market Research Report` only when planned live federal, public-web, and commercial evidence was obtained and approved. A boolean completion flag cannot override synthetic, fixture-only, or explicitly non-live federal evidence. Otherwise use `Federal-Data Desk-Research Draft` and state which source classes are missing.

Do not include hidden prompts, tool names, generated namespaces, local paths, credentials, or source document text beyond short necessary paraphrases.
