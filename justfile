default:
    @just --list

sync:
    uv sync

alias install := sync

test:
    uv run pytest

lint:
    uv run ruff check

format:
    uv run ruff format

run *args:
    uv run ebless {{args}}

clean:
    rm -rf .venv dist build *.egg-info
