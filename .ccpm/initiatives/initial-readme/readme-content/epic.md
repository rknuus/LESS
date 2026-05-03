---
name: readme-content
status: backlog
created: 2026-05-03T13:16:22Z
progress: 0%
initiative: .ccpm/initiatives/initial-readme/initial-readme.md
depends_on: []
---

# Epic: readme-content

## Overview

Write the project's first user-facing `README.md` covering what LESS is, how to set it up, and how to use the CLI to index and search a directory of eBooks. The single deliverable is `README.md` at the repository root.

## Scope

**Included:**
- A single Markdown file at `README.md` in the repository root.
- Sections, in order: *What is LESS*, *Why semantic search*, *Supported formats*, *Setup*, *Usage*, *How it works*.
- Runnable command examples for both indexing and searching.

**Excluded:**
- Architecture / design documentation.
- Contributor guide, code of conduct, license file.
- Badges, screenshots, animated demos.
- Translations.

## Dependencies

- None within this initiative.
- External: assumes a stable enough CLI surface (command names like `index` and `search`) to document. If the CLI is not yet implemented, the README is written against the *intended* interface and will be revised once the implementation lands.
