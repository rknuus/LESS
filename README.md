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

- A recent runtime to execute the ebless CLI (see your platform's installation instructions).

### Install

Follow the installation instructions for your platform.

## Usage

### Index a directory of books

Point ebless at a directory and have it index every supported eBook it finds:

```sh
ebless index <path/to/books>
```

ebless walks the directory, extracts paragraphs from each supported file, computes embeddings, and stores them. Re-running `index` on the same directory only processes files that have changed since the last run.

### Search the index

Run a natural-language query against your indexed library:

```sh
ebless search "<query>"
```

Example:

```sh
ebless search "passages about the value of slow, deliberate thinking"
```

ebless returns the top matching paragraphs, each annotated with the source book and a similarity score, so you can quickly jump to the relevant passage.

### Common options

- `--limit <N>` — return at most N results (default: a small handful).
- `--book <name>` — restrict the search to a single indexed book.

See `ebless <command> --help` for the full list of options on each command.

## How it works

At a high level, ebless does three things:

1. **Extract.** For every supported eBook in the indexed directory, ebless extracts its text and splits it into paragraphs.
2. **Embed.** Each paragraph is passed to the configured embedding model, which returns a fixed-size vector capturing the paragraph's meaning.
3. **Store and query.** Vectors and their source-paragraph references are written to a vector database. At search time, the query string is embedded with the same model and the database returns the paragraphs whose vectors lie closest to the query vector.

Because retrieval is based on vector similarity rather than exact word matches, ebless finds passages that are conceptually related to the query even when they share no surface vocabulary.
