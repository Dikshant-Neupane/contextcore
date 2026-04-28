<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0A0A0A,100:222222&height=140&section=header&text=ContextCore&fontColor=F5F5F5&fontSize=56&fontAlignY=50" width="100%" />

**Engineering the bridge between large codebases and AI context windows.**

[![PyPI](https://img.shields.io/pypi/v/contextcore-ai-toolkit?style=flat-square&label=pypi&color=ffffff&labelColor=111111)](https://pypi.org/project/contextcore-ai-toolkit/)
[![Python](https://img.shields.io/pypi/pyversions/contextcore-ai-toolkit?style=flat-square&color=ffffff&labelColor=111111)](https://pypi.org/project/contextcore-ai-toolkit/)
[![License](https://img.shields.io/github/license/Dikshant-Neupane/contextcore?style=flat-square&color=ffffff&labelColor=111111)](LICENSE)

[Install](#installation) • [Features](#features) • [Usage](#usage) • [Architecture](#architecture) • [Quality](#quality-gates)

</div>

---

## The Problem

Large repositories do not fit cleanly into LLM context windows. Raw file dumps are noisy, costly, and hard for assistants to reason over.

## The Approach

**ContextCore** is a local-first, AST-driven context engine that indexes source code into a structured graph and returns ranked, compact context through a deterministic CLI.

## Features

- Layered context pipeline with sealed versions (`v1` to `v4`)
- Role-aware retrieval (`developer`, `auditor`, `maintainer`)
- Freshness-aware query labeling via staleness checks
- Structured Markdown output for assistant-friendly consumption
- Local processing only, no source upload to external APIs

## Installation

### From PyPI (recommended)

```bash
pip install contextcore-ai-toolkit
contextcore --help
```

### From source (contributors)

```bash
pip install -e ".[dev]"
python tests/run_all.py
python tests/run_all.py --gate
```

## Usage

```bash
# 1) Index a project
contextcore index ./sample_project

# 2) Check graph status
contextcore status

# 3) Query ranked context
contextcore query "where does token counting happen"

# 4) Show changes since last index
contextcore diff
```

### Role and freshness controls

```bash
contextcore query "auth flow" --role auditor --stale-after-days 30
```

## Architecture

| Layer | Purpose | Status |
|---|---|---|
| L1 | Static analysis (AST extraction) | SEALED |
| L2 | Temporal/freshness logic | Implemented (decision-graph expansion is future work) |
| L3 | Intent routing | SEALED |
| L4 | Dependency/context graph (SQLite) | SEALED |
| L5 | Structured Markdown emitter | SEALED |

## Quality Gates

| Track | Status |
|---|---|
| v1 | SEALED (`v1.0`) |
| v2 | SEALED (`v2.0`) |
| v3 | SEALED |
| v4 | SEALED (RBAC + freshness + external dogfood evidence) |
| Active suite | 124 passed, 1 skipped, 0 failed |
| Gate suite | 14 passed, 0 skipped, 0 failed |

### Key sealed metrics

| Metric | Result | Target |
|---|---|---|
| v1 compression ratio | 11.38x | >5x |
| v1 eval accuracy | 10/10 (100%) | >=80% |
| v2 subgraph accuracy | 10/10 | >=8/10 |
| v2 avg latency | 10.8ms | <=500ms |
| v4 external validation | `scrapy` run on 445 Python files | 200-500 file real project |

## Output Contract

`contextcore query` emits structured Markdown with parseable metadata sections, optimized for assistant pipelines and automation.

## Documentation

- [PROJECT.md](PROJECT.md): roadmap and version dashboards
- [CONTEXT.md](CONTEXT.md): execution log and benchmark tracker
- [DECISIONS.md](DECISIONS.md): architecture decisions (ADRs)
- [tests/TEST_MANIFEST.md](tests/TEST_MANIFEST.md): test inventory and gate map
- [.contextcore/context_snapshot.md](.contextcore/context_snapshot.md): current execution snapshot

## Security and Privacy

- Local processing only
- No source-code telemetry
- No external API calls with source code content

## License

MIT (see [LICENSE](LICENSE))
