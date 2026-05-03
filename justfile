default:
    @just --list

sync:
    uv sync

alias install := sync

test:
    uv run pytest

lint:
    uv run ruff check

typecheck:
    ty check ebless tests --error-on-warning

format:
    uv run ruff format

run *args:
    uv run ebless {{args}}

clean:
    rm -rf .venv dist build *.egg-info
