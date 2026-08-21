# 1102tools Agent Skills

Portable agent skills for federal acquisition deliverables: SOW / PWS, IGCEs, OT project descriptions, and OT cost analyses. These are not six giant prompt files. Each capability is now a complete, multi-file skill package with a compact orchestration core, supporting references, deterministic validators, client metadata, and its own test record.

Website: [1102tools.com](https://1102tools.com)

## The fastest install: hand this PDF to your AI

[![The 1102tools universal setup guide: one PDF for two agent plugins, eight MCP servers, and six standalone skills. Repository-marketplace instructions cover Codex, Claude Code, and Copilot CLI; standalone setup covers major clients with tested surfaces and open limits stated. August 2026.](docs/setup-guide-promo.png?v=3)](https://1102tools.com/downloads/1102tools-universal-setup.pdf)

**[Download the universal setup guide (PDF)](https://1102tools.com/downloads/1102tools-universal-setup.pdf)**, then drop it into Claude, ChatGPT (Codex), Gemini (Antigravity), Copilot, DeepSeek Harness, Grok, Cursor, opencode, or LibreChat and say what you want installed. The AI reads the guide and walks you through agent marketplace installation, free API keys, exact standalone configuration, restart, verification, updates, and removal. If 39 pages is more than your chat will accept, paste in just the section for your platform; every option is written to stand alone. The guide distinguishes tested surfaces from pending ones, and Part 9 is troubleshooting built from errors I actually encountered.

![Architecture diagram showing how each instrument chains scope, pricing, and data sources. FAR contracts: SOW/PWS Builder feeds three IGCE Builders (FFP, LH/T&M, Cost-Reimbursement) pulling from BLS OEWS, GSA CALC+, and GSA Per Diem. Other Transactions: OT Project Description Builder feeds OT Cost Analysis pulling from the same three data sources.](docs/architecture-v6.png)

**Before you build:** Not every acquisition capability should be an AI tool. Dozens of potential skills were evaluated and several were intentionally excluded because they cross the line from data assembly into professional judgment. See **[ai-boundaries.md](ai-boundaries.md)**.

## A skill is now a package, not a single Markdown file

The April releases concentrated each workflow into one dense `SKILL.md`, with some pricing skills reaching roughly 10,000 to 18,000 tokens. That worked, but it made every instruction compete for context at once and mixed orchestration, reference material, platform handling, workbook specifications, and validation rules in one file.

The August modernization replaces that monolith with progressive disclosure. Each skill is a directory that looks like this:

```text
skill-name/
├── SKILL.md                 compact workflow, decisions, and load-bearing gates
├── references/              detailed rules and specifications loaded when needed
├── scripts/                 deterministic workbook or document validators
├── agents/
│   └── openai.yaml          OpenAI client display and invocation metadata
├── test.md                  current cross-model and artifact test record
└── testing.md               historical test record, where one already existed
```

This separation is functional, not cosmetic:

1. **The core stays focused.** `SKILL.md` contains workflow selection, staged questions, professional-judgment boundaries, and the correctness gates that must survive context pressure.
2. **Detail is loaded when it is relevant.** Contract-type rules, data-source operations, workbook layouts, document specifications, runtime adaptation, and extended validation assertions live one level down in `references/`.
3. **Correctness does not depend only on model prose.** Pricing skills include independent recomputation and formula-structure checks. Document skills include DOCX structure, separation, TOC, placeholder, and table checks.
4. **Claude and Codex use the same skill body.** Runtime-specific behavior is expressed through capability-based instructions and optional client metadata rather than maintaining separate Claude and Codex forks.
5. **The evidence ships with the skill.** Every directory includes `test.md` describing the models, clients, fixtures, injected faults, results, and remaining open coverage.

The result is still simple to install: copy or upload one skill folder. Internally, however, it is a tested capability package rather than a long prompt wearing a skill name.

**Install the entire skill directory or ZIP, not only `SKILL.md`.** The references and scripts are part of the capability and its validation system.

## Companion repo: MCPs for API data

For federal API data (SAM.gov, BLS wages, GSA CALC+ rates, GSA Per Diem, USASpending, eCFR, Federal Register, Regulations.gov), use the companion repo:

**[federal-contracting-mcps](https://github.com/1102tools-dev/federal-contracting-mcps)**: eight MCP servers covering those APIs, installed with one config block per server in any MCP client.

The two repos work together: MCPs handle data, skills handle deliverables.

## Companion MCPs updated to 1.0.0 (August 2026)

The MCP servers these skills call were rebuilt on v2 of the MCP Python SDK and published at 1.0.0. **Update them**, then read the two notes below, because both affect estimates you may already have produced.

**Check any IGCE you built between roughly April and August 2026.** The BLS OEWS server was defaulting to a data year that BLS had withdrawn when it published the 2025 estimates. Wage lookups returned empty values rather than an error, which is indistinguishable from a privacy-suppressed cell. All three IGCE Builders and OT Cost Analysis price labor off that server. If an estimate from that window shows missing or suppressed wages, or you worked around them by hand, rebuild it.

**The skills in this repo were also carrying the old vintage.** They hardcoded May 2024 as the BLS data vintage and computed the wage aging factor from it. Pairing an updated MCP with the old skill would age 2025 wages from a 2024 vintage, adding a full extra year of escalation and overstating every labor line by roughly one year of your escalation rate. The vintage is now May 2025, and each pricing skill carries a standing instruction to confirm it with `detect_latest_year()` before pricing rather than trusting the constant. **Re-download the four pricing skills.**

Apologies to anyone who lost time to either one. The MCP-side detail is in each server's `changelog.md`.

**`.mcpb` bundles are discontinued.** They could not be signed in a way Claude Desktop recognizes, so every install raised an untrusted-developer prompt, and they re-resolved dependencies on each launch instead of pinning them. Install via the config block in the companion repo instead.

## Why the split

The five API data-source skills (BLS OEWS, GSA CALC+, GSA Per Diem, SAM.gov, USASpending) were removed from this repo in April 2026. They moved to the MCP companion repo.

**Reasons:**

1. **Deterministic tool calls.** MCP servers execute tested Python code. The model does not generate API-call code on the fly. Skills drifted across runs; MCPs do not. Same input, same output.
2. **Updated independently of the skills.** When an upstream API changes, the MCP ships a fix and you get it on the next launch. Nothing to re-upload. A data-source skill would have to be re-downloaded and re-installed by every user.
3. **Less context cost.** Tool schemas are ~100 tokens each. The old API skills cost 500-1000 lines of context per run.
4. **Production-hardened.** Each MCP went through 3-6 audit rounds with live testing against the production API. Roughly 350 bugs fixed during hardening across the eight MCPs.
5. **Cross-client support.** MCP is an open standard, so the same servers run in Claude Desktop, Claude Code, Codex, Antigravity, and Copilot. This was the strongest argument for the split in April, when skills were Claude-only. It has since weakened: `SKILL.md` is now read by nearly every runtime too. The other four reasons still hold, and are why the split stays.

The orchestration skills in this repo stay as skills. Their value is decision trees, FAR-compliant narrative, and document generation, not API calls.

## The orchestration skills

> **August 21, 2026 modernization:** OpenAI Codex using GPT-5.6 Sol restructured all six skills into portable, progressive-disclosure packages while preserving the correctness gates from the original test program. Behavioral gates were tested with explicit invocation in Codex CLI using GPT-5.6 Sol at xhigh reasoning and Claude Code CLI using Opus 5. FFP also received claude.ai Opus 5 Max and Codex Desktop coverage. Pricing fixtures passed formula-structure audits, independent Python recomputation, and LibreOffice formula execution. Document fixtures passed deterministic validation and all-page rendering review. Every skill directory includes a current [`test.md`](skills/igce-builder-ffp/test.md); open coverage and client-specific limitations are recorded there. Explicit invocation remains the deterministic CLI test path.

### FAR contracts

| Skill | Requires | Description |
|-------|----------|-------------|
| [SOW/PWS Builder](skills/sow-pws-builder) | None | Structured scope decision tree producing a contract-file-ready SOW or PWS. Applies the results-oriented PWS standard in FAR 37.602(b)(1), while keeping staffing and Section B handoffs in chat rather than the document body. |
| [IGCE Builder: FFP](skills/igce-builder-ffp) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | Firm-fixed-price IGCEs with layered wrap rate buildup (fringe, overhead, G&A, profit). |
| [IGCE Builder: LH/T&M](skills/igce-builder-lh-tm) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | Labor Hour and Time-and-Materials IGCEs with burden multiplier pricing. |
| [IGCE Builder: Cost-Reimbursement](skills/igce-builder-cr) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | CPFF, CPAF, CPIF IGCEs with fee structure analysis and statutory fee caps. |

### Other Transactions (OT)

| Skill | Requires | Description |
|-------|----------|-------------|
| [OT Project Description Builder](skills/ot-project-description-builder) | None | Milestone-based project descriptions that distinguish Research OTs under 10 U.S.C. 4021, Prototype OTs under 10 U.S.C. 4022, and follow-on production under 10 U.S.C. 4022(f). Uses observable maturity evidence and go/no-go gates without forcing TRLs onto every project. |
| [OT Cost Analysis](skills/ot-cost-analysis) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | Should-cost estimates and neutral price comparisons for OT agreements. Handles authority-specific contribution rules, consortium fees, fixed-price and cost-type milestones, and proposed-amount normalization without originating the Agreements Officer's determination. |

"Requires" lists the MCP servers each skill calls at runtime. Install them from the companion repo.

## Install

1. Install [Claude Desktop](https://claude.ai/download), or use any supported runtime listed below.
2. Install the MCPs you need from [federal-contracting-mcps](https://github.com/1102tools-dev/federal-contracting-mcps). Each server's README has a copy-paste config block; add it to your client config and restart.
3. Add the skill. In Claude Desktop: **Customize > Skills > + > Create skill > Upload a skill**. Elsewhere, drop the unzipped folder into that runtime's skills directory:

| Runtime | Skills directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| DeepSeek Harness | `~/.dsh/skills/` or `~/.agents/skills/` |
| opencode | `.opencode/skills/`, or a path in `skills.paths` |
| LibreChat | imports the `.zip` directly |

4. Ask naturally. The skill reads its instructions and calls the MCP tools.

The pricing skills need three MCP servers and a Python environment with `openpyxl` to produce their workbooks. A runtime with no code execution can read them but cannot finish the job.

## License

MIT

## Author

Built by [James Jenrette](https://www.linkedin.com/in/jamesjenrette/), lead systems analyst and contracting officer. Independently developed and not endorsed by any federal agency.
