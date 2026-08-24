# 1102tools Agent Skills

Portable, host-neutral workflow packages for federal acquisition policy, market research, GovCon growth, SOW/PWS, IGCE, and Other Transaction work. These are not giant prompt files. Each capability is a complete, multi-file package with a compact orchestration core, supporting references, deterministic validators, client metadata, and its own test record.

Website: [1102tools.com](https://1102tools.com)

## Most users should start with an agent

The packaged [1102tools agents](https://github.com/1102tools-dev/federal-contracting-agents) combine the appropriate workflow and source integrations for one job. Some federal providers still require a free account or API key. The beginner-facing [HTML setup instructions](https://1102tools.com/setup) and [downloadable Agent Setup Guide](https://1102tools.com/downloads/1102tools-agent-setup-guide.pdf) cover Codex and Claude Code.

No 1102tools account is required. Market Research and GovCon Growth require `SAM_API_KEY` for SAM.gov work. Pre-Award and Other Transaction can use bounded BLS and Per Diem fallbacks without their optional keys. Acquisition Policy can use the bounded Regulations.gov `DEMO_KEY` fallback. Every affected workflow checks local credential presence before its menu or routed response, explains missing or limited access, and never asks for a key in chat. See [credential setup](https://1102tools.com/setup#credentials).

Use this repository when you specifically want to inspect, adapt, or install a standalone skill. Follow the selected skill directory's `SKILL.md` and its testing record; the agent setup guide does not cover standalone installation.

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

For federal API and published policy sources (SAM.gov, BLS wages, GSA CALC+ rates, GSA Per Diem, USASpending, eCFR, Federal Register, Regulations.gov, and Acquisition.gov), use the companion repo:

**[federal-contracting-mcps](https://github.com/1102tools-dev/federal-contracting-mcps)**: source-specific servers covering those federal systems, with advanced installation documented in the selected server directory.

The two repos work together: MCPs handle data, skills handle deliverables.

## Companion MCP safety release (August 2026)

The MCP servers include synchronized cross-process anti-burst pacing. Default intervals are three seconds for SAM.gov, BLS OEWS, USASpending, GSA CALC+, eCFR, Federal Register, and Acquisition.gov, and four seconds for GSA Per Diem and Regulations.gov. This is a 1102tools safety safeguard, not a provider quota guarantee, and it cannot coordinate the same key across different computers. Current package versions and setup details live in the companion repository.

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
4. **Tested source adapters.** The established MCP servers went through 3-6 audit rounds with live production-API testing. Acquisition.gov adds deterministic parser, PDF, transport, and security tests; its serialized live checks now pass against the RFO index, model text, an agency-deviation PDF, and published guidance.
5. **Cross-client support.** MCP is an open standard, so the same servers can run in multiple compatible local clients. This was the strongest argument for the split in April, when skills were Claude-only. It has since weakened: `SKILL.md` is now read by many runtimes too. The other four reasons still hold, and are why the split stays.

The orchestration skills in this repo stay as skills. Their value is decision trees, FAR-compliant narrative, and document generation, not API calls.

## The orchestration skills

> **August 2026 modernization and stable-agent release:** OpenAI Codex using GPT-5.6 Sol restructured the original six skills into portable, progressive-disclosure packages and added Market Research Workflow, GovCon Growth Workflow, and Acquisition Policy Workflow. All nine skills carry deterministic validation and their own evidence records. The five packaged agents that combine these skills with pinned source integrations are stable at `1.0.1`; standalone skill installation remains the advanced, self-supported path.

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
| [Market Research Workflow](skills/market-research-workflow) | SAM.gov, USASpending, and approved web access for complete reports | Begins with a required workflow menu and separate acquisition-document intake, then produces evidence-backed FAR Part 10 findings or a validated report without originating reserved acquisition decisions. Web research can use optional Tavily, the host's native search, or both. |
| [GovCon Growth Workflow](skills/govcon-growth-workflow) | SAM.gov and USASpending; GSA CALC+ only for pricing context; approved web access by mode | Opportunity, bid-screen, competitor, recompete, teaming, agency-market, and pricing-context research for industry. Web research can use optional Tavily, the host's native search, or both. Public evidence alone never produces a bid decision. |
| [Acquisition Policy Workflow](skills/acquisition-policy-workflow) | eCFR, Federal Register, Regulations.gov, and Acquisition.gov by mode | Routes clear policy questions directly and vague requests through a ten-choice menu. Keeps codified text, RFO model text, agency deviations, rulemaking status, and public comments separately classified, with an optional validated Acquisition Policy Impact Brief. |

"Requires" lists the MCP servers each skill calls at runtime. Install them from the companion repo and configure any applicable credential outside chat. SAM.gov is a hard credential requirement for its operations; BLS OEWS, GSA Per Diem, and Regulations.gov expose limited unauthenticated fallbacks.

### Optional web providers and privacy

The two research skills are provider-aware but do not install a search service. Each research plan requires the user to choose Native web only, Native web with Tavily fallback, Tavily only, or No public web before any search request. Native web only is recommended on the maintained Codex and Claude clients; Tavily remains an explicitly selected portability option. Ambiguous replies such as `OK` or `native` do not select a provider. No public web disables both public-web providers while preserving approved federal MCP and supplied-document research. The plan shows the exact sanitized terms and public URLs first. Uploaded document text, proprietary or procurement-sensitive information, PII, CUI, private URLs, and credentials never enter a public search provider.

The GovCon Growth and Market Research agent packages configure Tavily's official keyless remote MCP. Tavily is a third-party service, not an 1102tools service, and its privacy terms apply. Standalone users may rely only on their host's native search or separately configure Tavily. Tavily is optional and is never the sole supported path.

## Install

The cross-client [`skills`](https://skills.sh) installer can discover and install all nine complete skill packages directly from either the canonical GitHub repository or the 1102tools domain:

```bash
npx skills add 1102tools-dev/federal-contracting-skills
npx skills add https://1102tools.com
```

The domain source is published at [`/.well-known/agent-skills/index.json`](https://1102tools.com/.well-known/agent-skills/index.json). It identifies 1102tools as the publisher, links back to this repository and pins each downloadable archive with a SHA-256 digest. This is a machine-readable discovery and provenance surface; the GitHub repository remains the canonical source.

For manual installation:

1. Install [Claude Desktop](https://claude.ai/download), or use any supported runtime listed below.
2. Install the MCPs you need from [federal-contracting-mcps](https://github.com/1102tools-dev/federal-contracting-mcps). Each server's README has a copy-paste config block; add it to your client config and restart.
3. Add the complete skill directory. In Claude Desktop: **Customize > Skills > + > Create skill > Upload a skill**. Elsewhere, drop the unzipped folder into that runtime's skills directory:

| Runtime | Skills directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| opencode | `.opencode/skills/`, or a path in `skills.paths` |
| LibreChat | imports the `.zip` directly |

4. Ask naturally. The skill reads its instructions and calls the MCP tools.

The pricing skills need three MCP servers and a Python environment with `openpyxl` to produce their workbooks. A runtime with no code execution can read them but cannot finish the job.

## License

MIT

## Author

Built by [James Jenrette](https://www.linkedin.com/in/jamesjenrette/), lead systems analyst and contracting officer. Independently developed and not endorsed by any federal agency.
