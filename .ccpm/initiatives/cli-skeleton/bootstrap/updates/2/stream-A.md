---
issue: 2
stream: bootstrap
started: 2026-05-03T14:18:44Z
status: in_progress
---
## Scope
- pyproject.toml + uv.lock + hatchling build
- ebless/ package (cli.py, indexer.py, __init__.py)
- tests/test_cli.py
- README.md install/usage refresh

## Progress
- pyproject.toml created (PEP 621, hatchling, click runtime, pytest dev, ebless entry point)
- ebless/ package scaffolded (__init__.py, indexer.py stub, cli.py with Click group + index subcommand)
- tests/test_cli.py created (4 tests: help lists index, happy path, missing path, stub contract via capsys)
- README.md Setup/Install + Usage sections refreshed to use uv
- uv sync succeeded; uv.lock generated
- uv run ebless --help OK (lists index)
- uv run ebless index /tmp/ebless-smoke prints "would index /tmp/ebless-smoke" (exit 0)
- uv run ebless index /does/not/exist exits 2 with Click validation error
- uv run pytest: 4 passed
