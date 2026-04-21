# CONTEXTCORE — context_snapshot.md
# AI-MAINTAINED — Full replace after every session. Max 80 lines.
# Last Updated: 2026-04-21 | Session: 7 CLOSED → 8 READY
# Updated By: Human (session 7 close-out)

---

## WHERE WE ARE
- Version:          v2.0 — IN PROGRESS
- Active Layers:    L4 (Graph) + L4 (Slice) + CLI + Git Hook
- Test Phase:       v2 scaffold COMPLETE | implementation starting
- v1 Baseline:      11.38x compression | 100% accuracy | 33/33 sealed

---

## TEST SYSTEM STATE (as of end of session 7)
- Total tests in manifest:   T-001 to T-090 (90 registered)
- Passing:                   59
- Skipped (locked stubs):    53  <- these unlock as L4 is built
- Failed:                    0   <- must stay 0 at all times
- Gate v1:                   SEALED (gate_v1.py — 4 assertions)
- Gate v2:                   PENDING (GROUND_TRUTH stubs present, not filled)
- Gate v3/v4:                LOCKED
- Last full run command:      python tests/run_all.py
- Last run result:            59 passed | 53 skipped | 0 failed

---

## WHAT WAS COMPLETED IN SESSION 7
- tests/gate_checks/gate_v1.py      SEALED — 4 assertions on v1 results
- tests/gate_checks/gate_v2.py      PENDING — GROUND_TRUTH stubs + skipif guard
- tests/gate_checks/gate_v3.py      LOCKED
- tests/gate_checks/gate_v4.py      LOCKED
- tests/layer4_graph/               7 files | 23 locked stubs (T-048 to T-070)
- tests/cli/test_cli.py             6 locked stubs (T-071 to T-076)
- tests/hooks/test_git_hook.py      4 locked stubs (T-077 to T-080)
- tests/TEST_MANIFEST.md            T-001 to T-090 registered
- tests/run_all.py                  Windows cp1252 Unicode crash fixed
- pyproject.toml                    python_files = ["test_*.py", "gate_*.py"]
- CLAUDE.md                         Test system rules appended

---

## WINDOWS CP1252 FIX — WHAT WAS DONE AND WHY
Problem:  print() calls with emoji (✅ ❌ 🧪 etc.) crash on Windows
          cp1252 terminals with UnicodeEncodeError.
Fix:      sys.stdout recoded at startup in run_all.py.
          Console output emojis replaced with ASCII equivalents
          in all print() paths.
          File writes (report Markdown) remain UTF-8 — unaffected.
Rule:     All future print() in run_all.py and any CLI output file
          must use ASCII-safe symbols for console.
          Markdown report files may use UTF-8 freely.
ASCII map used:
          PASS    ->  [PASS]   (was ✅)
          FAIL    ->  [FAIL]   (was ❌)
          SKIP    ->  [SKIP]   (was ⏭)
          LOCKED  ->  [LOCK]   (was 🔒)
          PENDING ->  [...]    (was 🟡)

---

## FILES STATE — COMPLETE PICTURE
### v1 (SEALED — do not touch)
- src/contextcore/layer1_ast/parser.py        SEALED
- src/contextcore/layer1_ast/extractor.py     SEALED
- src/contextcore/layer5_compress/emitter.py  SEALED
- benchmarks/token_count.py                   SEALED
- benchmarks/quality_eval.py                  SEALED

### v2 Test Scaffold (COMPLETE — do not add stubs)
- tests/layer4_graph/test_schema.py           23 stubs locked
- tests/layer4_graph/test_builder.py          locked stubs
- tests/layer4_graph/test_querier.py          locked stubs
- tests/layer4_graph/test_bfs_scoring.py      locked stubs
- tests/layer4_graph/test_layer4_integration  locked stubs
- tests/cli/test_cli.py                       locked stubs
- tests/hooks/test_git_hook.py                locked stubs

### v2 Implementation (BUILD THIS — session 8 starts here)
- src/contextcore/layer4_graph/__init__.py    NOT CREATED
- src/contextcore/layer4_graph/schema.py      NOT CREATED
- src/contextcore/layer4_graph/builder.py     NOT CREATED
- src/contextcore/layer4_graph/querier.py     NOT CREATED
- db/schema.sql                               NOT CREATED
- db/__init__.py                              NOT CREATED

---

## NEXT SESSION — PICK UP EXACTLY HERE

FIRST COMMAND OF SESSION 8 (before anything else):
  python tests/run_all.py
  -> Must show: 59 passed | 53 skipped | 0 failed
  -> If different: stop and fix before building anything

BUILD ORDER (strict — do not skip steps):

  STEP 1: src/contextcore/layer4_graph/schema.py
          -> Python dataclasses: GraphNode, GraphEdge,
             EdgeType, NodeType, EdgeConfidence, SubgraphResult
          -> Remove skipif from tests/layer4_graph/test_schema.py
          -> Run: pytest tests/layer4_graph/test_schema.py -v
          -> Must: 4 tests GREEN, 0 RED
          -> Update TEST_MANIFEST.md: T-048 to T-051 -> PASS

  STEP 2: db/schema.sql
          -> SQLite DDL: nodes table + edges table + index_meta
          -> Indexes on filepath, name, node_type, source_id, target_id
          -> Run: sqlite3 .contextcore/test.db < db/schema.sql
          -> Confirm tables created

  STEP 3: src/contextcore/layer4_graph/builder.py
          -> Reads L1 extractor output (FileStructure)
          -> Writes nodes + edges to SQLite
          -> Remove skipif from test_builder.py ONE TEST AT A TIME
          -> Red -> Green -> next test
          -> Target: T-052 to T-060 all GREEN

  STEP 4: src/contextcore/layer4_graph/querier.py
          -> BFS from seed nodes, depth 3, ADR-007 scoring
          -> Remove skipif from test_querier.py ONE TEST AT A TIME
          -> Target: T-061 to T-065 all GREEN

  STEP 5: python tests/run_all.py
          -> Must show: 82+ passed | fewer skipped | 0 failed
          -> If 0 failed: commit

DO NOT TOUCH: CLI (T-071 to T-076) or hooks (T-077 to T-080)
              until querier tests are all GREEN.

---

## OPEN DEVELOPER ACTION REQUIRED (AI cannot do this)
  gate_v2.py GROUND_TRUTH has 10 stub entries ([FILL IN]).
  Developer must fill these from the dogfood project BEFORE
  running --gate. This is the kill test. It cannot be automated.
  Suggested timing: fill during Step 4 dogfood session.
