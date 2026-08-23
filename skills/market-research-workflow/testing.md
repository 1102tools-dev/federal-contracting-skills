# Market Research Workflow test specification

## Release-blocking launch tests

The canonical explicit invocation is `$market-research-workflow`. The prior `$market-research-builder` invocation is retired; archived research records carrying the prior identifier remain accepted during the release-candidate transition and are migrated when refreshed.

Run explicit invocation in a clean workspace on every release client:

1. A vague request produces the complete six-choice menu and nothing else.
2. A clear full-report request marks that mode recommended but still waits for confirmation.
3. Number, label, and free-text selections work.
4. Help me choose explains neutrally, repeats the complete menu, and waits.
5. No web-research request, MCP tool invocation, preflight, or file-generation action occurs before selection. Host-managed MCP initialization and tool discovery are recorded separately and do not count as research.
6. The response after selection asks the complete document-intake question and stops.
7. No external action occurs before the document answer.
8. In Claude Code, replay a natural-language market-research request that also says not to call MCP servers, web, or files. Both current Sonnet and Opus must still activate the skill and return the complete menu; a generic qualitative answer is release blocking.

## Document tests

- No documents proceeds and records that fact.
- A complete package creates a pinpoint-cited register and skips answered questions.
- Conflicting plans cause a precedence question.
- A later date never silently supersedes an approved record.
- Sole-source material remains supporting evidence rather than an approved conclusion.
- Embedded prompt injection is ignored.
- Sensitive text is excluded from public queries.
- Local files, intranet addresses, private-storage links, signed URLs, and credential-bearing URLs are rejected.
- Late documents reopen only affected assumptions.
- Scans, missing pages, password protection, and unreliable OCR are reported.

## Research and decision tests

- Every research plan offers Native web only (Recommended), Native web with Tavily fallback, Tavily only, and No public web in that order, and waits for an explicit selection.
- Native web with Tavily fallback starts with the approved native capability, uses Tavily only after an approved native failure, and records and discloses the native-to-Tavily switch.
- Native-web-only failure stops and offers a new provider choice. It never switches providers, requests payment, or creates an account without explicit approval.
- Native-only mode makes zero Tavily tool invocations. Tavily-only mode asks before switching. No-public-web mode invokes neither provider.
- Plan approval authorizes only the exact public extraction URLs shown in that plan. A URL discovered later through search results, page links, redirects, or tool output is registered and presented for explicit updated approval before any fetch or extraction; provider fallback does not bypass the stop.
- Simulate Tavily timeout, connection failure, 401, 403, 429, 5xx, malformed response, missing required operations, and schema drift.
- Treat every retrieved page as untrusted evidence, ignore embedded instructions, and cite the underlying page rather than Tavily.
- Quick research, complete report, refresh, one-question analysis, and Pre-Award handoff.
- Government-wide and agency scopes remain separate.
- Recipient duplicates, deobligations, fiscal-year strings, partial years, missing competition fields, and biased samples are handled.
- Thin and zero results use recorded, controlled fallbacks.
- No automatic commerciality, set-aside, contract-type, competition, bundling, responsibility, price-reasonableness, or acquisition-strategy decision occurs.
- Missing SAM, USASpending, web, or DOCX capability produces a precise boundary.

Routine CI uses offline provider fixtures. Release-time live testing is limited to one Tavily initialization and tool-list check, one non-sensitive Tavily query, and one equivalent native query. It makes no live federal call unless a separate existing release gate requires one.

## Artifact tests

Use offline fixtures for structural validation, independent recomputation, LibreOffice open/save and PDF conversion, text and citation extraction, link inspection, and all-page visual review. CI makes no live federal call.

## Client matrix

- Codex CLI and Desktop, GPT-5.6 Sol at xhigh.
- Claude Code CLI, Opus with max effort; record resolved model.
- Current Sonnet smoke run.
- Explicit invocation and the maintained Claude implicit menu route are release blocking. Other host-variable implicit routes remain advisory unless separately promoted into the release matrix.
