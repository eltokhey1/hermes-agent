# Hermes — 30 Claude Code Plugins & Skills: Candidate Source Register

**Recorded:** 2026-10-24 · **Status:** DESIGN / RESEARCH ONLY; NOT INSTALLED, TESTED OR PRODUCTION-INTEGRATED.
**Captured from:** user-provided infographic “Top 30 Claude Code Plugins”, attributed on image to **Charlie Hills**, annotated “counted 21/10/2026.” Original publication URL is **UNVERIFIED**. The picture's rankings and star counts are *unverified snapshots*, not measurements used for Hermes prioritization.
**Repository links:** checked for accessible public repository metadata through the GitHub connector on 2026-10-24 (30/30 names resolved). This proves repository existence only, **not authorship of the image, security, licenses, compatibility, actual plugins/skills packaging, quality, or install readiness**.

## Guardrails and scope
- Add as **candidates inside existing Hermes design/research backlog**, not 30 installed agents, 30 new top-level projects or a replacement for the canonical **45 work packages / 120 legacy IDs / 16 operational streams**.
- **No installs, cloning/executing third-party scripts, secrets, external sends, paid calls, scheduled jobs, CI triggers, merges, production deployments or `main` changes** from this registration.
- P0 owner-Windows inventory, restricted backup/functional restore and ACL/secret/budget/ESTOP negatives; then P1 durable effect ledger, UNKNOWN reconciliation, independent verifier and authenticated approvals must independently PASS before enabled tool integrations.
- Existing Hermes skills/plugins/CLI are first reuse target. The local executor stays Hermes/Aider/Ollama where accepted; cloud models may only propose/review within explicit privacy and cost gates.
- A skill's `SKILL.md` and code are untrusted third-party content: inspect source, pin commit, review license, malware supply-chain risk, hooks, MCP privileges, network/data destinations, telemetry, update behavior and denial/fail-closed cases.
- Browser/desktop controls remain privileged even for nominally read-only work; no access to owner browser sessions, confidential mail, logged-in portals or company files without separate approval.

## Complete 30-item register

**Status meanings:** `REUSE` = architectural principle already in design, not proof of install; `REVIEW` = bounded offline priority; `CONDITIONAL` = only when specific project needs it; `DEFER` = no proven ROI or overlapping stack; `HOLD_PRIVILEGED` = stronger isolation/approval prerequisite.

| # | Infographic label | Candidate source (GitHub) | Job | Hermes triage | Benefit / primary gate |
|---|---|---|---|---|---|
| 01 | superpowers | [obra/superpowers](https://github.com/obra/superpowers) | Engineering workflow | `REVIEW` | TDD, planning, debugging; overlaps existing Hermes/Aider practices |
| 02 | matt-pocock-skills | [mattpocock/skills](https://github.com/mattpocock/skills) | Engineering workflow | `REVIEW` | Typed specs, code review, small reusable skills; check existing Ponytail rules |
| 03 | ECC | [affaan-m/ECC](https://github.com/affaan-m/ECC) | Engineering workflow | `DEFER` | Large multi-agent skill and hook bundle; audit all hooks and collisions before evaluation |
| 04 | ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Engineering workflow | `REUSE` | Minimal-diff principles already selected in Hermes design; verify actual local installation |
| 05 | agent-skills | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Engineering workflow | `REVIEW` | Spec, build, test, review; choose only non-overlapping skills |
| 06 | planning-with-files | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | Engineering workflow | `REVIEW` | Persistent task plans; do not create second canonical portfolio registry |
| 07 | ui-ux-pro-max | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI / visual | `CONDITIONAL` | Dashboard design and accessibility evals; inspect executable tooling |
| 08 | taste-skill | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | UI / visual | `CONDITIONAL` | Interface quality and style review; avoid duplicate UI skills |
| 09 | understand-anything | [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | UI / visual | `CONDITIONAL` | Codebase concept maps; assess value versus existing static analyzers |
| 10 | hyperframes | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | UI / visual | `DEFER` | HTML/video generation; no immediate TradeOps ROI path |
| 11 | diagram-design | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | UI / visual | `REVIEW` | Architecture diagrams and editorial SVGs; output-only, no privileged tools |
| 12 | frontend-slides | [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) | UI / visual | `CONDITIONAL` | Editable/browser slides for commercial presentations; review security/format |
| 13 | caveman | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Memory / context | `CONDITIONAL` | Compressed responses; verify technical precision and safety language |
| 14 | claude-mem | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | Memory / context | `DEFER` | Session memory; prefer existing durable state and evaluate privacy/retention |
| 15 | headroom | [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | Memory / context | `CONDITIONAL` | Context efficiency; instrument real cost/quality baseline first |
| 16 | context-mode | [mksglu/context-mode](https://github.com/mksglu/context-mode) | Memory / context | `CONDITIONAL` | Reduce context overhead; compare to native compaction |
| 17 | beads | [gastownhall/beads](https://github.com/gastownhall/beads) | Memory / context | `CONDITIONAL` | Agent task memory; avoid parallel source of truth for task IDs |
| 18 | claude-obsidian | [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | Memory / context | `DEFER` | Obsidian knowledge workspace; not justified without an owner vault use case |
| 19 | last30days | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | Research / marketing | `CONDITIONAL` | Fresh trend research for Revenue Radar; sources and dated claims required |
| 20 | humanizer | [blader/humanizer](https://github.com/blader/humanizer) | Research / marketing | `CONDITIONAL` | External communication drafts; human approval prior to publication |
| 21 | marketingskills | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | Research / marketing | `CONDITIONAL` | Growth, positioning, CRO research; no automated outreach |
| 22 | academic-research | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | Research / marketing | `CONDITIONAL` | Research workflows with source provenance; no unsupported facts |
| 23 | pm-skills | [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | Research / marketing | `CONDITIONAL` | PRDs, prioritization and pilot framing; avoid planning duplication |
| 24 | claude-seo | [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | Research / marketing | `CONDITIONAL` | SEO/AEO content for export business; approval prior to public changes |
| 25 | chrome-devtools-mcp | [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Agent tools / control | `HOLD_PRIVILEGED` | Browser debugging; isolate profile and block sensitive authenticated actions |
| 26 | oh-my-claudecode | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) | Agent tools / control | `DEFER` | Alternative orchestration/swarm; duplicates governed Hermes core |
| 27 | claude-hud | [jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud) | Agent tools / control | `CONDITIONAL` | Session/tool/cost visibility; avoid runtime overhead without measured benefit |
| 28 | browser-harness | [browser-use/browser-harness](https://github.com/browser-use/browser-harness) | Agent tools / control | `HOLD_PRIVILEGED` | Browser automation; sandbox, read-only default and approval for writes |
| 29 | ego-lite | [citrolabs/ego-lite](https://github.com/citrolabs/ego-lite) | Agent tools / control | `CONDITIONAL` | Browser harness option; compare with existing browser tools, select one |
| 30 | desktop-commander | [wonderwhy-er/DesktopCommanderMCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) | Agent tools / control | `HOLD_PRIVILEGED` | Shell/filesystem MCP access; explicit allowlist and isolated low-privilege user |

## Smallest viable evaluation sequence
1. **Inventory/deduplicate:** compare existing Hermes skills/plugins and the accepted Agent Skills Hub / Ponytail 5 policies. Do not install multiple overlapping orchestration suites (Superpowers, ECC, agent-skills, oh-my-claudecode) by default.
2. **Sandbox-only first comparison:** one workflow pack (`superpowers` **or** selected `mattpocock/skills` / `agent-skills`) plus `diagram-design` on synthetic data, each *one at a time*, against the baseline. `ponytail` principles are already selected; check real installed state.
3. **Optional UI/content research:** `ui-ux-pro-max`, `taste-skill`, `frontend-slides`, `marketingskills`, `last30days`, `claude-seo` only for a measurable user/project deliverable and with exact provenance.
4. **Memory and agent-control add-ons:** start with existing state/evidence. Compare `claude-mem`, `beads`, `context-mode`, `headroom` only if recall/context evals show a gap. Privileged `desktop-commander`, `browser-harness`, `chrome-devtools-mcp` require an approved sandbox/identity/permission boundary before even pilot integration.
5. **Gate for any promotion:** provenance + license review; negative tests (prompt injection, unauthorized file/network action, secrets leakage, stale approvals); impact measurement vs baseline; independent acceptance and a separate owner authorization.

## Economics and measurement contract
**No verified paid price, latency, acceptance rate or savings is available yet.** Do not import popularity-based ROI assumptions. Record measured baseline and post-change for at least 30 representative, non-sensitive tasks per accepted use case, preferably more for risky tools.

Metrics: `success_rate`, `p50/p95_latency_ms`, `tokens_per_success`, `cost_per_success_usd`, `failed_tool_calls`, `security_violation_count`, `review_minutes_saved`, `license_cost_usd`, `monthly_fixed_cost_usd`; report at 1k/10k/100k monthly tasks using **documented** assumptions. Candidate promotion target: **zero unauthorized actions and zero leaked canary secrets**, no degradation in critical correctness; quantify time/cost saved and project revenue link before paid adoption. Any quantitative improvement threshold is a proposed gate until Hermes baselines are measured.

## Source attribution and reconciliation
- Infographic: user-supplied image; visual byline **Charlie Hills**. Public original URL **unknown/unverified**. The ordering above follows the screenshot, not an independent popularity ranking.
- Primary repository links: all 30 are recorded in the register; source identity is an *initial match*, not verified software provenance or endorsement.
- Source specification for skill packs: https://agentskills.io/specification
- Existing Hermes design record: `ops/portfolio/BUSINESS_PORTFOLIO_RESEARCH_BACKLOG_2026-10-18.md` in draft PR #6.
- Representative official vendor context: https://github.com/obra/superpowers (Hermes plugin instructions present in README); https://github.com/mattpocock/skills ; https://github.com/addyosmani/agent-skills ; https://github.com/ChromeDevTools/chrome-devtools-mcp.
- **Canonical integration discipline:** This is a *candidate reference list*, not new deployed modules. All features remain subject to independent Windows P0/P1 evidence and the approved Hermes portfolio registry.
