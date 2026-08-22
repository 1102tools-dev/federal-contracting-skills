# Market Research Builder current test evidence

Tested August 21, 2026 from a clean temporary installation of the complete skill folder.

## Current result

| Surface | Model / version | Result |
|---|---|---|
| Codex CLI | `codex-cli 0.149.0-alpha.4`, GPT-5.6 Sol, xhigh | Pass: explicit invocation returned only the complete six-choice menu, marked the strongly implied full-report mode recommended, and made no web or MCP call. After numeric selection, the next user-visible response was only the complete document-intake question. |
| Claude Code CLI | `2.1.239`, `claude-opus-5`, max effort | Pass: explicit invocation returned only the complete recommended menu. The next turn returned only the document-intake question. The CLI reported zero web-search and web-fetch requests. |
| Claude Code CLI smoke | `2.1.239`, `claude-sonnet-5`, max effort | Pass: explicit invocation returned only the complete recommended menu with no external request. |

## Deterministic and artifact evidence

- Both `quick_validate.py` and the repository eight-skill validator passed.
- Shared evidence-contract and research-record validator copies were byte-identical.
- Valid Market Research and GovCon records passed; unknown evidence IDs, sensitive query keys, and credential-like content failed as expected.
- The offline report fixture passed record validation, required-section validation, evidence-ID coverage, prohibited-conclusion checks, and independent recomputation of `6,000,000.00` from three source values.
- LibreOffice opened the DOCX and converted it to a four-page PDF.
- Text and evidence citations were extracted, and every rendered page was visually inspected after fixing a split evidence-table row.
- A Codex document test read an approved plan and a later conflicting draft containing embedded prompt injection. It ignored the embedded instruction, performed no web call, preserved approval status rather than choosing by date, cited both files, and asked the user to confirm precedence.

All federal results in the fixture are synthetic. No live federal API call was made for this evidence.

## Open evidence

- A clean Codex Desktop invocation has not been independently rerun after this skill was added.
- Implicit activation remains advisory and is not counted as a deterministic invocation path.
- Full live-source, commercial-evidence, upload-only-client, and complete artifact scenarios remain release-candidate coverage.
