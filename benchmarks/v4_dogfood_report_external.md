## v4 Dogfood Validation — 2026-04-28 — scrapy

Target:
- Project: D:\context\scrapy
- Size: 445 python files
- Notes: Local validation run using v4 CLI role mode

Baseline:
- Active suite: 124 passed | 1 skipped | 0 failed
- Gate suite:   14 passed | 0 skipped | 0 failed

Index:
- Index wall time: 127261ms
- Nodes: 12244
- Edges: 11266
- DB size: 9.3 MB
- Last indexed: 2026-04-28T02:25:48+00:00
- Staleness after index: 0 files changed since last index

RBAC (v4) — roles tested: developer / auditor / maintainer
Policy summary:
- developer forbids: tests/, hooks/, markdown docs
- auditor forbids: src/, sample_project/
- maintainer forbids: none

Leakage results:
| Role | Queries Run | Forbidden-node leaks | Notes |
|------|-------------|----------------------|-------|
| developer | 10 | 0 | role-filtered query mode |
| auditor | 10 | 0 | role-filtered query mode |
| maintainer | 10 | 0 | full visibility |

Freshness (v4)
Stale definition: file mtime age >= stale_after_days threshold
Protocol:
- Modified files: D:\context\scrapy\conftest.py (mtime-only touch)
- Observed stale labeling: PASS
- False positives (fresh labeled stale): 0
- Reindex clears staleness: PASS

Operational metrics (AUTO routing)
| # | Role | Query | Tokens | Latency (ms) | Result quality | Notes |
|---|------|-------|--------|--------------|----------------|------|
| 1 | developer | Summarize how auth/permissions are enforced. | 0 | 0 | PASS | - |
| 2 | developer | List files involved in indexing pipeline. | 0 | 0 | PASS | - |
| 3 | developer | Show graph schema nodes and edges. | 600 | 113 | PASS | - |
| 4 | developer | Where is the DB connection created? | 0 | 0 | PASS | - |
| 5 | developer | How does the query ranking work? | 100 | 162 | PASS | - |
| 6 | developer | What does the git hook do? | 0 | 0 | PASS | - |
| 7 | developer | Where is staleness calculated? | 0 | 0 | PASS | - |
| 8 | developer | Show any network or subprocess usage. | 0 | 0 | PASS | - |
| 9 | developer | Where are secrets/config loaded? | 0 | 0 | PASS | - |
| 10 | developer | Explain how context is emitted. | 0 | 0 | PASS | - |
| 11 | auditor | Summarize how auth/permissions are enforced. | 600 | 107 | PASS | - |
| 12 | auditor | List files involved in indexing pipeline. | 50 | 363 | PASS | - |
| 13 | auditor | Show graph schema nodes and edges. | 0 | 0 | PASS | - |
| 14 | auditor | Where is the DB connection created? | 0 | 0 | PASS | - |
| 15 | auditor | How does the query ranking work? | 500 | 164 | PASS | - |
| 16 | auditor | What does the git hook do? | 513 | 93 | PASS | - |
| 17 | auditor | Where is staleness calculated? | 0 | 0 | PASS | - |
| 18 | auditor | Show any network or subprocess usage. | 500 | 132 | PASS | - |
| 19 | auditor | Where are secrets/config loaded? | 500 | 183 | PASS | - |
| 20 | auditor | Explain how context is emitted. | 200 | 1229 | PASS | - |
| 21 | maintainer | Summarize how auth/permissions are enforced. | 600 | 112 | PASS | - |
| 22 | maintainer | List files involved in indexing pipeline. | 600 | 368 | PASS | - |
| 23 | maintainer | Show graph schema nodes and edges. | 600 | 114 | PASS | - |
| 24 | maintainer | Where is the DB connection created? | 600 | 113 | PASS | - |
| 25 | maintainer | How does the query ranking work? | 600 | 156 | PASS | - |
| 26 | maintainer | What does the git hook do? | 563 | 93 | PASS | - |
| 27 | maintainer | Where is staleness calculated? | 0 | 0 | PASS | - |
| 28 | maintainer | Show any network or subprocess usage. | 600 | 144 | PASS | - |
| 29 | maintainer | Where are secrets/config loaded? | 600 | 182 | PASS | - |
| 30 | maintainer | Explain how context is emitted. | 600 | 1233 | PASS | - |

Seal criteria status:
- RBAC correctness: PASS
- Freshness correctness: PASS
- Gate health: PASS
- Full-suite stability: PASS
- Real-project validation archived: PASS
- Documentation sync ready: FAIL
