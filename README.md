# CONTEXTCORE

AST-first context infrastructure for AI coding workflows.

- v1 sealed: 11.38x compression, 100% quality accuracy
- v2 sealed: gate passed (10/10 accuracy, 10.8ms avg latency, 577 avg tokens)
- v3 kickoff: Layer 3 intent classifier scaffold implemented
- local-first: source code never leaves your machine

## Current status

| Track | Status |
|---|---|
| v1 | SEALED (tag: v1.0) |
| v2 | SEALED (L4 + CLI + hooks + gate) |
| v3 | ACTIVE (L3 classifier + integration started) |
| Full active suite | 107 passed, 12 skipped, 0 failed |

## Why CONTEXTCORE exists

Raw file dumps waste context window and cost tokens. CONTEXTCORE reduces code to structural, task-relevant context before it reaches an assistant.

## Architecture (roadmap)

1. L1: static AST extraction (Tree-sitter)
2. L2: temporal graph (planned)
3. L3: intent routing (planned)
4. L4: dependency graph and retrieval (active)
5. L5: compact markdown emission

## v1 results (sealed)

| Metric | Result | Target |
|---|---|---|
| Compression ratio | 11.38x | >5x |
| Accuracy on eval set | 10/10 (100%) | >=80% |
| Parse failures | 0/20 files | 0 |

## Quick start

```bash
pip install -e ".[dev]"
python tests/run_all.py
```

## Documentation index

- [CLAUDE.md](CLAUDE.md): project operating rules
- [PROJECT.md](PROJECT.md): roadmap and session dashboards
- [CONTEXT.md](CONTEXT.md): session log and tracker
- [DECISIONS.md](DECISIONS.md): ADR history
- [.contextcore/context_snapshot.md](.contextcore/context_snapshot.md): current execution snapshot
- [tests/TEST_MANIFEST.md](tests/TEST_MANIFEST.md): phase test map and unlock order

## Safety and privacy

- local processing only
- no source-code telemetry
- no external API calls with source content

## License

MIT (see [LICENSE](LICENSE))
