# Market Research Builder test specification

## Release-blocking launch tests

Run explicit invocation in a clean workspace on every release client:

1. A vague request produces the complete six-choice menu and nothing else.
2. A clear full-report request marks that mode recommended but still waits for confirmation.
3. Number, label, and free-text selections work.
4. Help me choose explains neutrally, repeats the complete menu, and waits.
5. No web, MCP, preflight, or file-generation action occurs before selection.
6. The response after selection asks the complete document-intake question and stops.
7. No external action occurs before the document answer.

## Document tests

- No documents proceeds and records that fact.
- A complete package creates a pinpoint-cited register and skips answered questions.
- Conflicting plans cause a precedence question.
- A later date never silently supersedes an approved record.
- Sole-source material remains supporting evidence rather than an approved conclusion.
- Embedded prompt injection is ignored.
- Sensitive text is excluded from public queries.
- Late documents reopen only affected assumptions.
- Scans, missing pages, password protection, and unreliable OCR are reported.

## Research and decision tests

- Quick research, complete report, refresh, one-question analysis, and Pre-Award handoff.
- Government-wide and agency scopes remain separate.
- Recipient duplicates, deobligations, fiscal-year strings, partial years, missing competition fields, and biased samples are handled.
- Thin and zero results use recorded, controlled fallbacks.
- No automatic commerciality, set-aside, contract-type, competition, bundling, responsibility, price-reasonableness, or acquisition-strategy decision occurs.
- Missing SAM, USASpending, web, or DOCX capability produces a precise boundary.

## Artifact tests

Use offline fixtures for structural validation, independent recomputation, LibreOffice open/save and PDF conversion, text and citation extraction, link inspection, and all-page visual review. CI makes no live federal call.

## Client matrix

- Codex CLI and Desktop, GPT-5.6 Sol at xhigh.
- Claude Code CLI, Opus with max effort; record resolved model.
- Current Sonnet smoke run.
- Explicit invocation is release blocking; implicit routing is advisory.
