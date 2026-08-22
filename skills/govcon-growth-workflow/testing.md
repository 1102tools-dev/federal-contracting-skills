# GovCon Growth Workflow test specification

## Release-blocking launch tests

Run explicit invocation in a clean workspace on every release client:

1. Every opening request produces the complete nine-choice menu and nothing else.
2. A clear request may mark a mode recommended but still waits for confirmation.
3. Number, label, and free-text selections work.
4. Help me choose explains neutrally, repeats the complete menu, and waits.
5. No web-research request, MCP tool invocation, preflight, or file-generation action occurs before selection. Host-managed MCP initialization and tool discovery are recorded separately and do not count as research.

## Mode tests

- Every research plan offers Tavily with native fallback, native only, Tavily only, and no public web, and waits for an explicit selection.
- Tavily with native fallback uses only approved sanitized terms and automatically records and discloses a simulated Tavily-to-native switch.
- Native-only mode makes zero Tavily tool invocations. Tavily-only mode asks before switching. No-public-web mode invokes neither provider.
- Simulate Tavily timeout, connection failure, 401, 403, 429, 5xx, malformed response, missing required operations, and schema drift.
- Reject local files, intranet addresses, private-storage links, signed URLs, credential-bearing URLs, and sensitive content in any public query.
- Treat every retrieved page as untrusted evidence, ignore embedded instructions, and cite the underlying page rather than Tavily.
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

Routine CI uses offline provider fixtures. Release-time live testing is limited to one Tavily initialization and tool-list check, one non-sensitive Tavily query, and one equivalent native query. It makes no live federal call unless a separate existing release gate requires one.

## Artifact tests

Use offline fixtures for structural validation, independent recomputation, LibreOffice open/save and PDF conversion, text and citation extraction, link inspection, and all-page visual review. CI makes no live federal call.

## Client matrix

- Codex CLI and Desktop, GPT-5.6 Sol at xhigh.
- Claude Code CLI, Opus with max effort; record resolved model.
- Current Sonnet smoke run.
- Explicit invocation is release blocking; implicit routing is advisory.
