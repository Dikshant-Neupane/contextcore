# TEST_MANIFEST.md
> Living document — updated each time a phase gate is passed.
> Last updated: Session 10 (2026-04-27)
> Status: **v1 ✅ SEALED** | **v2 ✅ SEALED** | **v3 🟡 ACTIVE** | **v4 🔒 LOCKED**

---

## TEST COUNT BY PHASE (updated session 10)

| Phase       | Registered | Passing | Failing | Skipped | Notes              |
|-------------|-----------|---------|---------|---------|-------------------|
| v1          | 47        | 47      | 0       | 0       | SEALED             |
| v2 — L4     | 23        | 23      | 0       | 0       | SEALED session 8   |
| v2 — CLI    | 6         | 6       | 0       | 0       | COMPLETE session 9 |
| v2 — Hook   | 4         | 4       | 0       | 0       | COMPLETE session 9 |
| v2 — Gate   | 3         | 3       | 0       | 0       | SEALED session 10  |
| integration | —         | 17      | 0       | 13      | v2 unlocked        |
| **Total**   | **90**    | **100** | **0**   | **13**  | parametrized +10   |

Last full run:  100 passed | 13 skipped | 0 failed
Command:        python tests/run_all.py
Date:           2026-04-27 (Session 10 close)

Note on count: 93 > 90 registered because parametrized tests in
conftest.py expand some fixtures into multiple cases at runtime.
Registered count tracks test functions. Pytest count tracks cases.
Both are correct. The number that matters is: 0 failed.

---

## Layer 1 — AST Parser/Extractor (v1 ✅)

| ID    | Test name                                    | File                                  | Phase | Status |
|-------|----------------------------------------------|---------------------------------------|-------|--------|
| T-001 | test_parse_file_returns_file_not_found_for_missing_path | layer1_ast/test_parser.py | v1 | ✅ PASS |
| T-002 | test_parse_file_returns_metadata_for_valid_python_file  | layer1_ast/test_parser.py | v1 | ✅ PASS |
| T-003 | test_extract_function_names                  | layer1_ast/test_extractor.py          | v1    | ✅ PASS |
| T-004 | test_extract_class_names                     | layer1_ast/test_extractor.py          | v1    | ✅ PASS |
| T-005 | test_extract_imports                         | layer1_ast/test_extractor.py          | v1    | ✅ PASS |
| T-006 | test_extract_docstrings                      | layer1_ast/test_extractor.py          | v1    | ✅ PASS |
| T-007 | test_extract_function_signatures             | layer1_ast/test_extractor.py          | v1    | ✅ PASS |
| T-008 | test_parser_to_extractor_pipeline            | layer1_ast/test_layer1_integration.py | v1    | ✅ PASS |
| T-008b| test_parser_to_extractor_class_file          | layer1_ast/test_layer1_integration.py | v1    | ✅ PASS |
| T-008c| test_parser_to_extractor_preserves_source_path | layer1_ast/test_layer1_integration.py | v1  | ✅ PASS |

---

## Layer 5 — Compact Emitter (v1 ✅)

| ID    | Test name                                    | File                                       | Phase | Status |
|-------|----------------------------------------------|--------------------------------------------|-------|--------|
| T-009 | test_emitter_outputs_markdown                | layer5_compress/test_emitter.py            | v1    | ✅ PASS |
| T-010 | test_emitter_no_raw_source                   | layer5_compress/test_emitter.py            | v1    | ✅ PASS |
| T-011 | test_token_count_compressed_lt_raw           | layer5_compress/test_emitter.py            | v1    | ✅ PASS |
| T-012 | test_structure_preserved_in_output           | layer5_compress/test_emitter.py            | v1    | ✅ PASS |
| T-012b| test_emitter_golden_output_simple_function   | layer5_compress/test_emitter.py            | v1    | ✅ PASS |
| T-012c| test_emitter_golden_output_class_with_methods| layer5_compress/test_emitter.py            | v1    | ✅ PASS |
| T-012d| test_emitter_golden_output_file_with_imports | layer5_compress/test_emitter.py            | v1    | ✅ PASS |
| T-013 | test_compression_ratio_gt_5x                 | layer5_compress/test_layer5_integration.py | v1    | ✅ PASS |
| T-014 | test_compression_ratio_result (≥10x floor)   | layer5_compress/test_layer5_integration.py | v1    | ✅ PASS |
| T-014b| test_compression_zero_parse_failures         | layer5_compress/test_layer5_integration.py | v1    | ✅ PASS |
| T-014c| test_emitter_pipeline_emitter_adapter        | layer5_compress/test_layer5_integration.py | v1    | ✅ PASS |

---

## Edge Cases (v1 ✅)

| ID    | Test name                                    | File                  | Phase | Status |
|-------|----------------------------------------------|-----------------------|-------|--------|
| T-015 | test_parse_file_missing_file                 | test_edge_cases.py    | v1    | ✅ PASS |
| T-016 | test_parse_file_empty_file                   | test_edge_cases.py    | v1    | ✅ PASS |
| T-017 | test_parse_file_syntax_error_does_not_crash  | test_edge_cases.py    | v1    | ✅ PASS |
| T-018 | test_parse_file_metadata_fields              | test_edge_cases.py    | v1    | ✅ PASS |
| T-019 | test_extract_missing_file                    | test_edge_cases.py    | v1    | ✅ PASS |
| T-020 | test_extract_empty_file                      | test_edge_cases.py    | v1    | ✅ PASS |
| T-021 | test_extract_constants_only                  | test_edge_cases.py    | v1    | ✅ PASS |
| T-022 | test_extract_only_top_level_classes          | test_edge_cases.py    | v1    | ✅ PASS |
| T-023 | test_extract_top_level_function              | test_edge_cases.py    | v1    | ✅ PASS |
| T-024 | test_extract_function_no_return_annotation   | test_edge_cases.py    | v1    | ✅ PASS |
| T-025 | test_extract_decorated_class                 | test_edge_cases.py    | v1    | ✅ PASS |
| T-026 | test_extract_multiple_classes_and_functions  | test_edge_cases.py    | v1    | ✅ PASS |
| T-027 | test_emit_empty_structure_returns_empty_string | test_edge_cases.py  | v1    | ✅ PASS |
| T-028 | test_emit_contains_filename_header           | test_edge_cases.py    | v1    | ✅ PASS |
| T-029 | test_emit_class_prefixed_with_plus           | test_edge_cases.py    | v1    | ✅ PASS |
| T-030 | test_emit_function_prefixed_with_fn          | test_edge_cases.py    | v1    | ✅ PASS |
| T-031 | test_emit_self_stripped_from_method_params   | test_edge_cases.py    | v1    | ✅ PASS |
| T-032 | test_emit_failed_structure_returns_empty_string | test_edge_cases.py | v1    | ✅ PASS |
| T-033 | test_roundtrip_on_all_sample_files           | test_edge_cases.py    | v1    | ✅ PASS |

---

## Quality / Accuracy (v1 ✅)

| ID    | Test name                                         | File              | Phase | Status |
|-------|---------------------------------------------------|-------------------|-------|--------|
| T-034 | test_raw_corpus_passes_all_checks                 | test_quality.py   | v1    | ✅ PASS |
| T-035 | test_compressed_output_passes_quality_threshold   | test_quality.py   | v1    | ✅ PASS |
| T-036 | test_compressed_answers_question[Q1]              | test_quality.py   | v1    | ✅ PASS |
| T-037 | test_compressed_answers_question[Q2]              | test_quality.py   | v1    | ✅ PASS |
| T-038 | test_compressed_answers_question[Q3]              | test_quality.py   | v1    | ✅ PASS |
| T-039 | test_compressed_answers_question[Q4]              | test_quality.py   | v1    | ✅ PASS |
| T-040 | test_compressed_answers_question[Q5]              | test_quality.py   | v1    | ✅ PASS |
| T-041 | test_compressed_answers_question[Q6]              | test_quality.py   | v1    | ✅ PASS |
| T-042 | test_compressed_answers_question[Q7]              | test_quality.py   | v1    | ✅ PASS |
| T-043 | test_compressed_answers_question[Q8]              | test_quality.py   | v1    | ✅ PASS |
| T-044 | test_compressed_answers_question[Q9]              | test_quality.py   | v1    | ✅ PASS |
| T-045 | test_compressed_answers_question[Q10]             | test_quality.py   | v1    | ✅ PASS |

---

## Gate v1 — Kill Tests (v1 ✅ SEALED 2026-04-21)

| ID    | Test name                              | File                    | Phase | Status |
|-------|----------------------------------------|-------------------------|-------|--------|
| G1-01 | test_v1_gate_compression_ratio         | gate_checks/gate_v1.py  | v1    | ✅ PASS (11.38x) |
| G1-02 | test_v1_gate_ai_accuracy               | gate_checks/gate_v1.py  | v1    | ✅ PASS (100%) |
| G1-03 | test_v1_gate_all_tests_passed          | gate_checks/gate_v1.py  | v1    | ✅ PASS |
| G1-04 | test_v1_gate_artifacts_exist           | gate_checks/gate_v1.py  | v1    | ✅ PASS |

---

## Integration — Full Pipeline (v1 ✅)

| ID    | Test name                                              | File                              | Phase | Status |
|-------|--------------------------------------------------------|-----------------------------------|-------|--------|
| T-046 | TestFullV1Pipeline::test_full_l1_l5_pipeline_simple_file  | integration/test_v1_pipeline.py | v1    | ✅ PASS |
| T-047 | TestFullV1Pipeline::test_full_pipeline_on_sample_project  | integration/test_v1_pipeline.py | v1    | ✅ PASS |
| T-047b| TestFullV1Pipeline::test_pipeline_compression_ratio_beats_v1_gate | integration/test_v1_pipeline.py | v1 | ⏭ SKIP (tiktoken) |
| T-047c| TestFullV1Pipeline::test_pipeline_markdown_structure_preserved | integration/test_v1_pipeline.py | v1 | ✅ PASS |

---

## Layer 4 — Knowledge Graph (v2 ✅ DONE 2026-04-21)

> `src/contextcore/layer4_graph/` fully implemented: schema.py, builder.py, querier.py, score_node().
> All 23 tests PASSING. Git tag: `layer4-complete`

| ID    | Test name                             | File                                       | Phase | Status |
|-------|---------------------------------------|--------------------------------------------|-------|--------|
| T-048 | test_node_types_valid                 | layer4_graph/test_schema.py                | v2    | ✅ PASS |
| T-049 | test_edge_types_valid                 | layer4_graph/test_schema.py                | v2    | ✅ PASS |
| T-050 | test_node_id_deterministic            | layer4_graph/test_schema.py                | v2    | ✅ PASS |
| T-051 | test_edge_id_deterministic            | layer4_graph/test_schema.py                | v2    | ✅ PASS |
| T-052 | test_builder_creates_file_nodes       | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-053 | test_builder_creates_function_nodes   | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-054 | test_builder_creates_class_nodes      | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-055 | test_builder_creates_imports_edges    | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-056 | test_builder_creates_calls_edges      | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-057 | test_builder_creates_contains_edges   | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-058 | test_builder_handles_circular_imports | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-059 | test_builder_incremental_update       | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-060 | test_builder_persists_to_sqlite       | layer4_graph/test_builder.py               | v2    | ✅ PASS |
| T-061 | test_querier_returns_subgraph_result  | layer4_graph/test_querier.py               | v2    | ✅ PASS |
| T-062 | test_bfs_depth_3_max                  | layer4_graph/test_querier.py               | v2    | ✅ PASS |
| T-063 | test_direct_match_highest_score       | layer4_graph/test_querier.py               | v2    | ✅ PASS |
| T-064 | test_result_within_token_budget       | layer4_graph/test_querier.py               | v2    | ✅ PASS |
| T-065 | test_result_within_latency_budget     | layer4_graph/test_querier.py               | v2    | ✅ PASS |
| T-066 | test_score_direct_match_gt_indirect   | layer4_graph/test_bfs_scoring.py           | v2    | ✅ PASS |
| T-067 | test_score_inherits_gt_contains       | layer4_graph/test_bfs_scoring.py           | v2    | ✅ PASS |
| T-068 | test_recent_node_bonus_applied        | layer4_graph/test_bfs_scoring.py           | v2    | ✅ PASS |
| T-069 | test_build_then_query_roundtrip       | layer4_graph/test_layer4_integration.py    | v2    | ✅ PASS |
| T-070 | test_incremental_reindex_speed        | layer4_graph/test_layer4_integration.py    | v2    | ✅ PASS |

---

## LAYER 4 TEST STATUS (T-048 to T-070) — ALL PASSING

| ID    | Test Name                             | Status | Session |
|-------|---------------------------------------|--------|---------|
| T-048 | test_node_types_valid                 | PASS   | 8       |
| T-049 | test_edge_types_valid                 | PASS   | 8       |
| T-050 | test_node_id_deterministic            | PASS   | 8       |
| T-051 | test_edge_id_deterministic            | PASS   | 8       |
| T-052 | test_builder_creates_file_nodes       | PASS   | 8       |
| T-053 | test_builder_creates_function_nodes   | PASS   | 8       |
| T-054 | test_builder_creates_class_nodes      | PASS   | 8       |
| T-055 | test_builder_creates_imports_edges    | PASS   | 8       |
| T-056 | test_builder_creates_calls_edges      | PASS   | 8       |
| T-057 | test_builder_creates_contains_edges   | PASS   | 8       |
| T-058 | test_builder_handles_circular_imports | PASS   | 8       |
| T-059 | test_builder_incremental_update       | PASS   | 8       |
| T-060 | test_builder_persists_to_sqlite       | PASS   | 8       |
| T-061 | test_querier_returns_subgraph_result  | PASS   | 8       |
| T-062 | test_bfs_depth_3_max                  | PASS   | 8       |
| T-063 | test_direct_match_highest_score       | PASS   | 8       |
| T-064 | test_result_within_token_budget       | PASS   | 8       |
| T-065 | test_result_within_latency_budget     | PASS   | 8       |
| T-066 | test_score_direct_match_gt_indirect   | PASS   | 8       |
| T-067 | test_score_inherits_gt_contains       | PASS   | 8       |
| T-068 | test_recent_node_bonus_applied        | PASS   | 8       |
| T-069 | test_build_then_query_roundtrip       | PASS   | 8       |
| T-070 | test_incremental_reindex_speed        | PASS   | 8       |

---

## Gate v2 — Kill Tests (v2 ✅ SEALED 2026-04-27)

> Gate result: 10/10 accuracy | 10.8ms avg latency | 577 avg tokens

| ID    | Test name                                  | File                   | Phase | Status |
|-------|--------------------------------------------|------------------------|-------|--------|
| G2-01 | test_v2_gate_subgraph_accuracy_8_of_10     | gate_checks/gate_v2.py | v2    | ✅ PASS |
| G2-02 | test_v2_gate_avg_latency_under_500ms       | gate_checks/gate_v2.py | v2    | ✅ PASS |
| G2-03 | test_v2_gate_avg_tokens_under_600          | gate_checks/gate_v2.py | v2    | ✅ PASS |
| G2-04 | test_v2_gate_artifacts_exist               | gate_checks/gate_v2.py | v2    | ✅ PASS |

---

## CLI TEST STATUS (T-071 to T-076) — ALL PASSING

| ID    | Test Name                       | Status | Session |
|-------|---------------------------------|--------|---------|
| T-071 | test_index_command_runs         | PASS   | 9       |
| T-072 | test_query_command_runs         | PASS   | 9       |
| T-073 | test_status_command_runs        | PASS   | 9       |
| T-074 | test_diff_command_runs          | PASS   | 9       |
| T-075 | test_query_output_is_markdown   | PASS   | 9       |
| T-076 | test_json_flag_returns_json     | PASS   | 9       |

---

## HOOK TEST STATUS (T-077 to T-080) — ALL PASSING

| ID    | Test Name                           | Status | Session |
|-------|-------------------------------------|--------|---------|
| T-077 | test_hook_installs_in_under_30s     | PASS   | 9       |
| T-078 | test_hook_is_executable             | PASS   | 9       |
| T-079 | test_hook_triggers_on_commit        | PASS   | 9       |
| T-080 | test_incremental_reindex_under_2s   | PASS   | 9       |

---

## Integration — v2 Pipeline (v2 ✅ UNLOCKED)

| ID    | Test name                               | File                             | Phase | Status |
|-------|-----------------------------------------|----------------------------------|-------|--------|
| T-081 | test_full_l1_l4_l5_pipeline             | integration/test_v2_pipeline.py  | v2    | ✅ PASS |
| T-082 | test_v2_pipeline_returns_subgraph       | integration/test_v2_pipeline.py  | v2    | ✅ PASS |
| T-083 | test_v2_pipeline_within_token_budget    | integration/test_v2_pipeline.py  | v2    | ✅ PASS |
| T-084 | test_v2_pipeline_latency_under_500ms    | integration/test_v2_pipeline.py  | v2    | ✅ PASS |

---

## Gate v3 (v3 🔒 LOCKED)

| ID    | Test name                                | File                   | Phase | Status |
|-------|------------------------------------------|------------------------|-------|--------|
| G3-01 | test_v3_gate_intent_accuracy_7_of_10     | gate_checks/gate_v3.py | v3    | 🔒 LOCKED |
| G3-02 | test_v3_gate_latency_under_150ms         | gate_checks/gate_v3.py | v3    | 🔒 LOCKED |
| G3-03 | test_v3_gate_artifacts_exist             | gate_checks/gate_v3.py | v3    | 🔒 LOCKED |

---

## Integration — v3 Pipeline (v3 🔒 LOCKED)

| ID    | Test name                                    | File                            | Phase | Status |
|-------|----------------------------------------------|---------------------------------|-------|--------|
| T-085 | test_full_l1_l3_l4_l5_pipeline               | integration/test_v3_pipeline.py | v3    | 🔒 LOCKED |
| T-086 | test_v3_pipeline_intent_routes_correctly     | integration/test_v3_pipeline.py | v3    | 🔒 LOCKED |
| T-087 | test_v3_pipeline_latency_under_150ms         | integration/test_v3_pipeline.py | v3    | 🔒 LOCKED |

---

## Gate v4 (v4 🔒 LOCKED)

| ID    | Test name                              | File                   | Phase | Status |
|-------|----------------------------------------|------------------------|-------|--------|
| G4-01 | test_v4_gate_rbac_permission_correct   | gate_checks/gate_v4.py | v4    | 🔒 LOCKED |
| G4-02 | test_v4_gate_stale_detection           | gate_checks/gate_v4.py | v4    | 🔒 LOCKED |
| G4-03 | test_v4_gate_artifacts_exist           | gate_checks/gate_v4.py | v4    | 🔒 LOCKED |

---

## Integration — v4 Pipeline (v4 🔒 LOCKED)

| ID    | Test name                          | File                            | Phase | Status |
|-------|------------------------------------|---------------------------------|-------|--------|
| T-088 | test_full_stack_pipeline           | integration/test_v4_pipeline.py | v4    | 🔒 LOCKED |
| T-089 | test_v4_pipeline_rbac_enforced     | integration/test_v4_pipeline.py | v4    | 🔒 LOCKED |
| T-090 | test_v4_pipeline_stale_nodes_flagged | integration/test_v4_pipeline.py | v4  | 🔒 LOCKED |

---

## How to run

```bash
# All active tests
python tests/run_all.py

# Only gate kill tests
python tests/run_all.py --gate

# Specific phase
python tests/run_all.py --phase v1

# Everything (including locked stubs)
python tests/run_all.py --full
```

---

## Gate completion checklist

To seal v2 and unlock v3:
- [x] Implement `src/contextcore/layer4_graph/schema.py`
- [x] Implement `src/contextcore/layer4_graph/builder.py`
- [x] Implement `src/contextcore/layer4_graph/querier.py`
- [x] Implement `src/contextcore/cli/`
- [x] Implement `hooks/post-commit` + `hooks/install_hooks.py`
- [x] Fill in `GROUND_TRUTH` in `gate_checks/gate_v2.py` (10 real dogfood queries)
- [x] Remove `pytestmark = pytest.mark.skip` from layer4_graph, cli, hooks tests
- [x] Run `python tests/run_all.py --gate` and confirm G2-01 through G2-04 pass
- [x] Commit with tag `v2`

---

## SKIP REMOVAL SCHEDULE (final state)

| File                                    | Tests      | Status              | Session |
|-----------------------------------------|------------|---------------------|---------|
| tests/layer4_graph/test_schema.py       | T-048/051  | [DONE] PASS         | 8       |
| tests/layer4_graph/test_builder.py      | T-052/060  | [DONE] PASS         | 8       |
| tests/layer4_graph/test_querier.py      | T-061/065  | [DONE] PASS         | 8       |
| tests/layer4_graph/test_bfs_scoring.py  | T-066/068  | [DONE] PASS         | 8       |
| tests/layer4_graph/test_layer4_int.py   | T-069/070  | [DONE] PASS         | 8       |
| tests/cli/test_cli.py                   | T-071/076  | [DONE] PASS         | 9       |
| tests/hooks/test_git_hook.py            | T-077/080  | [DONE] PASS         | 9       |
| tests/gate_checks/gate_v2.py            | T-081/083  | [DONE] PASS         | 10      |
| tests/integration/test_v2_pipeline.py   | —          | [DONE] PASS         | 10      |
| tests/integration/test_v3_pipeline.py   | —          | [LOCKED] v3         | —       |
| tests/integration/test_v4_pipeline.py   | —          | [LOCKED] v4         | —       |

All skipif markers removed except gate_v2.py (by design — waits for
GROUND_TRUTH) and integration pipeline tests (unlock post-gate).
