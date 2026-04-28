# CONTEXTCORE — context_snapshot.md
# AI-MAINTAINED — Full replace after every session. Max 80 lines.
Last synced: 2026-04-28

## Current state (authoritative)
- Versions:
        - v1: SEALED
        - v2: SEALED (tag v2.0)
        - v3: SEALED
        - v4: SEALED (external dogfood evidence archived)

- Test health (latest verified):
        - Full suite: 124 passed | 1 skipped | 0 failed
        - Gate suite: 14 passed | 0 skipped | 0 failed

## v4 external dogfood evidence (SEALED requirement)
- External repo used: scrapy (cloned locally; ~445 Python files)
- Validator: benchmarks/v4_dogfood_validate.py
- External report: benchmarks/v4_dogfood_report_external.md
- Evidence also summarized/archived in CONTEXT.md

## What changed after v4 seal (post-seal follow-through)
- Output contract fixed (Markdown-only):
        - CLI query output is Structured Markdown only.
        - Role/staleness/elapsed metadata is emitted in a parseable Markdown block:
                "## Meta" with keys (role, stale_after_days, matched_count, total_tokens, elapsed_ms, etc.)
        - Any legacy JSON mode does not emit JSON payload.

- CI + release automation hardened:
        - Tag-driven GitHub Release workflow exists (assets uploaded automatically).
        - Safe manual dry-run exists via workflow_dispatch (validates assets; does not publish).
        - Release publish guard is restricted to refs/tags/v*.
        - CI workflows updated/split so tag-only gates do not appear on normal pushes.
        - Actions versions upgraded (checkout/setup-python) to current majors.

- Gate maintenance (auditability preserved):
        - gate_v2 expectations hardened against brittle rank/name drift using stable anchors.
        - Explicit rationale documented in gate_v2 and CONTEXT.md.
        - v2.0 tag remains an accurate record of passing state at tag time.

## Repo truth constraints (do not violate)
- LOCAL FIRST: never send source code off-machine.
- NO TELEMETRY.
- Structured Markdown output is the primary/contracted output format.
- ASCII-only CLI console output (no emoji).
- CLI has exactly 4 commands: index/query/status/diff.
- 0 failing tests is non-negotiable.

## Working tree policy
Do not commit generated/local artifacts:
- .contextcore/contextcore.db (or similar DB artifacts)
- tests/results/latest.md
- tests/results/archive/*

## Next steps (optional, not required for “sealed”)
- Run the Release workflow manually once (workflow_dispatch) to confirm:
        - Dry-run asset validation passes
        - publish-release is skipped on branch refs
- Only create v4.0.1 if you want a real public patch release.
- Reconcile CI Python version vs pyproject requires-python if mismatched.
