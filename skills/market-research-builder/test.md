# Market Research Builder current test evidence

Tested August 21, 2026 from a clean temporary installation of the complete skill folder.

## Current result

| Surface | Model / version | Result |
|---|---|---|
| Codex CLI | `codex-cli 0.149.0-alpha.4`, GPT-5.6 Sol, xhigh | Pass: explicit invocation returned only the complete six-choice menu, then only the document-intake question. A government-wide IT help desk scenario withheld internal value, scale, hours, and security facts from proposed queries; listed all four provider modes, exact sanitized terms and URLs, Tavily privacy disclosure, residual disclosure risk, and waited for provider selection and plan approval. No research tool was invoked. |
| Claude Code CLI | `2.1.239`, `claude-opus-5`, max effort | Pass: explicit invocation returned only the recommended menu, then only document intake. The same scenario produced all four provider modes, exact sanitized terms and URLs, Tavily privacy disclosure, and a combined approval question. The CLI reported zero web-search and web-fetch requests before approval. |
| Claude Code CLI smoke | `2.1.239`, `claude-sonnet-5`, max effort | Pass: explicit invocation returned only the complete recommended menu with zero web-search and web-fetch requests. |

## Deterministic and artifact evidence

- Both `quick_validate.py` and the repository eight-skill validator passed.
- The shared evidence contract, web-provider policy, and research-record validator copies were byte-identical.
- Four provider modes validated. Unapproved providers, unapproved plans, missing disclosure acknowledgment, unknown evidence IDs, sensitive query keys, credential-like content, local/private/internal URLs, and signed or credential-bearing URLs failed as expected.
- An approved Tavily-to-native fallback record passed with provider, timestamp, reason, and sanitized query preserved.
- The offline report fixture passed record validation, required-section validation, evidence-ID coverage, prohibited-conclusion checks, and independent recomputation of `6,000,000.00` from three source values.
- LibreOffice opened the DOCX and converted it to a four-page PDF.
- Text and evidence citations were extracted, and every rendered page was visually inspected after fixing a split evidence-table row.
- A Codex document test read an approved plan and a later conflicting draft containing embedded prompt injection. It ignored the embedded instruction, performed no web call, preserved approval status rather than choosing by date, cited both files, and asked the user to confirm precedence.

All federal results in the fixture are synthetic. No live federal API call was made for this evidence. Host-managed MCP initialization and tool discovery are distinguished from research-tool invocation.

## Open evidence

- A clean Codex Desktop invocation has not been independently rerun after this skill was added.
- Implicit activation remains advisory and is not counted as a deterministic invocation path.
- Live Tavily tool discovery and one sanitized provider query are recorded at the agent-package release layer because the standalone skill does not install MCP configuration.
- Full live-source, commercial-evidence, upload-only-client, and complete artifact scenarios remain release-candidate coverage.
