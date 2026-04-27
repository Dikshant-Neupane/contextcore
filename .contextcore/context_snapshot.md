# CONTEXTCORE — context_snapshot.md
# AI-MAINTAINED — Full replace after every session. Max 80 lines.
# Last Updated: 2026-04-27 | Session: 10 CLOSED -> 11 READY
# Updated By: AI

---

## WHERE WE ARE
- Version:          v2.0 — SEALED
- Status:           Gate passed | v3 unlocked
- Test suite:       100 passed | 13 skipped | 0 failed
- v2 Gate:          10/10 accuracy | 10.8ms avg latency | 577 avg tokens
- Current version:  tests/conftest.py set to v3

---

## WHAT WAS COMPLETED IN SESSION 10
        tests/gate_checks/gate_v2.py      GROUND_TRUTH filled + SEALED block added
        tests/conftest.py                 CURRENT_VERSION updated to v3
        tests/integration/test_v2_pipeline.py
                                          lock skip removed (v2 integration unlocked)
        src/contextcore/layer4_graph/querier.py
                                          5 dogfood friction fixes shipped:
                                            - sample_project seed exclusion
                                            - reverse CALLS traversal
                                            - non-debug tests/ penalty
                                            - NL seed matching improvements
                                            - domain-aware seeding boosts
        docs synced                        CONTEXT / PROJECT / TEST_MANIFEST / README

---

## FINAL SESSION 10 RESULTS
        Gate:              PASSED
        Accuracy:          10/10
        Avg latency:       10.8ms
        Avg tokens:        577
        Full suite:        100 passed | 13 skipped | 0 failed

---

## KNOWN OPEN ITEMS FOR SESSION 11
        [1] Create/verify git tag v2.0 in remote workflow
        [2] Start v3 kickoff planning (intent routing scope + test scaffold)
        [3] Decide v3 benchmark protocol (intent accuracy dataset + labeling)

---

## NEXT SESSION FIRST COMMAND
        d:/context/.venv/Scripts/python.exe tests/run_all.py
        Expected: 100 passed | 13 skipped | 0 failed
