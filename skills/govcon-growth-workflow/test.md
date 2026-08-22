# GovCon Growth Workflow current test evidence

Tested August 21, 2026 from a clean temporary installation of the complete skill folder.

## Current result

| Surface | Model / version | Result |
|---|---|---|
| Codex CLI | `codex-cli 0.149.0-alpha.4`, GPT-5.6 Sol, xhigh | Pass: explicit invocation returned only the complete nine-choice menu, marked opportunity discovery recommended, and made no web or MCP call. |
| Claude Code CLI | `2.1.239`, `claude-opus-5`, max effort | Pass: explicit invocation returned only the complete recommended menu. The CLI reported zero web-search and web-fetch requests. |
| Claude Code CLI smoke | `2.1.239`, `claude-sonnet-5`, max effort | Pass: explicit invocation returned only the complete recommended menu with no external request. |

## Deterministic and artifact evidence

- Both `quick_validate.py` and the repository eight-skill validator passed.
- Shared evidence-contract and research-record validator copies were byte-identical.
- Valid GovCon and Market Research records passed; unknown evidence IDs, sensitive query keys, and credential-like content failed as expected.
- The offline evidence-brief fixture passed record validation, required-section validation, evidence-ID coverage, bid-decision boundary checks, and independent recomputation of `6,000,000.00` from three source values.
- The incomplete company-context fixture correctly produced `Evidence Brief - No Bid Decision` and listed missing vehicle, clearance, teaming, risk, and margin inputs.
- LibreOffice opened the DOCX and converted it to a three-page PDF.
- Text and evidence citations were extracted, and every rendered page was visually inspected after fixing compact-list collisions.

All federal results in the fixture are synthetic. No live federal API call was made for this evidence.

## Open evidence

- A clean Codex Desktop invocation has not been independently rerun after this skill was added.
- Each menu branch has a scenario specification, but the complete live-source branch matrix remains release-candidate coverage.
- Implicit activation remains advisory and is not counted as a deterministic invocation path.
- Full upload-only-client and real-opportunity artifact scenarios remain open.
