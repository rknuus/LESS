# ebless — eBook LLM Empowered Semantic Search

A command-line tool for indexing and searching personal eBook libraries by meaning, not keywords. ebless reads your books in common formats (PDF, EPUB, ...), splits them into paragraphs, embeds each paragraph as a vector, and stores the vectors in a local database so you can later retrieve passages by semantic similarity to a natural-language query.

## Why semantic search

Traditional full-text search (`grep`, library indexers) is great when you remember the exact wording, but eBook libraries are full of ideas you only remember roughly. Semantic search lets you query in your own words and surfaces relevant passages even when none of those words appear in the book.

## Supported formats

ebless aims to support the most common eBook formats:

- **PDF** (`.pdf`)
- **EPUB** (`.epub`)
- Additional formats may be added over time.

## Setup

### Prerequisites

- Python 3.11 or newer.
- [`uv`](https://docs.astral.sh/uv/) for dependency management.

### Install

Clone the repository and synchronise the environment:

```sh
uv sync
```

This creates a managed virtual environment, installs ebless in editable mode, and exposes the `ebless` command via `uv run`.

## Usage

### Index a directory of books

Point ebless at a directory and have it list every supported eBook it finds:

```sh
uv run ebless index <path/to/books>
```

ebless walks the directory recursively and prints the absolute path of every supported file it discovers, one per line, in sorted order. See [Current limitations](#current-limitations) for what `index` does not yet do.

### Search the index

Run a natural-language query against your indexed library:

```sh
uv run ebless search "<query>"
```

Example:

```sh
uv run ebless search "passages about the value of slow, deliberate thinking"
```

ebless returns the top matching paragraphs, each annotated with the source book and a similarity score, so you can quickly jump to the relevant passage.

### Common options

- `--limit <N>` — return at most N results (default: a small handful).
- `--book <name>` — restrict the search to a single indexed book.

See `uv run ebless <command> --help` for the full list of options on each command.

## Development

Common development tasks are exposed as [`just`](https://github.com/casey/just) recipes. Run `just` (no args) to list them:

```sh
just            # list available recipes
just sync       # install/refresh dependencies (alias: just install)
just test       # run the test suite
just lint       # ruff check
just format     # ruff format
just run …      # invoke ebless with arbitrary args
just clean      # remove .venv and build artifacts
```

The recipes are thin wrappers — equivalents like `uv run pytest` work too.

## Current limitations

ebless is in early development. The current build ships only the discovery walk used by `index`; everything else described above is the intended product, not the shipped one. In particular:

- **PDF only.** EPUB and other formats are not yet supported.
- **`index` only lists discovered files.** It does not yet extract text, compute embeddings, or persist anything to a vector store.
- **`search` is not yet implemented.** The command surface described above is aspirational.
- **Symlinks are skipped.** Symlinked directories are not descended into and symlinked files are not included in results.
- **Permission errors are warned-and-skipped.** When a directory cannot be read, ebless writes a warning to stderr and continues the walk; it does not abort.
- **macOS / Linux only at this time.**

## How it works

At a high level, ebless does three things:

1. **Extract.** For every supported eBook in the indexed directory, ebless extracts its text and splits it into paragraphs.
2. **Embed.** Each paragraph is passed to the configured embedding model, which returns a fixed-size vector capturing the paragraph's meaning.
3. **Store and query.** Vectors and their source-paragraph references are written to a vector database. At search time, the query string is embedded with the same model and the database returns the paragraphs whose vectors lie closest to the query vector.

Because retrieval is based on vector similarity rather than exact word matches, ebless finds passages that are conceptually related to the query even when they share no surface vocabulary.
