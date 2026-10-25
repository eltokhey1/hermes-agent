# Hermes Portfolio Control Tower — October 18, 2026

**REVIEW ONLY — NOT PRODUCTION READY.**

This is a **portfolio overlay**, not a second task queue. **The authoritative Hermes portfolio consists of 45 work packages across 16 streams, preserving 120 historical identifiers.** The 32 items in [MASTER_IMPLEMENTATION_MATRIX.csv](./MASTER_IMPLEMENTATION_MATRIX.csv) are engineering acceptance tasks/subgates mapped into the same 45-package portfolio, **not 32 additional work packages**. Likewise, V1 detail rows (44), Task Register entries (34), V6 next actions (26) and research entries (23) must not be added to the 45-package count. Supplemental IDs MUST be qualified by source (SOURCE::ID) to avoid 14 known semantic collisions. Acceptance rules remain in [READINESS_DECISION_POLICY.md](./READINESS_DECISION_POLICY.md). Windows P0/P1 formal gates remain UNVERIFIED/HOLD.

## Seven linked programs

| Program | Reuse rather than duplicate | Gate / next decision |
|---|---|---|
| A. Hermes Core & Security | P0/P1 (18 canonical tasks), draft PRs #4/#5/#7 | Local read-only inventory; encrypted custody; **functional isolated restore**, fail-closed, budget |
| B. Hermes Cloud & Bridge | Draft PR #8; cloud local V3; separate Hermes Bridge v0.4 | VM/Gemini/Gateway **NOT DEPLOYED**; preview Terraform/IAM/cost, do not apply; Bridge not integrated |
| C. Trade / Maritime Intelligence | Draft PR #1 and P3-03 | BL/HBL, carrier events, AIS, ETA/confidence; **never infer container state from AIS alone** |
| D. GCC Revenue & SaaS | Draft PRs #6/#9, P3-01/P3-02/P3-04 | Procurement/Supplier Intelligence → Shipment → ExportLead; Saudi/UAE; available startup capital up to $1,000 is **not authorized spend** |
| E. Viral Kit / CRM / Content | Reuse P1 evidence/permissions before autonomous tools | Scope real version and tests, no outbound messages/publishing without separate approval |
| F. Agent / Workflow Research Radar | Draft PRs #6/#9 and P1-06 | Single source registry: trace → verify → dedupe → benchmark → adopt/reject |
| G. Quant / Trading Research | Isolated research only | Simulation; no brokerage, live trading, or real money |

## No duplicate initiatives

- **#4** owns readiness tasks and approval truth.
- **#5** supplies an evidence-validator *candidate*, not production proof.
- **#6 and #9** must be deduplicated into one research/evidence view before any integration.
- **#8** is a cloud-design draft; its offline tests do not prove Google Cloud deployment.
- **#1** is a TradeOps design/prototype, not a live shipping deployment.
- **#2 and #3** are optional/deferred specialist reviews.
- **#7** is a candidate read-only preflight, not evidence of a Windows run.
- Keep all these PRs in **Draft**; no main merge or runtime changes by this plan.

## Decision sequence

1. **P0:** inspect true Windows checkout/dirty state → encrypted backup/off-device custody → functional isolated restore → least privilege, timeout/empty/malformed/network DENY, leak canary, hard $0 spend baseline.
2. **P1:** durable pre-action intent → PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN and no blind retry → bound approvals → progress watchdog → trustworthy evidence and red-team tests → independent go/no-go.
3. **P2:** data/provenance, scoped MCP/tools, model routing and events only when measured.
4. **P3:** customer problem validation and tightly gated Trade/Revenue/Viral pilots.
5. **P4:** resilience/counterfactuals/self-improvement behind regression and approval gates.

**Safe independent parallel work now:** public research and market qualification; design-only shipment source schema; Cloud Terraform plan review; tool/source radar dedup. **Blocked:** Windows mutation without secure audit/restore, paid Google resources without scoped cost approval, secrets into public GitHub, public Gateway, outbound messaging/publishing/trades.

## Working operating model

Observe → Verify → Predict → Economics → Risk → Plan → Human Approval → Sandbox/Execute → Audit → Learn. These are logical responsibilities under **Hermes Core**, not authorization for a competing free-form multi-agent OS.

New ideas go to an INBOX, are deduplicated against a canonical task ID/PR, receive dependencies + measurable evidence, then move through DESIGN_ONLY → IMPLEMENTED → TESTED → VERIFIED. Runtime UNKNOWN means stop and reconcile, **never automatically retry an uncertain external effect**. Product income claims require observed receipts/outcomes, not forecasts.

The full Arabic portfolio handbook and spreadsheet are exported as a separate review package outside the public repo; **do not upload private paths, log contents, keys, customer data, backup archives or Terraform state to GitHub**.

## Product Hunt October 2026 — research-only mapping

**Snapshot date: 2026-10-18; non-authoritative for final monthly positions.** The requested [monthly leaderboard](https://www.producthunt.com/leaderboard/monthly/2026/10) was not directly retrievable in the review environment. Candidates below were cross-checked against individual Product Hunt product pages and [official week-42 leaderboard](https://www.producthunt.com/leaderboard/weekly/2026/42). No votes, reviews, followers, or positions prove revenue, product-market fit, enterprise readiness, or GCC buyer demand.

This is a **source-intake overlay** to the 32 canonical task IDs in `MASTER_IMPLEMENTATION_MATRIX.csv`, **not** a new task queue or dependency change. Do not install any candidate based on Product Hunt publicity.

| Candidate | Existing problem / portfolio track | Existing task IDs | Phase decision | Source |
|---|---|---|---|---|
| Pancake | ExportLead / sales GTM infra reference | P3-02, P3-04 | Research-only; no sending | https://www.producthunt.com/products/pancake-6 |
| ReSO AI | GCC generative-search visibility hypothesis | P3-01, P3-02 | Research-only; validate paid demand | https://www.producthunt.com/products/reso |
| Formalini | TradeDocs / document data extraction | P3-01, P2-02 | Sanitized-data validation candidate | https://www.producthunt.com/products/formalini |
| GenPage 3.0 | Landing-page experiment for marketing/Viral Kit | P3-02 | Research-only; no ad spend | https://www.producthunt.com/products/genpage |
| Articos MCP | Simulated buyer messages | P3-01, P3-02 | Advisory only; never substitute actual interviews | https://www.producthunt.com/products/articos |
| Navige | Hard budget/kill switch/reference for orchestration | P0-07, P2-04 | Security evaluation later; no agent proxy | https://www.producthunt.com/products/navige |
| Inferock | Independent call-cost receipts and observability | P1-05, P2-05 | Design reference, not validated integration | https://www.producthunt.com/products/inferock |
| Harness by Autonomous | Multi-device coding-agent control | P2-03, P1-03 | Security review later; no remote-control deploy | https://www.producthunt.com/products/harness-by-autonomous |
| IrisGo | Watch-and-learn workflow UX | P2-03, P3-05 | UX benchmark only; preserve existing Hermes core | https://www.producthunt.com/products/irisgo-public-beta |
| OpenSwarm | Parallel agent operating environment | P4-03, P1-09 | Deferred; no company-OS replacement | https://www.producthunt.com/products/openswarm-3 |
| Polylane | Proposed PR and incident-risk evidence | P1-05, P4-02 | Optional review only | https://www.producthunt.com/products/polylane |
| Spira Maxima | Creative/video content signal | P3-01, P3-02 | Later research; no autopublish | https://www.producthunt.com/products/spira-ai |

**Commercial acceptance rule:** Each candidate needs a real buyer-problem hypothesis, validated source/legal right, cost and privacy review, and actual customer evidence (interviews, verified pain points, or payment intent) before it can enter a project-specific pilot. Track forecasts separately from actual revenue and reject purely vote-based scoring. All sensitive customer information stays out of this public repository.

**No-go remains unchanged:** All P0/P1 runtime gates UNVERIFIED, `PRODUCTION_READY=NO`. `main` remains untouched, and this PR remains Draft. Maintain the existing active weekly research radar rather than creating duplicate automations.

## Product Hunt 2026 year-to-date — additive, deduplicated research

**Source checked: 2026-10-18.** [Product Hunt yearly 2026](https://www.producthunt.com/leaderboard/yearly/2026) is a **year-to-date live listing**, not a finished annual award or verified sales ranking. Lists/crawl snapshots can differ and show promoted placements. Do not assert a fixed annual #rank or treat vote counts as income, verified users, or profitability. Official product pages clarify the promoted feature claims; customer and pricing claims need independent checks.

**Dedup protocol:** The [October 2026 signals](#product-hunt-october-2026--research-only-mapping) already cover 12 product references. The following annual scan adds only *new product names* to the same P0–P4 task IDs; it does not add a separate engineering task matrix or authorize install.

| YTD candidate | Why it matters | Canonical task / program | Scope and test gate | Primary evidence |
| --- | --- | --- | --- | --- |
| Lightfield | AI-native CRM reconstructing context from meetings, email and calls | P3-01, P3-02 / Viral Kit CRM, ExportLead | Compare read-only CRM extract and human-reviewed matching; no blanket mailbox scope | https://www.producthunt.com/products/lightfield |
| Upstream | Email inbox designed for people and agents | P1-03, P2-03 / Shipping email, TradeOps | `Mail.Read` only until separate authorized human approval for writes; no Cookie transfer | https://www.producthunt.com/products/upstream-3 |
| Kilo Code for VS Code | Parallel coding agents and diff review | P1-05, P1-06, P4-03 / Core | Independent PR review idea only, no agent tool install or autonomous merge | https://www.producthunt.com/products/kilocode |
| KiloClaw | Managed hosting for OpenClaw | P2-03, P0-07 / Cloud Hermes | Architecture/cost/security comparison only; *not* proof Hermes hosting is solved | https://www.producthunt.com/products/kiloclaw |
| DataFast | Revenue-attributed web analytics | P3-04 / GCC Revenue | Plan event-to-revenue measurement, but distinguish declared vs actual sales | https://www.producthunt.com/products/datafast |
| OpenSEO | AI-friendly SEO/GEO research with MCP integrations | P3-02, P2-03 / Commercial Radar, Viral | Compare to October ReSO before any duplicate subscription; assess license and privacy | https://www.producthunt.com/products/openseo |
| SEORCE | Search/GEO brand discovery analytics | P3-02 / Viral, commercial research | Competes with OpenSEO/ReSO concept: evaluate as one SEO/GEO cluster, **not three independent projects** | https://www.producthunt.com/products/seorce |
| Livedocs | General data agent | P2-02, P3-03 / Evidence, shipping | Look at provenance/joins of heterogeneous data; never infer cargo events from vessel AIS | https://www.producthunt.com/products/livedocs-2 |
| Atlas.new | Spatial data/map agent | P3-03 / Maritime intelligence | Optional map UX reference only; not authoritative port or vessel tracking | https://www.producthunt.com/products/atlas-co-2 |
| Instruct 2.5 | Cross-app task automation | P2-03, P1-03 / Integration | Compare to shipped Hermes skills/cron; require scoped identity and fail-closed denial | https://www.producthunt.com/products/instruct-2 |
| PostSyncer | Content marketing/publishing assistant | P3-01, P3-02 / Viral Kit | Candidate only, no auto-posting/outbound without authenticated approval | https://www.producthunt.com/products/postsyncer-2 |
| Cowork (Claude) | Delegate work to an AI coworker | P2-03, P1-05 / Cloud design | Evaluation reference for independent review, context and tool approval; never replace core by default | https://www.producthunt.com/products/claude |
| Framer AI Agents / Framer 3.0 | AI-managed web design/branching and publishing | P3-05, P4-03 / UI & controlled release | Study branching/approval UX, no one-click production publication | https://www.producthunt.com/products/framer |
| Fundraisly | AI investor discovery and meeting booking | P3-01, P3-04 / Commercial Radar | Only evaluate if verified buyer demand for fundraising, not current priority for GCC B2B services | https://www.producthunt.com/leaderboard/yearly/2026 |

**Cluster consolidation (prevents roadmap inflation):**
1. **CRM/email/context:** Lightfield + Upstream + October Pancake → *one* customer-workflow opportunity intake (P3-01/02), and one security boundary (P1-03). Do not implement multiple CRMs in Hermes.
2. **SEO/GEO/marketing:** OpenSEO + SEORCE + ReSO + October GenPage → *one* buyer-demand hypothesis for a GCC service. No subscription or content publication until proof of payment intent.
3. **Agent harness / coding / hosting:** Kilo Code + KiloClaw + Cowork + October Harness/IrisGo → reuse Hermes built-in capabilities; defer to P1 evidence and P2 integration benchmarks.
4. **Trade data & maps:** Livedocs + Atlas.new + Formalini → separate immutable raw carrier records, document extraction and derived AIS/ETA estimates; no inferred container discharge from AIS.
5. **Revenue measurement:** DataFast → P3-04 **actual-outcome ledger**, and P0-07 hard spend cap. A Product Hunt vote is a discovery metric, not commercial validation.

**Commercial ranked validation experiments — not implementation order:** 
- **Track 1 — Commerce/Procurement/TradeDocs:** 10–15 qualified Gulf-market interviews, 2 anonymized document/use-case examples, human-reviewed output and an offered paid pilot. Rank subject to evidence; no guaranteed income.
- **Track 2 — ExportLead & CRM:** 10–15 buyer interviews, permission-scoped sample of the lead/quote lifecycle, human approval for all outbound messages.
- **Track 3 — GCC GEO service:** 5–10 buyer pain-point calls and a reversible sample visibility audit; do not create new SaaS before validation.
- **Track 4 — Maritime shipment intelligence:** shadow read-only ETA/cargo provenance pilot only after scope/license and P1 acceptance.
- **All tracks:** `$1,000` is an upper bound on available starting capital, **not a spend authorization**. No paid subscriptions, scraping beyond terms, bulk messages, cloud VM deployment, or production code changes.

**One-line decision:** Keep canonical 32 engineering tasks + existing 7-program overlay + the currently open 10 Draft PRs. Annual Product Hunt adds research candidates only; all local Windows P0 and P1 acceptance gates stay **UNVERIFIED/HOLD**, even where user-reported backup ZIP integrity checks exist. Shared weekly Hermes radar already tracks Product Hunt; do not schedule a duplicate.

## Product Hunt category intelligence — workflow, dictation, voice and vibe coding

**Review date: 2026-10-18. Source: user-provided URLs. Status: RESEARCH_ONLY / no installation.**
Eight links collapse to **six category surfaces** after deduplication:
1. [All Product Hunt categories](https://www.producthunt.com/categories) — taxonomy index, not a product shortlist.
2. [AI Workflow Automation editorial picks](https://www.producthunt.com/categories/ai-workflow-automation?order=recent_launches#content), [all products](https://www.producthunt.com/categories/ai-workflow-automation/all) — same category; `recent_launches` may not actually prove an up-to-the-minute list.
3. [AI Dictation Apps editorial picks](https://www.producthunt.com/categories/ai-dictation-apps), [all products](https://www.producthunt.com/categories/ai-dictation-apps/all) — same category.
4. [Voice AI Tools](https://www.producthunt.com/categories/voice-ai-tools) — includes voice agent infrastructure, streaming STT/TTS and transcription; not synonymous with dictation.
5. [Productivity](https://www.producthunt.com/categories/productivity) — broad mature platform directory.
6. [Vibe Coding](https://www.producthunt.com/categories/vibe-coding?ref=footer) — IDE copilots, web/app builders and development helpers.

Editorial awards, ratings and review counts represent Product Hunt's editorial/community observations; they **do not** certify production reliability, current commercial availability, GCC demand, accuracy or revenue. Avoid product positions that change with sort, promotion and crawl freshness.

### Category-to-canonical-task mapping (no new engineering task IDs)

| Cluster | Products / primary directory source | Primary Hermes fit | Existing task IDs | Decision and verification gate |
| --- | --- | --- | --- | --- |
| Workflow orchestration | n8n, Zapier, Gumloop, Trace; [PH category](https://www.producthunt.com/categories/ai-workflow-automation) | Existing skills/plugins/cron first; human approval, durable states, idempotence | P1-01/03/05, P2-03/05 | Benchmark one synthetic flow against shipped Hermes; no core replacement and no paid node/service |
| Historical approval UX only | **Relay.app**, [PH product page and shutdown notice](https://www.producthunt.com/p/relay-app) | Approval UX reference, not vendor recommendation | P1-03/05 | **DO NOT ADOPT**: notice says free access ends 2026-08-15, paid 2026-09-14. Archived rankings are stale for vendor selection |
| Dictation input | Wispr Flow, Typeless, superwhisper, MacWhisper; [PH category](https://www.producthunt.com/categories/ai-dictation-apps) | Windows/phone voice input as **untrusted text** to existing Hermes commands | P1-03/07, P2-03 | Arabic/English trade terminology, consent, local vs cloud privacy, OS support, transcription accuracy measured; no side effect on mere transcript |
| Conversational voice infrastructure | ElevenLabs, Deepgram, OpenAI Whisper, LiveKit, Vapi; [PH voice category](https://www.producthunt.com/categories/voice-ai-tools) and [LiveKit SDK docs](https://docs.livekit.io/agents/) | Optional realtime STT → LLM → TTS interface only if demand exists; memory/guard external to audio adapter | P0-07, P1-03/07, P2-03/04 | Check provider cost, retention, Arabic/dialect accuracy, latency, interruption handling, separation of transcription from tool authorization |
| App prototyping & code | Cursor, Lovable, v0, Windsurf, bolt.new, Base44; [PH category](https://www.producthunt.com/categories/vibe-coding) | Sandbox-only commercial MVP UI exploration; Hermes repo development remains reviewed | P1-05/06/07, P3-01/05, P4-03 | Generated code requires tests, dependency/license scan, signed evidence, manual PR review; no direct deploy/push to `main` |
| Work management & collaboration | Notion, Linear, Slack, Figma; [PH productivity directory](https://www.producthunt.com/categories/productivity) | Prefer current Hermes state/ledger and connected scoped integrations; avoid parallel task master | P2-01/02/03, P3-05 | Least-privilege read-only sync initially, source-of-truth preserved, explicit external-write approval |

### Commercial licensing and service-lifecycle facts: binding vetoes

- **n8n is fair-code / Sustainable Use License, not unrestricted OSI-open-source software**. Per [the maintained n8n license](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) and [n8n support guidance](https://support.n8n.io/article/can-i-use-your-license-for-my-use-case), many internal/custom managed workflows are allowed, while offering external customers an editor/workflow configuration feature, resale/white label or hosting as a platform generally needs commercial licensing. Clarify the exact Hermes SaaS business model **before** proposing embedding or offering n8n to customers. No implied permissive commercial redistribution.
- **Relay.app announced shutdown** via a founder-listed Product Hunt community notice: free users 2026-08-15 and paid users 2026-09-14. Its historical 2026 Orbit recommendation is *not* valid evidence of October service availability. The approval pattern can be studied without vendor lock-in.
- **Dictation != agent authority**. Transcripts (even high-confidence speech) are input data, not identity proof, authorization, consent for customer data upload, or a durable approval. Voice synthesis and voice cloning also require identity/consent controls.
- Provider marketing about multilingual support is not proof of Arabic dialect quality; collect **synthetic** Arabic + English shipping/LC/quotation samples and explicitly measure text correctness and dangerous-command rejection.

### Four *proposed*, not executed, acceptance fixtures

| Fixture concept | Linked canonical tasks | Minimum proposed acceptance (not PASS) |
| --- | --- | --- |
| WFA-REFERENCE | P1-01/03/05, P2-03 | Synthetic workflow with timeout, empty response, malformed response and network failure; all **DENY**, zero side effects, meaningful state/evidence; baseline against built-in Hermes before external stack |
| VOICE-COMMANDS | P1-03/07, P2-03 | At least 30 synthetic utterances with Arabic dialect, English trade terms and ambiguity; 0 externally executing tools without authenticated action-specific approval; log redaction and consent tests |
| APP-PROTOTYPE | P1-05/06, P3-05, P4-03 | At least 10 deterministic representative code tests + isolated secret scan + dependency/license review; independent review before any PR merge or deploy |
| KNOWLEDGE-ROUTING | P2-01/02/03 | Query provenance against current Hermes ledger; no duplicate master task store, no cross-project leakage or false PASS status |

**Priority decision:** P0 backup custody/functional restoration and P1 evidence/guard invariants before any voice/code/workflow integration. P2 can later evaluate narrowly-scoped read-only voice/text and connectors. P3 may test **one** bilingual trade-operations workflow or voice intake manually if confirmed GCC buyer pain justifies it. Vibe coding supports prototype speed only; it does not create a new business or override security. P4 remains deferred.

**Operations:** Reuse the existing *single* unified weekly Hermes radar to watch these six categories and product-life-cycle changes, without adding another schedule. Existing 32 engineering tasks and 7 portfolio lanes remain the authority; 10 Draft PRs are linked proposals, not deployed proof. Do not modify `main` or enable cloud spend from research findings.

## Shipment Intelligence PR #10 — source-gated staging, no new project

As of 2026-10-19, [PR #10](https://github.com/eltokhey1/hermes-agent/pull/10) is a tenth **open Draft PR**, proposing an offline DCSA/AIS/SQLite evidence adapter under **SHP-02 / VES-01**, mapped to existing engineering **P3-03** (with P2-02 provenance and P1-05 acceptance). It is **not** an additional canonical program, not installed on the Windows host and not a live carrier integration.

**Verified control distinction:** the owner Library's prior v0.1.0 reference passed 12/12 synthetic unit tests in an isolated checkout, but malformed input still created a SQLite DB before rejection, arbitrary form-valid source URLs could produce a `CURRENT_ACTUAL` provider claim, and Maersk-style exports received derived local event IDs. The v0.1.1 PR contains these code paths; it was **read-only code reviewed**, not execution-tested here. [PR #10 review note](https://github.com/eltokhey1/hermes-agent/pull/10#issuecomment-6260572178).

**Action:** Keep commercial discovery read-only and independent. Do not infer vessel AIS as shipment release/discharge, rely on unauthenticated source-URL text as verified events, install a Draft skill, or add another shipment project. Follow P0 restored-app tests, P1 independent go/no-go, P2 authorized provenance and P3-03 validation before staging promotion. Product Hunt opportunities continue to be research references only. Current GH changed-file enumeration: 10 Draft PRs, 46 unique files, no filename overlap, **not** proof of mergeability or CI.
