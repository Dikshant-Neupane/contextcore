# CONTEXTCORE

AST-first context infrastructure for AI coding workflows.

```text
	____ ___  _   _ _____ _____ _   _ _____ _____ ___  ____  _____
 / ___/ _ \| \ | |_   _| ____| \ | |_   _| ____/ _ \|  _ \| ____|
| |  | | | |  \| | | | |  _| |  \| | | | |  _|| | | | |_) |  _|
| |__| |_| | |\  | | | | |___| |\  | | | | |__| |_| |  _ <| |___
 \____\___/|_| \_| |_| |_____|_| \_| |_| |_____\___/|_| \_\_____|
```

CONTEXTCORE converts raw source trees into compact, structurally meaningful context so assistants receive less noise and more relevant signals.

## Highlights

- v1 sealed: 11.38x compression, 100% eval accuracy
- v2 sealed: gate passed (10/10 subgraph accuracy, 10.8ms avg latency, 577 avg tokens)
- v3 sealed: intent routing + v3 gate + v3 integration coverage passing
- v4 sealed: RBAC + freshness gate, v4 integration, and external dogfood validation passing
- local-first by design: source code stays on your machine

## Current status

| Track | Status |
|---|---|
| v1 | SEALED (tag: v1.0) |
| v2 | SEALED (tag: v2.0) |
| v3 | SEALED (intent routing + v3 gate + v3 integration) |
| v4 | SEALED (RBAC + freshness gate + v4 integration + external dogfood evidence) |
| Active suite | 124 passed, 1 skipped, 0 failed |
| Gate suite | 14 passed, 0 skipped, 0 failed |

## Why this exists

Raw file dumps are expensive and low-signal for assistants. CONTEXTCORE enforces a layered pipeline to deliver smaller, task-relevant context with measurable quality gates.

## Layer Status

- L1 Static Analysis (AST): SEALED
- L4 Dependency Graph (SQLite): SEALED
- L5 Compression Emitter (Structured Markdown): SEALED
- L3 Intent Engine (task routing): SEALED
- L2 Temporal/Freshness: Implemented staleness/freshness validation and reporting; full temporal decision graph expansion is future work.

## Proven results

### v4 seal (sealed)

| Metric | Result | Target |
|---|---|---|
| RBAC correctness | 0 leaks across developer/auditor/maintainer | 0 unauthorized nodes |
| Freshness correctness | stale labeling PASS, 0 false positives, reindex clears PASS | PASS |
| External validation | scrapy dogfood run archived on 445 Python files | 200-500 file real project |

### v1 gate (sealed)

| Metric | Result | Target |
|---|---|---|
| Compression ratio | 11.38x | >5x |
| Accuracy on eval set | 10/10 (100%) | >=80% |
| Parse failures | 0/20 files | 0 |

### v2 gate (sealed)

| Metric | Result | Target |
|---|---|---|
| Subgraph accuracy | 10/10 | >=8/10 |
| Average latency | 10.8ms | <=500ms |
| Average tokens | 577 | <=600 |

## Quick start

### Install from PyPI

```bash
pip install contextcore-ai-toolkit==4.0.0
contextcore --help
```

### Install from source (contributors)

```bash
pip install -e ".[dev]"
python tests/run_all.py
python tests/run_all.py --gate
```

## CLI usage

```bash
contextcore index ./sample_project
contextcore status
contextcore query "where does token counting happen"
contextcore diff
```

## Documentation map

- [PROJECT.md](PROJECT.md): roadmap and version dashboards
- [CONTEXT.md](CONTEXT.md): session log and benchmark tracker
- [DECISIONS.md](DECISIONS.md): architecture decisions (ADRs)
- [tests/TEST_MANIFEST.md](tests/TEST_MANIFEST.md): test inventory and gate map
- [.contextcore/context_snapshot.md](.contextcore/context_snapshot.md): current execution snapshot
- [CLAUDE.md](CLAUDE.md): operational rules used during implementation

## Safety and privacy

- local processing only
- no source-code telemetry
- no external API calls with source code content

## License

MIT (see [LICENSE](LICENSE))
