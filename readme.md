# 1102tools Agent Skills

Eight portable agent skills for federal acquisition, market research, GovCon growth, SOW/PWS, IGCE, and Other Transaction workflows. These are not giant prompt files. Each capability is a complete, multi-file skill package with a compact orchestration core, supporting references, deterministic validators, client metadata, and its own test record.

Website: [1102tools.com](https://1102tools.com)

## The fastest install: hand this PDF to your AI

[![The 1102tools universal setup guide: one PDF for four agent plugins, eight MCP servers, and eight standalone skills. Repository-marketplace instructions cover Codex, Claude Code, and Copilot CLI; standalone setup covers major clients with tested surfaces and open limits stated. August 2026.](docs/setup-guide-promo.png?v=3)](https://1102tools.com/downloads/1102tools-universal-setup.pdf)

**[Download the universal setup guide (PDF)](https://1102tools.com/downloads/1102tools-universal-setup.pdf)**, then drop it into Claude, ChatGPT (Codex), Gemini (Antigravity), Copilot, DeepSeek Harness, Grok, Cursor, opencode, or LibreChat and say what you want installed. The AI reads the guide and walks you through agent marketplace installation, API keys, standalone configuration, restart, verification, updates, and removal. The guide distinguishes tested surfaces from pending ones.

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

**Install the entire skill directory, not only `SKILL.md`.** The references and scripts are part of the capability and its validation system. Upload-only clients may use a temporary local ZIP of one complete folder; this repository and website do not maintain separate skill ZIP releases.

## Companion repo: MCPs for API data

For federal API data (SAM.gov, BLS wages, GSA CALC+ rates, GSA Per Diem, USASpending, eCFR, Federal Register, Regulations.gov), use the companion repo:

**[federal-contracting-mcps](https://github.com/1102tools-dev/federal-contracting-mcps)**: eight MCP servers covering those APIs, installed with one config block per server in any MCP client.

The two repos work together: MCPs handle data, skills handle deliverables.

## Companion MCP safety release (August 2026)

The eight MCP servers now include synchronized cross-process anti-burst pacing. Default intervals are three seconds for SAM.gov, BLS OEWS, USASpending, GSA CALC+, eCFR, and Federal Register, and four seconds for GSA Per Diem and Regulations.gov. This is a 1102tools safety safeguard, not a provider quota guarantee, and it cannot coordinate the same key across different computers. Current package versions are listed in the companion repository and universal setup guide.

**Check any IGCE you built between roughly April and August 2026.** The BLS OEWS server was defaulting to a data year that BLS had withdrawn when it published the 2025 estimates. Wage lookups returned empty values rather than an error, which is indistinguishable from a privacy-suppressed cell. All three IGCE Builders and OT Cost Analysis price labor off that server. If an estimate from that window shows missing or suppressed wages, or you worked around them by hand, rebuild it.

**The April skills were also carrying the old vintage.** They hardcoded May 2024 as the BLS data vintage and computed the wage aging factor from it. Pairing an updated MCP with the old skill would age 2025 wages from a 2024 vintage, adding a full extra year of escalation. The vintage is now May 2025, and each pricing skill confirms it through the installed BLS operation rather than trusting a constant. Update the complete four pricing-skill folders if you still have an April copy.

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

> **August 21, 2026 modernization and expansion:** OpenAI Codex using GPT-5.6 Sol restructured the original six skills into portable, progressive-disclosure packages and added Market Research Builder and GovCon Growth Workflow as the seventh and eighth skills. The new launch gates were tested through explicit invocation in Codex CLI with GPT-5.6 Sol at xhigh and Claude Code CLI with Opus 5 at max effort plus Sonnet 5 smoke runs. Offline records, prompt-injection handling, numeric recomputation, LibreOffice conversion, citation extraction, and every rendered artifact page were checked. Each directory includes a current `test.md` with open coverage stated plainly.

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

### Research and growth

| Skill | Requires | Description |
|-------|----------|-------------|
| [Market Research Builder](skills/market-research-builder) | SAM.gov, USASpending, and approved web access for complete reports | Begins with a required workflow menu and separate acquisition-document intake, then produces evidence-backed FAR Part 10 findings or a validated report without originating reserved acquisition decisions. Web research can use optional Tavily, the host's native search, or both. |
| [GovCon Growth Workflow](skills/govcon-growth-workflow) | SAM.gov and USASpending; GSA CALC+ only for pricing context; approved web access by mode | Opportunity, bid-screen, competitor, recompete, teaming, agency-market, and pricing-context research for industry. Web research can use optional Tavily, the host's native search, or both. Public evidence alone never produces a bid decision. |

"Requires" lists the MCP servers each skill calls at runtime. Install them from the companion repo.

### Optional web providers and privacy

The two research skills are provider-aware but do not install a search service. Each research plan requires the user to choose Tavily with native fallback, native search only, Tavily only, or no public web before any search request. The plan shows the exact sanitized terms and public URLs first. Uploaded document text, proprietary or procurement-sensitive information, PII, CUI, private URLs, and credentials never enter a public search provider.

The GovCon Growth and Market Research agent packages configure Tavily's official keyless remote MCP. Tavily is a third-party service, not an 1102tools service, and its privacy terms apply. Standalone users may rely only on their host's native search or separately configure Tavily. Tavily is optional and is never the sole supported path.

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
