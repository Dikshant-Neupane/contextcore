═══════════════════════════════════════════════════════════════
CONTEXTCORE — MASTER_PROMPT.md (Post-v4 Seal Ops / Maintenance)
Date: 2026-04-28
Theme: verify automation + keep repo truthfully synced (no new features)
═══════════════════════════════════════════════════════════════

YOU ARE PICKING UP CONTEXTCORE AFTER v4 HAS BEEN SEALED.
Do not ask for re-explanations. Read the files, verify reality, then act.

[YOUR TASK THIS SESSION]
- Verify the release workflow manual dry-run passes (no publish).
- Verify CI is green and not misleading (tag-only jobs do not appear on normal pushes).
- Fix any remaining doc drift so README/snapshot/context match what is actually done.
- Do NOT add product features.

[CONSTRAINTS THIS SESSION]
- LOCAL FIRST, NO TELEMETRY.
- Structured Markdown output contract remains.
- ASCII-only CLI console output.
- CLI remains exactly 4 commands (index/query/status/diff).
- 0 failing tests at all times.
- Do not commit generated artifacts (.contextcore db, tests/results).

[DEFINITION OF DONE THIS SESSION]
- python tests/run_all.py: 0 failures
- python tests/run_all.py --gate: 0 failures
- GitHub Actions manual Release dry-run succeeds:
  - "Dry-run: validate release assets (no publish)" passes
  - publish-release is skipped on manual run
- Docs are consistent:
  - context_snapshot + CONTEXT + PROJECT + README + TEST_MANIFEST agree on sealed status and current counts
- One clean commit if any drift was fixed; otherwise no code changes.

═══════════════════════════════════════════════════════════════
1) READ FIRST (no actions before reading)
═══════════════════════════════════════════════════════════════

Read fully, in order:
1. .contextcore/context_snapshot.md
2. CONTEXT.md
3. PROJECT.md
4. DECISIONS.md
5. README.md
6. tests/TEST_MANIFEST.md
7. pyproject.toml
8. .github/workflows/ci.yml (or equivalent CI workflow)
9. .github/workflows/ci-tag-gate.yml (or equivalent)
10. .github/workflows/release.yml

Then proceed.

═══════════════════════════════════════════════════════════════
2) BASELINE COMMANDS (non-negotiable)
═══════════════════════════════════════════════════════════════

Run:
  python tests/run_all.py
  python tests/run_all.py --gate

Must be 0 failed.

If failures exist: stop and fix before doing anything else.

═══════════════════════════════════════════════════════════════
3) RELEASE WORKFLOW MANUAL DRY-RUN (no tags)
═══════════════════════════════════════════════════════════════

From GitHub UI:
- Actions -> Release -> Run workflow (branch: main)
Expected:
- Dry-run validation job runs and passes
- publish-release is skipped (manual runs must never publish)

Do not create v4.0.1 unless you actually want a public patch release.

═══════════════════════════════════════════════════════════════
4) DOC DRIFT CHECKLIST
═══════════════════════════════════════════════════════════════

Ensure these statements are true everywhere they appear:
- v4 is SEALED (and external evidence is archived)
- Current test totals reflect latest run
- README does not claim key shipped components are merely "planned" if implemented
- Any post-tag maintenance is documented (gate_v2 hardening rationale)

If drift exists, fix it and commit a docs-only commit.

═══════════════════════════════════════════════════════════════
5) SESSION CLOSE (only if changes were made)
═══════════════════════════════════════════════════════════════

Update required targets per repo rules:
- .contextcore/context_snapshot.md (FULL REPLACE)
- CONTEXT.md (APPEND)
- PROJECT.md (APPEND dashboard)
- tests/TEST_MANIFEST.md (counts)
- README.md (if needed)
- DECISIONS.md (only if a new ADR)

Commit:
  docs: sync post-v4-seal operational state

═══════════════════════════════════════════════════════════════
END MASTER PROMPT
═══════════════════════════════════════════════════════════════
