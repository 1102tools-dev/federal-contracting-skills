# 1102tools Agent Skills

Agent skills for federal acquisition deliverables: SOW / PWS, IGCEs, OT project descriptions, OT cost analyses. Six orchestration skills that handle scope decisions, cost buildup, FAR citations, and document generation.

Website: [1102tools.com](https://1102tools.com)

## The fastest install: hand this PDF to your AI

[![The 1102tools universal setup guide: one PDF that installs everything. Drop it into the AI you already use and say what you want installed; it walks you through the free API keys, the exact config block for your platform, and how to verify the tools are live. Covers 11 platforms, install paths executed against the real clients, troubleshooting written from what actually broke. August 2026.](docs/setup-guide-promo.png)](https://1102tools.com/downloads/1102tools-universal-setup.pdf)

**[Download the universal setup guide (PDF)](https://1102tools.com/downloads/1102tools-universal-setup.pdf)**, then drop it into Claude, ChatGPT (Codex), Gemini (Antigravity), Copilot, DeepSeek Harness, Grok, Cursor, opencode, or LibreChat and say what you want installed. The AI reads the guide and walks you through every step: free API keys, the exact config for your platform, restart, verify. If 35 pages is more than your chat will accept, paste in just the section for your platform; every option is written to stand alone. Part 9 is troubleshooting built from errors we actually hit while executing every major install path for real.

![What a skill is, where they run, and what that means in practice. A skill is a folder with a SKILL.md file in it: written instructions your AI reads and follows, not code and not a plugin. These bundles load unmodified on Claude Desktop, Claude Code, Codex, Antigravity, Copilot, DeepSeek Harness, Grok, Cursor, opencode, and LibreChat. They were loaded and run in Claude Desktop, Claude Code, Codex, Antigravity, Copilot CLI, DeepSeek Harness, opencode, Grok, and LibreChat in August 2026; Cursor documents the same format but has not been tested here. On Copilot CLI the skill needed to be invoked by name to fire. Built and tested with Claude on Opus, and outputs are only verified there; runtimes with their own document capability fall through to it and still produce a real file.](docs/skills-explainer.png)

Runs on all of these, since the image above cannot be clicked: [Claude Desktop](https://claude.ai/download) &middot; [Claude Code](https://claude.com/claude-code) &middot; [Codex](https://openai.com/codex/) &middot; [Antigravity](https://antigravity.google) &middot; [Copilot](https://github.com/features/copilot) &middot; [DeepSeek Harness](https://deepseek.com/harness/en/) &middot; [Grok](https://x.ai/grok) &middot; [Cursor](https://cursor.com) &middot; [opencode](https://opencode.ai) &middot; [LibreChat](https://www.librechat.ai)

![Architecture diagram showing how each instrument chains scope, pricing, and data sources. FAR contracts: SOW/PWS Builder feeds three IGCE Builders (FFP, LH/T&M, Cost-Reimbursement) pulling from BLS OEWS, GSA CALC+, and GSA Per Diem. Other Transactions: OT Project Description Builder feeds OT Cost Analysis pulling from the same three data sources.](docs/architecture-v6.png)

**Before you build:** Not every acquisition capability should be an AI tool. Dozens of potential skills were evaluated and several were intentionally excluded because they cross the line from data assembly into professional judgment. See **[ai-boundaries.md](ai-boundaries.md)**.

## Companion repo: MCPs for API data

For federal API data (SAM.gov, BLS wages, GSA CALC+ rates, GSA Per Diem, USASpending, eCFR, Federal Register, Regulations.gov), use the companion repo:

**[federal-contracting-mcps](https://github.com/1102tools/federal-contracting-mcps)**: eight MCP servers covering those APIs, installed with one config block per server in any MCP client.

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

> **Model note:** Built and tested with Claude, on Opus. These are dense single-file skills, 10,000 to 18,000 tokens each, and that density is what smaller models struggle with: expect missed steps and wrong outputs. That is a model limitation, not a platform one. See the panel at the top for which runtimes read the format.

### FAR contracts

| Skill | Requires | Description |
|-------|----------|-------------|
| [SOW/PWS Builder](skills/sow-pws-builder) | — | Structured scope decision tree producing contract-file-ready SOW or PWS. FAR 37.102(d) compliant: staffing handoff for the IGCE Builder delivered as chat output, never embedded in the document body. |
| [IGCE Builder: FFP](skills/igce-builder-ffp) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | Firm-fixed-price IGCEs with layered wrap rate buildup (fringe, overhead, G&A, profit). |
| [IGCE Builder: LH/T&M](skills/igce-builder-lh-tm) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | Labor Hour and Time-and-Materials IGCEs with burden multiplier pricing. |
| [IGCE Builder: Cost-Reimbursement](skills/igce-builder-cr) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | CPFF, CPAF, CPIF IGCEs with fee structure analysis and statutory fee caps. |

### Other Transactions (OT)

| Skill | Requires | Description |
|-------|----------|-------------|
| [OT Project Description Builder](skills/ot-project-description-builder) | — | Milestone-based project descriptions for prototype OT agreements under 10 USC 4021/4022. Replaces the SOW/PWS for OTs: structures work around TRL progression phases and go/no-go gates. Handles NDC, small business, traditional (with cost sharing), and consortium-brokered agreements. |
| [OT Cost Analysis](skills/ot-cost-analysis) | BLS OEWS, GSA CALC+, GSA Per Diem MCPs | Should-cost estimates and price reasonableness analyses for OT agreements. Milestone-based pricing citing 10 USC 4021 instead of FAR 15.404. Handles cost-sharing math, consortium management fees, fixed-price and cost-type milestone payments. |

"Requires" lists the MCP servers each skill calls at runtime. Install them from the companion repo.

## Install

1. Install [Claude Desktop](https://claude.ai/download), or use any runtime from the panel above.
2. Install the MCPs you need from [federal-contracting-mcps](https://github.com/1102tools/federal-contracting-mcps). Each server's README has a copy-paste config block; add it to your client config and restart.
3. Add the skill. In Claude Desktop: **Customize > Skills > + > Create skill > Upload a skill**. Elsewhere, drop the unzipped folder into that runtime's skills directory:

| Runtime | Skills directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| DeepSeek Harness | `~/.dsh/skills/` or `~/.agents/skills/` |
| opencode | `.opencode/skills/`, or a path in `skills.paths` |
| LibreChat | imports the `.zip` directly |

4. Ask naturally. The skill reads its instructions and calls the MCP tools.

The pricing skills need three MCP servers and a Python environment with `openpyxl` to produce their workbooks. A runtime with no code execution can read them but cannot finish the job.

## License

MIT

## Author

Built by [James Jenrette](https://www.linkedin.com/in/jamesjenrette/), lead systems analyst and contracting officer. Independently developed and not endorsed by any federal agency.
