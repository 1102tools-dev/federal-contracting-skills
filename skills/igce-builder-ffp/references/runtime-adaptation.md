# Runtime Adaptation

Use capabilities rather than product names in the main workflow. This reference explains how to adapt questions, tools, files, and workbook calculation without forking the skill.

## Structured questions

When the host exposes a structured question or user-input tool, use it for short, mutually exclusive choices. Otherwise:

1. Present numbered options in chat.
2. Accept a number, label, or free-text correction.
3. Preserve the staged-question gates.
4. End the response at the question when the workflow requires a pause.

Do not mention a host-specific function name in user-facing instructions.

## MCP tool discovery

Inspect the operations exposed in the session. Match these stable server and operation names:

- `bls-oews`: `detect_latest_year`, `get_wage_data`, `igce_wage_benchmark`, `list_common_metros`, `list_common_soc_codes`
- `gsa-calc`: `suggest_contains`, `exact_search`, `keyword_search`, `igce_benchmark`, `price_reasonableness_check`
- `gsa-perdiem`: `estimate_travel_cost`, `lookup_city_perdiem`, `get_mie_breakdown`

Hosts may add namespaces or separators around an MCP operation. Treat those wrappers as runtime details. Never copy a full host-generated name into the workbook or Methodology.

If a stable operation is not exposed, inspect available schemas for an equivalent operation on the same server. If none exists, stop and report the missing dependency. Do not hand-build an API request as an undocumented substitute.

## Python and openpyxl

Confirm that the runtime can execute Python and import openpyxl before workbook construction. If not, explain that the skill can prepare the estimate data but cannot finish the `.xlsx` artifact in that runtime.

Use the skill-local scripts with paths resolved relative to the skill directory. Do not assume a global skill root.

## Spreadsheet calculation

Openpyxl writes and inspects formulas but does not evaluate them. Use this order:

1. Prefer a real spreadsheet engine available to the runtime.
2. On macOS or Linux, detect `soffice` or the LibreOffice application executable.
3. Recalculate a temporary copy, never the only copy of the user's workbook.
4. Reopen the recalculated copy with `data_only=True` and compare the cached results with the independent Python recomputation.
5. If no engine is available, run structural and independent checks and disclose that formula execution was not independently verified.

Do not claim that opening a workbook will necessarily recalculate it. That behavior depends on the receiving application and its calculation settings.

## File locations and delivery

Choose the destination in this order:

1. A path supplied by the user
2. A writable output directory provided by the host
3. The current project or working directory

Use the host's attachment or artifact-presentation capability when it exists. Otherwise return the absolute path. Do not assume a particular sandbox directory, presentation function, or OS-specific open command exists.

Confirm the file exists before reporting success. Do not overwrite a user file unless the user requested that exact target.

## Validation disclosure

Report the layers that actually ran:

- Formula-structure audit
- Independent mathematical recomputation
- LibreOffice or Excel execution verification

When the third layer did not run, use this exact statement:

> Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.
