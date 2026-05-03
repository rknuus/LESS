---
name: initial-readme
description: Initial README explaining what LESS is and how to set up and use the CLI
status: backlog
worktree: false
created: 2026-05-03T13:08:41Z
---

# Initiative: initial-readme

## Executive Summary

Create the project's first `README.md` so prospective users of LESS (LLM Empowered Semantic Search) can understand what the tool does, install it, and run their first index/search against an eBook collection without needing to read the source.

## Problem Statement

LESS is a CLI for indexing and semantically searching eBook files (PDF, EPUB, ...) by embedding each paragraph into a vector database and querying by similarity. The repository currently has no user-facing documentation, so a new user landing on the repo cannot answer:

- What does this tool do, and why would I use it instead of a keyword search?
- How do I install it and its dependencies?
- How do I index a folder of books and run my first search?

## User Stories

- **As a prospective user**, I want a one-paragraph description of LESS at the top of the README so I can decide within seconds whether the tool fits my use case.
  - *Acceptance*: A "What is LESS" section appears above the fold and names the supported file formats and the semantic-search value proposition.
- **As a new user setting up the tool**, I want clear setup instructions so I can install LESS and its dependencies without trial and error.
  - *Acceptance*: A "Setup" section lists prerequisites (runtime, vector DB, embedding model/API), installation commands, and a verification step.
- **As a new user running my first search**, I want a minimal end-to-end usage example so I can index a sample directory and run a query within five minutes.
  - *Acceptance*: A "Usage" section shows the index command and the search command with concrete example arguments and expected output shape.

## Functional Requirements

1. The README is a single Markdown file at the repository root named `README.md`.
2. It contains, at minimum, these sections in this order: *What is LESS*, *Why semantic search*, *Supported formats*, *Setup*, *Usage*, *How it works* (brief).
3. Each command shown is a runnable example with placeholder paths the reader can substitute.
4. Links (if any) use Markdown link syntax — no raw URLs in body text.

## Non-Functional Requirements

- **Tone**: concise and practical; assumes the reader is technically literate but new to LESS.
- **Length**: aim for under one screen of "above the fold" before deeper sections; full file under ~200 lines.
- **Style**: plain Markdown, no badges, no HTML, no images.

## Success Criteria

- A new user who only reads the README can install LESS, index a directory of eBooks, and run a first search successfully.
- The README answers the three questions in *Problem Statement* without the reader needing to open any source file.

## Constraints & Assumptions

- **Constraint**: Markdown only. No badges, no embedded images, no shields, no HTML.
- **Constraint**: Must remain accurate as the CLI evolves — keep examples generic enough that small interface changes do not invalidate them.
- **Assumption**: The CLI's command surface (e.g., `index`, `search`) and configuration mechanism are either already designed or will be defined by the time this README is written. If they are not, this initiative will surface that gap.

## Out of Scope

- Architecture / design documentation (belongs in a separate `ARCHITECTURE.md` or `docs/` initiative).
- Contributor guide, code of conduct, license file (separate concerns).
- Tutorial-style long-form walkthroughs.
- Badges, screenshots, animated demos.
- Translations / non-English versions.

## Dependencies

- Stable enough CLI surface to document (command names and basic flags). If the CLI does not yet exist, the README will be written against the *intended* interface and revised once the implementation lands.
