---
name: cli-skeleton
description: Python 3 project skeleton and `ebless index <path>` CLI command wired to a stub indexer
status: backlog
worktree: false
created: 2026-05-03T14:14:18Z
---

# Initiative: cli-skeleton

## Executive Summary

Bootstrap the `ebless` project as a Python 3 package with a Click-based CLI and ship the first user-visible command, `ebless index <path>`. The command parses arguments and invokes a stub indexer that prints "would index <path>" and returns. No actual file discovery, extraction, embedding, or storage is implemented in this initiative — the goal is a working end-to-end skeleton that future initiatives can flesh out.

## Problem Statement

The repository currently contains only a README describing the intended product. There is no Python package, no CLI entry point, no test harness, and no install path. Without a runnable skeleton, every subsequent initiative would have to re-litigate baseline tooling decisions and would have nowhere to attach code. This initiative establishes that baseline: a packaged Python project that can be installed locally and exposes the `ebless` command, with `index` as a working (stubbed) subcommand. Future initiatives — real indexer, search command, vector store — plug into this skeleton without touching tooling.

## User Stories

**US-1: Developer installs the package locally**
As a developer working on ebless, I can install the project in editable mode (e.g. `pip install -e .`) so that the `ebless` command becomes available on my PATH and points at the source tree.
- Acceptance: After install, running `ebless --help` from any directory exits 0 and prints the top-level command summary including the `index` subcommand.

**US-2: User runs the index command against a directory**
As a user, I can run `ebless index <path>` and the command accepts the path argument, validates it exists, and invokes the stub indexer.
- Acceptance: `ebless index /some/dir` (where `/some/dir` exists) prints `would index /some/dir` to stdout and exits 0.
- Acceptance: `ebless index /does/not/exist` exits non-zero with a clear error message.
- Acceptance: `ebless index --help` shows usage including the path argument.

**US-3: Developer runs the test suite**
As a developer, I can run the project's tests with a single command and see them all pass, so that future changes have a regression net.
- Acceptance: A documented test command (e.g. `pytest`) exits 0 against a fresh checkout with no manual setup beyond the install step.
- Acceptance: Tests cover the CLI invocation paths in US-2 (happy path + missing-path error path) and assert the stub is called.

## Functional Requirements

- **FR-1**: The project is a standard Python 3 package with a `pyproject.toml` declaring dependencies (Click) and an entry point that exposes the `ebless` command.
- **FR-2**: The CLI is implemented with Click and uses a command group so that future subcommands (e.g. `search`) can be added without restructuring.
- **FR-3**: The `index` subcommand accepts exactly one positional argument: a filesystem path.
- **FR-4**: The `index` subcommand validates that the path exists and is a directory before invoking the stub. Validation failures exit non-zero with a clear message; Click's built-in `click.Path(exists=True, file_okay=False, dir_okay=True)` is acceptable.
- **FR-5**: The stub indexer is a separate module/function (not inlined in the CLI handler), so it can be replaced in a later initiative without touching the CLI surface. It prints exactly `would index <path>` to stdout and returns.
- **FR-6**: The package layout separates CLI, stub indexer, and tests into distinct modules organized by concern (per project CLAUDE.md: "Modularize by concern, not by technical layer").
- **FR-7**: A test suite using pytest covers the CLI happy path, the missing-path error path, and the stub-indexer invocation.

## Non-Functional Requirements

- **Python 3.11+** as the minimum runtime — the project targets a recent runtime, and locking to a current minor avoids legacy-compatibility branches in subsequent initiatives.
- **No runtime dependencies beyond Click** in this initiative. Embedding/PDF/EPUB/vector-store libraries are explicitly deferred.
- **Editable install must work** from a clean clone: `pip install -e .` (or equivalent with `uv`) produces a working `ebless` on PATH.
- **README is updated** with the actual install and run commands once the skeleton is real, replacing the current "Follow the installation instructions for your platform." placeholder.
- **Tests are deterministic** — no network calls, no filesystem state outside `tmp_path` fixtures.

## Success Criteria

- Running `pip install -e .` (or `uv pip install -e .`) in a fresh clone succeeds and puts `ebless` on PATH.
- `ebless --help` lists the `index` subcommand.
- `ebless index <existing-dir>` prints `would index <existing-dir>` and exits 0.
- `ebless index <nonexistent-path>` exits non-zero with a clear error (Click's default error message is acceptable).
- `pytest` exits 0 with all tests passing on a fresh clone.
- README's Install and Usage sections reflect the real, working commands.

## Constraints & Assumptions

- **Language**: Python 3 (Python 3.11+).
- **CLI framework**: Click.
- **Test framework**: pytest (idiomatic for Python; aligns with project CLAUDE.md's "Write and pass tests before finalizing").
- **Packaging**: PEP 621 `pyproject.toml`. Build backend choice (setuptools, hatchling, etc.) is left to the implementer; pick the simplest option that works.
- **No real indexing logic**: The stub is the deliverable for the indexing path in this initiative. The interface between CLI and indexer is what matters — it must be replaceable without CLI changes.
- **Single-platform development**: macOS/Linux target; Windows is not in scope for this initiative.
- **No CI configuration**: Pipelines are out of scope here; running `pytest` locally is the verification path.

## Out of Scope

- Actual file discovery (walking the directory, filtering by extension).
- Text extraction from PDF or EPUB.
- Embedding model integration.
- Vector database setup or storage.
- The `ebless search` command.
- The `--limit` and `--book` options described in the README.
- Re-index optimization (skipping unchanged files).
- Logging configuration, structured output, progress bars.
- CI/CD, release automation, PyPI publishing.
- Windows support, cross-platform path edge cases.

## Dependencies

- Python 3.11+ available on the developer's machine.
- `pip` (or `uv`) for the editable install.
- Click (added as the only runtime dependency).
- pytest (added as a dev/test dependency).
