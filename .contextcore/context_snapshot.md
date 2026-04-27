# CONTEXTCORE — context_snapshot.md
# AI-MAINTAINED — Full replace after every session. Max 80 lines.
# Last Updated: 2026-04-27 | Session: 11 CLOSED -> 12 READY
# Updated By: AI

---

## WHERE WE ARE
- Version:          v3.0 — ACTIVE
- Status:           Layer 3 kickoff implemented
- Test suite:       107 passed | 12 skipped | 0 failed
- Gate suite:       9 passed | 5 skipped | 0 failed
- v2 gate:          Still passing (no regression)

---

## WHAT WAS COMPLETED IN SESSION 11
        src/contextcore/layer3_intent/__init__.py
        src/contextcore/layer3_intent/types.py
        src/contextcore/layer3_intent/classifier.py
                                First deterministic intent classifier
                                TaskType + IntentResult contract
        tests/layer3_intent/test_classifier.py
                                T-091 to T-096 all passing
        src/contextcore/cli/main.py
                                Added --task-type option to query command
                                AUTO mode routes via Layer 3 classifier
        src/contextcore/layer4_graph/querier.py
                                query() accepts task_type override
        tests/gate_checks/gate_v3.py
                                Scaffold prepared with GROUND_TRUTH format
                                and skip-if guards until labels are filled

---

## SESSION 11 FRICTION NOTES
- Historical docs contain stale phase labels in some sections (non-blocking)
- Existing CLI still supports --json from v2 tests; markdown remains default

---

## NEXT SESSION FIRST ACTION
        1) Fill gate_v3 GROUND_TRUTH with 10 labeled prompts
        2) Run: d:/context/.venv/Scripts/python.exe tests/run_all.py --gate
        3) Measure intent accuracy against 7/10 v3 target
