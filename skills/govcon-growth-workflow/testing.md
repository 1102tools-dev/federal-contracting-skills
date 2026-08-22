# GovCon Growth Workflow test specification

## Release-blocking launch tests

Run explicit invocation in a clean workspace on every release client:

1. Every opening request produces the complete nine-choice menu and nothing else.
2. A clear request may mark a mode recommended but still waits for confirmation.
3. Number, label, and free-text selections work.
4. Help me choose explains neutrally, repeats the complete menu, and waits.
5. No web, MCP, preflight, or file-generation action occurs before selection.

## Mode tests

- Opportunity discovery and notice interpretation.
- Bid screen with complete and incomplete company context.
- Competitor and incumbent analysis with entity ambiguity.
- Recompete radar with uncertain end dates.
- Partner identification and public due diligence.
- Agency and market intelligence.
- Pricing context that preserves the CALC+ ceiling-rate limitation.
- Prior-brief refresh.
- Missing or rate-limited SAM and optional DOCX generation.

Every mode tests no-document intake and at least one relevant supplied document. Bid recommendations must be withheld unless every required internal category is present.

## Artifact tests

Use offline fixtures for structural validation, independent recomputation, LibreOffice open/save and PDF conversion, text and citation extraction, link inspection, and all-page visual review. CI makes no live federal call.

## Client matrix

- Codex CLI and Desktop, GPT-5.6 Sol at xhigh.
- Claude Code CLI, Opus with max effort; record resolved model.
- Current Sonnet smoke run.
- Explicit invocation is release blocking; implicit routing is advisory.
