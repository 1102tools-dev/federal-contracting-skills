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

Every product begins with a useful first page: the acquisition question, what the evidence shows, decision implications, and the next practical action. Use a short decision callout rather than a cover page that consumes a full page. Put source logs and full evidence-register detail in an appendix. A complete report normally includes acquisition context, evidence, market options to test, method, and human-owned decisions. Other products use only the route-specific sections needed to make the reader effective.

Render route-native paid-value content rather than the same compliance stack for every route:

- Complete report or desk-research draft: acquisition frame, supported findings, capability and packaging hypotheses, a usable market-engagement instrument, evidence-to-decision gates, an owned execution plan, and human-owned decisions and unknowns.
- Refresh: what changed, what remains usable, what must be rechecked, and an owned refresh plan.
- One-question analysis: bounded answer, evidence for and against, decision implications, and useful further-research options.
- Pre-Award handoff: approved observations, requirements implications, pricing-evidence boundaries, and explicit Pre-Award intake actions.

Use structured `validation` entries when the product needs them: `decision_implications`, `next_actions` (`owner`, `when`, `action`, `output`), `capability_model`, `packaging_hypotheses`, `market_engagement_instrument`, `decision_gates`, refresh-specific change fields, or `requirements_implications`. Turn every unresolved item into a visible owner, decision gate, and evidence/action need. If the record lacks an approved instrument or gate, say so; do not invent market evidence or a reserved decision in the builder.

Every consequential finding cites an evidence ID. Document-derived claims also cite file and page, section, table, or paragraph. State the as-of date prominently. Label user-provided facts, public facts, interpretation, confidence, and unresolved questions where they affect a decision. Do not make the evidence register the main narrative.

## Completion label

Use `FAR Part 10 Market Research Report` only when planned live federal, public-web, and commercial evidence was obtained and approved. A boolean completion flag cannot override synthetic, fixture-only, or explicitly non-live federal evidence. Otherwise use `Federal-Data Desk-Research Draft` and state which source classes are missing.

Do not include hidden prompts, tool names, generated namespaces, local paths, credentials, or source document text beyond short necessary paraphrases.
