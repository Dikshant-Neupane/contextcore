# CONTEXTCORE — context_snapshot.md
# AI-MAINTAINED — Full replace after every session. Max 80 lines.
# Last Updated: 2026-04-23 | Session: 9 CLOSED -> 10 READY
# Updated By: Human (session 9 close-out)

---

## WHERE WE ARE
- Version:          v2.0 — IMPLEMENTATION COMPLETE
- Status:           CLI + Hook built | Dogfood + Gate remaining
- Test suite:       93 passed | 20 skipped | 0 failed
- v1 Baseline:      11.38x compression | 100% accuracy | SEALED
- v2 L4:            23/23 passing | SEALED
- v2 CLI:           6/6 passing | T-071 to T-076 GREEN
- v2 Hook:          4/4 passing | T-077 to T-080 GREEN

---

## WHAT WAS COMPLETED IN SESSION 9
        pyproject.toml               Typer dependency added + CLI entrypoint
        src/contextcore/cli/__init__.py  Package marker created
        src/contextcore/cli/main.py  4-command CLI implemented (ADR-009)
        hooks/post-commit            Bash hook: detects .py changes, calls
                                                                                                                         contextcore index --incremental in bg
        hooks/install_hooks.py       Python installer: copy + chmod + idempotent
        benchmarks/subgraph_accuracy.py  Subgraph quality benchmark script
        tests/cli/test_cli.py        Stubs replaced with real tests (T-071/076)
        tests/hooks/test_git_hook.py Stubs replaced with real tests (T-077/080)
        .contextcore/contextcore.db  Created on first index run
        tests/results/               4 new archive reports generated

---

## TEST SUITE STATE (exact, end of session 9)
        Total registered:  90  (T-001 to T-090)
        Passing:           93  (includes parametrized expansions)
        Skipped:           20
        Failing:            0  <- must stay 0 always
        Skipped breakdown:
                gate_v2.py        T-081 to T-083  GROUND_TRUTH not filled (dev action)
                test_v2_pipeline  integration     LOCKED until gate v2 passes
                test_v3_pipeline  integration     LOCKED
                test_v4_pipeline  integration     LOCKED

---

## FILES STATE — COMPLETE PICTURE
        SEALED (do not touch)
                src/contextcore/layer1_ast/           SEALED v1
                src/contextcore/layer5_compress/      SEALED v1
                tests/gate_checks/gate_v1.py          SEALED v1
                src/contextcore/layer4_graph/         SEALED v2 L4

        COMPLETE (session 9)
                src/contextcore/cli/main.py           COMPLETE
                hooks/post-commit                     COMPLETE
                hooks/install_hooks.py                COMPLETE
                tests/cli/test_cli.py                 T-071/076 GREEN
                tests/hooks/test_git_hook.py          T-077/080 GREEN

        REMAINING (developer action required — AI cannot do these)
                tests/gate_checks/gate_v2.py          GROUND_TRUTH needs 10 real queries
                Dogfood project                       Not chosen yet

---

## NEXT SESSION — PICK UP EXACTLY HERE

FIRST COMMAND (non-negotiable):
        python tests/run_all.py
        Expected: 93 passed | 20 skipped | 0 failed
        If different: STOP. Fix before touching anything.

SESSION 10 IS DOGFOOD + GATE. NO NEW CODE.

        ACTION 1 — Choose dogfood project
                Must be: Python project | 150-250 files | you know it well
                If none available: use sample_project/ as a smaller proxy
                and note the limitation in CONTEXT.md

        ACTION 2 — Index it
                pip install -e .
                contextcore index ./your-real-project
                Observe: node count | edge count | time taken
                Note any errors or slow paths

        ACTION 3 — Use it for real work (minimum 1 hour)
                For every question you ask the AI today, first run:
                contextcore query "your question here"
                Compare the context it returns to what you would have
                pasted manually. Note every friction point.

        ACTION 4 — Fix top 3 friction points found in ACTION 3
                Each fix = one commit
                Run: python tests/run_all.py after each fix
                Must stay: 0 failed

        ACTION 5 — Fill GROUND_TRUTH in tests/gate_checks/gate_v2.py
                Open gate_v2.py
                Fill all 10 GROUND_TRUTH entries from real queries you ran today
                Each entry needs: query text + expected_nodes (filepaths or names)
                This is a developer-only action. AI cannot fabricate these.

        ACTION 6 — Run the gate
                python tests/run_all.py --gate
                Must pass all three:
                        T-081: 8/10 subgraph queries return correct nodes
                        T-082: avg retrieval latency <= 500ms
                        T-083: avg token count per result <= 600
                If all pass -> proceed to ACTION 7
                If any fail -> see GATE FAIL PROTOCOL below

        GATE FAIL PROTOCOL (if needed):
                T-081 fails: fix BFS scoring weights in querier.py (ADR-007)
                                                                 check: are seed nodes matching correctly?
                                                                 check: is depth-3 BFS reaching the right nodes?
                T-082 fails: profile GraphQuerier.query()
                                                                 check: are SQLite indexes being used? (EXPLAIN QUERY PLAN)
                                                                 check: is BFS traversal doing N+1 queries?
                T-083 fails: tighten token budget in SubgraphResult
                                                                 check: are too many low-score nodes included?
                                                                 add: hard token cap after scoring sort
                After fix: re-run --gate | do NOT tag until all 3 pass

        ACTION 7 — If gate passes: seal and tag
                Update gate_v2.py: add SEALED comment + actual results
                Update PROJECT.md: v2 row in success metrics table
                Update TEST_MANIFEST.md: gate counts all PASS
                Update conftest.py: CURRENT_VERSION = "v3"
                Append v2 retrospective to CONTEXT.md
                Full replace context_snapshot.md with v3 kickoff state
                Full replace MASTER_PROMPT.md with session 11 (v3) prompt
                Append session 10 dashboard to PROJECT.md
                git tag v2.0
                Announce: v2 is done.

---

## OPEN DEVELOPER ACTIONS (AI cannot do these)
        [1] Choose dogfood project (session 10 start)
        [2] Run contextcore index on it (session 10)
        [3] Fill gate_v2.py GROUND_TRUTH (session 10 during dogfood)
        [4] Confirm: does contextcore query produce useful output
                        for real tasks? (this is the real v2 validation)
