# LESS — LLM Empowered Semantic Search

A command-line tool for indexing and searching personal eBook libraries by meaning, not keywords. LESS reads your books in common formats (PDF, EPUB, ...), splits them into paragraphs, embeds each paragraph as a vector, and stores the vectors in a local database so you can later retrieve passages by semantic similarity to a natural-language query.

## Why semantic search

Traditional full-text search (`grep`, library indexers) is great when you remember the exact wording, but eBook libraries are full of ideas you only remember roughly. Semantic search lets you query in your own words — *"the part where the author argues against premature optimization"* — and surfaces relevant passages even when none of those words appear in the book.

## Supported formats

LESS aims to support the most common eBook formats:

- **PDF** (`.pdf`)
- **EPUB** (`.epub`)
- Additional formats may be added over time.

## Setup

### Prerequisites

- A recent runtime to execute the LESS CLI (see your platform's installation instructions).
- A vector database for storing paragraph embeddings (configurable; LESS ships with a sensible local default).
- Access to an embedding model — either a local model or an API endpoint (configurable).

### Install

Follow the installation instructions for your platform, then verify the install:

```sh
less --version
```

If the version prints successfully, LESS is on your `PATH` and ready to use.

### Configure

LESS reads its configuration (vector database location, embedding backend, default indexing options) from a config file in your user directory. Run:

```sh
less config init
```

to create a config file with default values, then edit it to point to your preferred vector database and embedding backend.

## Usage

### Index a directory of books

Point LESS at a directory and have it index every supported eBook it finds:

```sh
less index <path/to/books>
```

LESS walks the directory, extracts paragraphs from each supported file, computes embeddings, and stores them. Re-running `index` on the same directory only processes files that have changed since the last run.

### Search the index

Run a natural-language query against your indexed library:

```sh
less search "<query>"
```

Example:

```sh
less search "passages about the value of slow, deliberate thinking"
```

LESS returns the top matching paragraphs, each annotated with the source book and a similarity score, so you can quickly jump to the relevant passage.

### Common options

- `--limit <N>` — return at most N results (default: a small handful).
- `--book <name>` — restrict the search to a single indexed book.

See `less <command> --help` for the full list of options on each command.

## How it works

At a high level, LESS does three things:

1. **Extract.** For every supported eBook in the indexed directory, LESS extracts its text and splits it into paragraphs.
2. **Embed.** Each paragraph is passed to the configured embedding model, which returns a fixed-size vector capturing the paragraph's meaning.
3. **Store and query.** Vectors and their source-paragraph references are written to a vector database. At search time, the query string is embedded with the same model and the database returns the paragraphs whose vectors lie closest to the query vector.

Because retrieval is based on vector similarity rather than exact word matches, LESS finds passages that are conceptually related to the query even when they share no surface vocabulary.
