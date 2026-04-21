# CONTEXTCORE — context_snapshot.md
# AI-MAINTAINED — Full replace after every session. Max 80 lines.
# Last Updated: 2026-04-21 | Session: 8 CLOSED -> 9 READY
# Updated By: Human (session 8 close-out)

---

## WHERE WE ARE
- Version:          v2.0 — IN PROGRESS
- Active Layers:    L4 COMPLETE | CLI + Git Hook next
- Test Phase:       82 passed | 30 skipped | 0 failed
- v1 Baseline:      11.38x compression | 100% accuracy | SEALED
- v2 L4 Result:     23/23 L4 tests passing | cascade deletes verified

---

## WHAT WAS COMPLETED IN SESSION 8

### Commits (in order)
        02980a4  chore: added MIT license
        f354a57  feat(Layer4): schema + builder + querier complete
                                         T-048 to T-070 unlocked and passing
        16699a2  refactor(Layer4): SQLite foreign key enforcement
                                         cascade deletes rechecked and confirmed correct

### Artifacts now in repo
        src/contextcore/layer4_graph/schema.py      COMPLETE
        src/contextcore/layer4_graph/builder.py     COMPLETE
        src/contextcore/layer4_graph/querier.py     COMPLETE
        db/schema.sql                               COMPLETE
        tests/layer4_graph/test_schema.py           23/23 PASSING
        tests/layer4_graph/test_builder.py          PASSING
        tests/layer4_graph/test_querier.py          PASSING
        tests/layer4_graph/test_bfs_scoring.py      PASSING
        tests/layer4_graph/test_layer4_integration  PASSING

### Technical decision made (session 8)
        SQLite foreign key enforcement enabled (PRAGMA foreign_keys = ON)
        Cascade deletes verified: deleting a FILE node removes all
        child FUNCTION + CLASS nodes and all edges sourced from them.
        This is correct behaviour for incremental re-index on file delete.

---

## TEST SUITE STATE (exact, end of session 8)
        Total registered:  90  (T-001 to T-090)
        Passing:           82
        Skipped:           30  <- CLI (T-071/076) + hooks (T-077/080) still locked
        Failing:            0  <- must stay 0 always
        Next unlock:       T-071 to T-076 (CLI) then T-077 to T-080 (hooks)

---

## FILES STATE — COMPLETE PICTURE

        SEALED (v1 — do not touch)
                src/contextcore/layer1_ast/          SEALED
                src/contextcore/layer5_compress/     SEALED
                benchmarks/token_count.py            SEALED
                benchmarks/quality_eval.py           SEALED
                tests/gate_checks/gate_v1.py         SEALED

        COMPLETE (v2 L4 — do not touch)
                src/contextcore/layer4_graph/        COMPLETE
                db/schema.sql                        COMPLETE
                tests/layer4_graph/                  COMPLETE 23/23

        BUILD THIS (session 9)
                src/contextcore/cli/__init__.py      NOT CREATED
                src/contextcore/cli/main.py          NOT CREATED
                hooks/post-commit                    NOT CREATED
                hooks/install_hooks.py               NOT CREATED

        STILL LOCKED (unlock after CLI + hook built)
                tests/cli/test_cli.py                6 stubs (T-071 to T-076)
                tests/hooks/test_git_hook.py         4 stubs (T-077 to T-080)
                tests/integration/test_v2_pipeline.py LOCKED (unlock last)

---

## NEXT SESSION — PICK UP EXACTLY HERE

FIRST COMMAND (before any code):
        python tests/run_all.py
        Expected: 82 passed | 30 skipped | 0 failed
        If different: STOP. Fix before building anything.

BUILD ORDER (strict):

        STEP 1: src/contextcore/cli/main.py
                                        -> Typer-based CLI (pip install typer already in pyproject.toml?)
                                        -> 4 commands: index / query / status / diff
                                        -> index  -> calls GraphBuilder.index_directory()
                                        -> query  -> calls GraphQuerier.query() -> L5 Markdown output
                                        -> status -> reads index_meta from SQLite
                                        -> diff   -> git diff HEAD~1 HEAD --name-only | show affected nodes
                                        -> Remove skipif from tests/cli/test_cli.py ONE TEST AT A TIME
                                        -> Target: T-071 to T-076 GREEN

        STEP 2: hooks/post-commit + hooks/install_hooks.py
                                        -> post-commit: bash script, calls contextcore index --incremental
                                        -> install_hooks.py: copies hook, makes executable, idempotent
                                        -> Remove skipif from tests/hooks/test_git_hook.py ONE AT A TIME
                                        -> Target: T-077 to T-080 GREEN

        STEP 3: python tests/run_all.py
                                        -> Must: 90 passed | 0 skipped | 0 failed
                                        -> All 90 tests green = full v2 implementation complete

        STEP 4: Dogfood
                                        -> Run: contextcore index ./your-real-project
                                        -> Use contextcore query for real dev tasks for 1 full day
                                        -> Note every friction point. Fix top 3.
                                        -> Fill GROUND_TRUTH in tests/gate_checks/gate_v2.py

        STEP 5: Kill test
                                        -> python tests/run_all.py --gate
                                        -> Must: 8/10 subgraph correct | avg <=500ms | avg <=600 tokens
                                        -> If passes: git tag v2.0 | unlock v3

DO NOT TOUCH: v1 sealed files | layer4_graph/ implementation
                                                        gate_v1.py (sealed) | gate_v2.py GROUND_TRUTH until dogfood

---

## OPEN DEVELOPER ACTION REQUIRED
        [PENDING] Fill GROUND_TRUTH in tests/gate_checks/gate_v2.py
                                                10 real queries from dogfood project
                                                Timing: Step 4 above — during dogfood day
        [PENDING] Choose dogfood project (150-250 file Python project)
                                                Needed before: Step 4
        [PENDING] Confirm typer is in pyproject.toml dependencies
                                                Check before starting Step 1
