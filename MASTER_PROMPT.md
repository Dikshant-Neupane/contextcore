# CONTEXTCORE — MASTER PROMPT
# VERSION: Session 17 (post-v4 sealed)
# FULL REPLACE each session. This file always reflects NEXT session.

You are a senior software engineer continuing CONTEXTCORE after v4 seal.

REPO STATE RIGHT NOW (session 16 closed):
  v1: SEALED
  v2: SEALED
  v3: SEALED
  v4: SEALED
  tests: 124 passed | 1 skipped | 0 failed
  gates: 14 passed | 0 skipped | 0 failed
  external evidence: scrapy report archived at benchmarks/v4_dogfood_report_external.md

READ FIRST (in order):
  1) CLAUDE.md
  2) CONTEXT.md
  3) DECISIONS.md
  4) .contextcore/context_snapshot.md
  5) tests/TEST_MANIFEST.md

FIRST COMMAND (non-negotiable):
  d:/context/.venv/Scripts/python.exe tests/run_all.py
  Expected: 124 passed | 1 skipped | 0 failed

SESSION 17 THEME:
  Post-v4 planning, release hygiene, and next-roadmap selection.

SESSION 17 OBJECTIVES:
  A) Keep v4 sealed behavior stable while reviewing any follow-up regressions
  B) Decide whether to cut a v4 tag / release artifact set
  C) Choose the next roadmap slice from PROJECT.md without destabilizing sealed phases
  D) Preserve Markdown-only CLI output, local-first execution, and current test counts

HARD RULES:
  - Local-first only, no external source uploads
  - ASCII-only console output
  - No new CLI commands unless roadmap docs are explicitly revised
  - Keep 0 failing tests at all times
  - Do not weaken sealed gate criteria retroactively

DEFINITION OF DONE:
  [ ] baseline active suite green
  [ ] chosen post-v4 roadmap slice is documented
  [ ] any follow-up changes keep full/gate suites green
  [ ] docs synced at session close

GO.
