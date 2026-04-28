# CONTEXTCORE - PROJECT.md
# Master Version Document | Inception to Final Vision
# Created: 2026-04-21 | Author: Dikshant Neupane

---

## THE PROBLEM WE ARE SOLVING
AI coding assistants receive raw file dumps as context.
This is inefficient, expensive, and inaccurate.
Developers spend $50-150/month on token costs.
Context windows are wasted on irrelevant information.
No existing tool routes context by developer INTENT before serving it.

CONTEXTCORE solves this by:
1. Parsing code with AST (not raw text)
2. Compressing it into structured Markdown
3. Slicing only the relevant subgraph per task
4. Eventually routing by intent automatically

---

## THE NORTH STAR
"On a 200-500 file project, CONTEXTCORE delivers accurate,
task-relevant context in <=600 tokens and <=150ms."

---

## VERSION ROADMAP

Current execution snapshot (2026-04-28): v1 sealed, v2 sealed, v3 sealed, v4 sealed.
Verified runs: full suite 124 passed | 1 skipped | 0 failed; gate suite 14 passed | 0 skipped | 0 failed.

---

### VERSION 1.0 - "PROVE IT WORKS"
**Timeline:** Month 1 (Weeks 1-4)
**Theme:** Kill the riskiest assumption. Nothing else.
**Status:** SEALED

#### Scope (ONLY these. Nothing else.)
- [x] Project scaffolding + all documentation
- [ ] Layer 1: Tree-sitter AST parser (Python only)
- [ ] Layer 5: Compressed Markdown emitter
- [ ] benchmarks/token_count.py - raw vs compressed measurement
- [ ] 20-file Python test corpus

#### Kill Test (Must Pass Before v2)
> "Does AST -> Markdown reduce tokens by >5x
>  without reducing AI answer accuracy below 80%?"

#### Definition of Done
- Compression ratio > 5x on a real 20-file Python project
- AI answer accuracy maintained (measured by 10 standard questions)
- Token measurement script is automated and repeatable
- All tests pass (pytest)
- README explains what v1 does in plain English

#### What v1 Explicitly Does NOT Do
- No graph database
- No intent classification
- No temporal tracking
- No team features
- No CLI tool (yet)
- No external API calls

---

### VERSION 2.0 - "MAKE IT SMART"
**Timeline:** Month 2-3 (After v1 kill test passes)
**Theme:** Add the graph layer. Make slicing work.
**Status:** SEALED

#### Planned Scope
- Layer 4: SQLite-backed dependency graph
- Relevance-ranked context slicing
- Cross-file relationship mapping
- Git hook for incremental re-indexing
- CLI: contextcore index ./project
- Test on YOUR OWN real project (dogfooding)
- README update + first public GitHub push

#### Kill Test
> "Does relevance slicing deliver the correct subgraph
>  for 8/10 real developer queries on a 200-file project?"

---

### VERSION 3.0 - "MAKE IT FEEL LIKE MAGIC"
**Timeline:** Month 4-5
**Theme:** Intent engine. Near-zero friction.
**Status:** SEALED

#### Planned Scope
- Layer 3: Lightweight intent classifier (7B local model or GPT-4o-mini)
- 6 task modes: DEBUG / REFACTOR / SCAFFOLD / ONBOARD / REVIEW / SECURITY
- Auto-routing of developer queries to task mode
- Background async pre-fetch (context ready before prompt submitted)
- Confidence decay scoring on stale graph nodes
- "Why this context" explainer output
- VSCode extension OR CLI tool (decide after v2 feedback)

#### Kill Test
> "Does the intent classifier correctly route 7/10 natural
>  language prompts to the correct subgraph mode?"

---

### VERSION 4.0 - "MAKE IT PRODUCTION READY"
**Timeline:** Month 6+
**Theme:** Security, freshness, team-readiness.
**Status:** SEALED

#### Planned Scope
- Layer 2: Temporal graph (Graphiti-style, SQLite-backed first)
- Graph staleness daemon (git post-commit hook -> incremental re-index)
- RBAC: Node-level permissions inherited from git file permissions
- Confidence decay: old unconfirmed decisions flagged as STALE
- Infrastructure tiers: Lite / Standard / Full mode
- Team sharing: shared .contextcore/ folder in git repo
- PyPI package publication
- Benchmark paper: formal token reduction claims with methodology

#### Kill Test
> "Does CONTEXTCORE serve fresh, permission-correct context
>  to 3 different developer roles on the same 500-file project?"

#### Seal Criteria (v4.0)
- RBAC correctness: no unauthorized nodes returned for `developer`, `auditor`, and `maintainer` role scenarios.
- Freshness correctness: stale files are labeled `[STALE]` at/above threshold and fresh files are not mislabeled.
- Gate health: `python tests/run_all.py --gate --no-report` remains green with v4 tests included.
- Full-suite stability: `python tests/run_all.py --full --no-report` remains green with no new failures.
- Real-project validation: run the same role/freshness checks on one 200-500 file dogfood project and archive metrics.
- Documentation sync: README/PROJECT/CONTEXT/TEST_MANIFEST reflect final v4 counts and sealed status in one pass.

#### Final seal evidence
- External dogfood target: `D:\context\scrapy`
- External project size: 445 Python files
- Archived report: `benchmarks/v4_dogfood_report_external.md`
- Result: PASS on RBAC correctness, freshness correctness, gate health, and full-suite stability

---

### FINAL VISION - "CONTEXTCORE AS INFRASTRUCTURE"
**Timeline:** Month 9-12
**Theme:** The context layer every AI dev tool uses.

#### Vision
- CONTEXTCORE becomes the standard context protocol for AI coding
- MCP server integration (any AI tool can call it)
- Language support: Python, TypeScript, Go, Rust, Java
- Plugin marketplace: custom intent modes per domain
- Enterprise: SOC2 compliance, audit logs, SSO
- Open-source core, hosted managed version
- Community-contributed intent mode library

---

## SUCCESS METRICS BY VERSION

| Version | Token Reduction | Latency | Accuracy | Stars |
|---------|----------------|---------|----------|-------|
| v1      | >5x            | N/A     | >80%     | 0     |
| v2      | slice-mode (577 avg tokens) | 10.8ms | 100% (10/10) | 50+   |
| v3      | >50x           | <150ms  | >90%     | 500+  |
| v4      | >70x           | <80ms   | >95%     | 2k+   |

---

## ARCHITECTURE OVERVIEW
INPUT: Raw project files (code, docs, diagrams)
  ↓
[L1] STATIC ANALYSIS ENGINE (Tree-sitter AST, local)
  ↓
[L2] TEMPORAL GRAPH LAYER (v4 - track decisions over time)
  ↓
[L3] INTENT EXTRACTION ENGINE (v3 - route by task type)
  ↓
[L4] RELEVANCE-RANKED CONTEXT SLICE (v2 - subgraph only)
  ↓
[L5] COMPRESSED TEXT EMISSION (v1 - structured Markdown)
  ↓
OUTPUT: <=600 tokens, <=150ms, structured Markdown

---

## NON-NEGOTIABLE PRINCIPLES (NEVER VIOLATE)
1. LOCAL FIRST: Source code never leaves the machine. Ever.
2. NO TELEMETRY: Zero tracking. Zero analytics. Full stop.
3. COMPRESSION OVER BRUTE FORCE: We never "just add more tokens."
4. INTENT BEFORE CONTEXT: We route first, serve second.
5. FRESHNESS MATTERS: Stale context is worse than no context.
6. FRICTION KILLS: Setup must take <5 minutes for solo developers.

---

## PROJECT STATE DASHBOARD

*Auto-appended each session close. Never edited retroactively.*
*ARCHIVAL ONLY: Entries below are historical snapshots at prior session close times.*
*Authoritative current state is the "Current execution snapshot" line under VERSION ROADMAP above.*

---

### Archival Snapshot — Session 8 Close | 2026-04-21
VERSION GATES ───────────────────────────────────────────────────────────────── v1 [SEALED] 11.38x compression | 100% accuracy | git tag v1.0 v2 [ACTIVE] L4 complete | CLI + hook + gate remaining v3 [LOCKED] Awaiting v2 gate pass v4 [LOCKED] Awaiting v3 gate pass

LAYER STATUS ───────────────────────────────────────────────────────────────── L1 AST Parser [SEALED] parser.py + extractor.py L2 Temporal Graph [LOCKED] v4 scope L3 Intent Engine [LOCKED] v3 scope L4 Dependency Graph [COMPLETE] schema + builder + querier L5 Compression [SEALED] emitter.py

TEST SUITE ───────────────────────────────────────────────────────────────── Registered: 90 (T-001 to T-090) Passing: 82 Skipped: 30 CLI T-071/076 | hooks T-077/080 | gate T-081/083 Failing: 0 non-negotiable floor

COMMITS THIS SESSION ───────────────────────────────────────────────────────────────── 02980a4 chore: MIT license f354a57 feat(Layer4): schema + builder + querier | T-048/070 green 16699a2 refactor(Layer4): FK enforcement + cascade delete verified [doc] chore(docs): session 8 close — 4 living docs synced

ADR LOG ───────────────────────────────────────────────────────────────── ADR-001 SQLite over Neo4j (v1) ACTIVE ADR-002 Python-only grammar (v1) ACTIVE ADR-003 Markdown output format (permanent) PERMANENT ADR-004 No external API calls on source (permanent) PERMANENT ADR-005 Layer 3 locked until v1 benchmarks pass SATISFIED ADR-006 Graph node + edge taxonomy ACTIVE ADR-007 BFS depth-3 retrieval + scoring ACTIVE ADR-008 Git post-commit incremental reindex PENDING BUILD ADR-009 CLI: 4 commands only PENDING BUILD ADR-010 ASCII-only console output (permanent) PERMANENT ADR-011 SQLite FK enforcement mandatory ACTIVE

DEVELOPER ACTIONS PENDING ───────────────────────────────────────────────────────────────── [1] Confirm typer in pyproject.toml before session 9 [2] Choose dogfood project (150-250 file Python project) [3] Fill gate_v2.py GROUND_TRUTH (10 real queries, hand-labeled) [4] Run dogfood day (use the tool for real dev work)

NORTH STAR METRIC STATUS ───────────────────────────────────────────────────────────────── Target: <=600 tokens | <=150ms | 200-500 file project v1 result: 11.38x compression | 100% accuracy [EXCEEDED TARGET] v2 result: pending gate (kill test Step 5 session 9)

---

### Dashboard entry format (for future sessions):
Each session close appends one dashboard block here.
Blocks are never edited after being written.
This file is the permanent record of where the project
stood at the close of every session.

---

### Archival Snapshot — Session 9 Close | 2026-04-23
VERSION GATES ───────────────────────────────────────────────────────────────── v1 [SEALED] 11.38x compression | 100% accuracy | git tag v1.0 v2 [ACTIVE] All code done | Dogfood + gate remaining v3 [LOCKED] Awaiting v2 gate pass v4 [LOCKED] Awaiting v3 gate pass

LAYER STATUS ───────────────────────────────────────────────────────────────── L1 AST Parser [SEALED] parser.py + extractor.py L2 Temporal Graph [LOCKED] v4 scope L3 Intent Engine [LOCKED] v3 scope L4 Dependency Graph [SEALED] schema + builder + querier L5 Compression [SEALED] emitter.py CLI [COMPLETE] 4 commands | Typer | ADR-009 satisfied Git Hook [COMPLETE] post-commit | install_hooks | ADR-008 satisfied

TEST SUITE ───────────────────────────────────────────────────────────────── Passing: 93 (includes parametrized case expansion) Skipped: 20 (gate: GROUND_TRUTH empty | v3/v4 integration: locked) Failing: 0 non-negotiable floor

SESSION 9 ARTIFACTS ───────────────────────────────────────────────────────────────── src/contextcore/cli/init.py Created src/contextcore/cli/main.py 4-command CLI (index/query/status/diff) hooks/post-commit Background incremental reindex hooks/install_hooks.py Idempotent hook installer benchmarks/subgraph_accuracy.py Subgraph quality benchmark tests/cli/test_cli.py T-071/076 all GREEN tests/hooks/test_git_hook.py T-077/080 all GREEN .contextcore/contextcore.db Created on first index run

ADR SATISFACTION STATUS ───────────────────────────────────────────────────────────────── ADR-008 Git post-commit hook [SATISFIED] session 9 ADR-009 CLI 4 commands only [SATISFIED] session 9 ADR-010 ASCII console output [ACTIVE] enforced in CLI ADR-011 SQLite FK enforcement [ACTIVE] enforced in builder+querier

v2 REMAINING (session 10 — developer action): [1] Choose dogfood project (150-250 file Python project) [2] Run contextcore index + query for real work [3] Fill gate_v2.py GROUND_TRUTH (10 labeled queries) [4] python tests/run_all.py --gate [5] Fix any gate failures (BFS tuning if needed) [6] git tag v2.0

---

### Archival Snapshot — Session 10 Close | 2026-04-27
VERSION GATES ─────────────────────────────────────────────────────────────────
v1 [SEALED] 11.38x compression | 100% accuracy | git tag v1.0
v2 [SEALED] gate passed | 10/10 accuracy | 10.8ms | 577 tokens
v3 [ACTIVE] unlocked for kickoff
v4 [LOCKED] awaiting v3 gate pass

LAYER STATUS ─────────────────────────────────────────────────────────────────
L1 AST Parser [SEALED]
L2 Temporal Graph [LOCKED]
L3 Intent Engine [NEXT]
L4 Dependency Graph [SEALED]
L5 Compression [SEALED]

TEST SUITE ─────────────────────────────────────────────────────────────────
Passing: 100
Skipped: 13
Failing: 0

SESSION 10 COMMITS ─────────────────────────────────────────────────────────────────
e2569dd fix(L4): exclude sample_project nodes during seed matching
2e95a80 fix(L4): include reverse CALLS traversal in BFS expansion
4e43973 fix(L4): de-prioritize test paths for non-debug queries
e8ccd7e fix(L4): improve seed matching for natural-language queries
2b6cf46 fix(L4): boost domain seeding for gate dogfood queries

v2 STATUS ─────────────────────────────────────────────────────────────────
SEALED. Next session starts v3 intent-layer kickoff.

---

### Archival Snapshot — Session 11 Close | 2026-04-27
VERSION GATES ─────────────────────────────────────────────────────────────────
v1 [SEALED] 11.38x compression | 100% accuracy | git tag v1.0
v2 [SEALED] 10/10 | 10.8ms | 577 tokens | git tag v2.0
v3 [ACTIVE] Layer 3 scaffold + first classifier + tests
v4 [LOCKED] awaiting v3 gate pass

LAYER STATUS ─────────────────────────────────────────────────────────────────
L1 AST Parser [SEALED]
L2 Temporal Graph [LOCKED]
L3 Intent Engine [IN PROGRESS] classifier + query integration started
L4 Dependency Graph [SEALED]
L5 Compression [SEALED]

TEST SUITE ─────────────────────────────────────────────────────────────────
Passing: 107
Skipped: 12
Failing: 0

SESSION 11 ARTIFACTS ─────────────────────────────────────────────────────────────────
src/contextcore/layer3_intent/__init__.py
src/contextcore/layer3_intent/types.py
src/contextcore/layer3_intent/classifier.py
tests/layer3_intent/test_classifier.py
tests/gate_checks/gate_v3.py
src/contextcore/layer4_graph/querier.py
src/contextcore/cli/main.py

v3 STATUS ─────────────────────────────────────────────────────────────────
Kickoff complete. Next step: label gate prompts and measure intent accuracy against 7/10 target.
