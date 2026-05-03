---
name: bootstrap
status: backlog
created: 2026-05-03T14:18:44Z
progress: 0%
initiative: .ccpm/initiatives/cli-skeleton/cli-skeleton.md
depends_on: []
---

# Epic: bootstrap

## Overview

Bootstrap the `ebless` Python 3 package: project scaffolding managed by `uv`, a Click-based CLI exposing the `ebless` command, an `index` subcommand wired to a replaceable stub indexer that prints `would index <path>` and returns, plus a pytest suite covering the CLI surface. After this epic, `uv sync` produces a working `ebless` on PATH and `pytest` exits 0.

## Architecture Decisions

- **Package layout** — single top-level package `ebless` with submodules organized by concern (per project CLAUDE.md): `ebless/cli.py` for the Click command surface, `ebless/indexer.py` for the stub (its function signature is the contract for the future real indexer), `ebless/__init__.py` exposing nothing (CLI is the public surface). Tests live in a sibling `tests/` directory at the repo root.
- **CLI shape** — Click `@click.group()` for `ebless`, `@cli.command("index")` for the subcommand. Using a group from day one avoids restructuring when `search` is added later.
- **Path validation** — delegated to Click's `click.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path)`. Click emits a clear error and exits non-zero on bad input — no custom validation code.
- **Stub contract** — `ebless.indexer.index_books(path: pathlib.Path) -> None` prints `would index <path>` to stdout and returns. Using a `Path` (not `str`) at the boundary is the natural Python convention and matches what Click hands back. The future real indexer keeps the same signature.
- **Build & dependency management** — `uv` with PEP 621 `pyproject.toml`. `uv.lock` is committed. Build backend: `hatchling` (lightweight, official, plays cleanly with `uv`).
- **Entry point** — `[project.scripts]` table maps `ebless = "ebless.cli:cli"` so `uv sync` (or `uv pip install -e .`) puts `ebless` on PATH.
- **Test framework** — `pytest` invoked via `uv run pytest`. CLI tests use Click's `CliRunner` for in-process invocation and pytest's `tmp_path` fixture for filesystem isolation. The stub is exercised via the runner, not patched out — the real test of the wiring is that running `ebless index <tmp_path>` produces the stub's output on stdout.
- **Minimum Python** — 3.11, declared in `pyproject.toml` `requires-python`.

## Technical Approach

### Backend Services

There is no backend service in this epic — `ebless` is a local CLI. The "service" boundary that matters is `indexer.index_books(path)`, which is a function-level seam designed to be replaced wholesale in a later initiative without touching the CLI.

### Frontend Components

N/A — terminal CLI.

### Infrastructure

- `pyproject.toml` (PEP 621): project metadata, `requires-python = ">=3.11"`, `dependencies = ["click>=8.1"]`, `[project.optional-dependencies] dev = ["pytest>=8"]`, `[project.scripts] ebless = "ebless.cli:cli"`, `[build-system]` declaring `hatchling`.
- `uv.lock` — committed; produced by `uv sync` / `uv lock`.
- `.python-version` — optional; pin to 3.11 if convenient for `uv`'s auto-provisioning.

## Implementation Strategy

Single coherent unit of work. Tests are written alongside the implementation — the project CLAUDE.md mandates tests with assertions for all code, and the surface here is small enough that splitting test creation from implementation would just create coordination overhead. Order within the unit:

1. Initialize `pyproject.toml` + `uv` lockfile, package directory, empty modules.
2. Implement `ebless/indexer.py` stub.
3. Implement `ebless/cli.py` with the Click group and `index` subcommand wired to the stub.
4. Write `tests/test_cli.py` covering the three acceptance paths (US-2 happy, US-2 missing-path, stub-invocation assertion).
5. Update `README.md` Install + Usage sections to reflect the real working commands (`uv sync`, `uv run ebless index <path>`).

Verification at the end of the unit: `uv sync` succeeds, `uv run ebless --help` lists `index`, `uv run ebless index <tmp-dir>` prints `would index <tmp-dir>`, `uv run ebless index /no/such/path` exits non-zero, `uv run pytest` exits 0.

## Task Breakdown Preview

A single task — `Bootstrap ebless package with index CLI and tests` — owns the entire epic. Decomposing further would split the package skeleton from the code that lives inside it, which adds branch-handoff overhead without parallelism (each step depends on the previous one).

## Dependencies

- **External**: Python 3.11+ on the developer's machine; `uv` installed.
- **Internal**: None — this is the foundation epic.

## Success Criteria (Technical)

- `uv sync` in a fresh clone exits 0 and produces a working venv with `ebless` available via `uv run ebless`.
- `uv run ebless --help` lists `index` as a subcommand.
- `uv run ebless index <existing-dir>` prints exactly `would index <existing-dir>` and exits 0.
- `uv run ebless index <nonexistent-path>` exits non-zero with a Click validation error.
- `uv run pytest` exits 0 with all tests passing.
- `README.md` Install and Usage sections show the real, working commands.
- `uv.lock` is committed; `pyproject.toml` declares Click as the only runtime dependency.

## Estimated Effort

XS — a few hours of focused work. The pieces are small and well-understood; the interesting decisions (language, framework, tool, stub shape) are already settled by the initiative.
