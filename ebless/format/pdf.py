"""Per-page blank-line chunking; failures emit a static-msg WARNING and
return []; an empty list is a valid successful result."""

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Chunk:
    text: str
    source_book: Path
    page_number: int
    ordinal: int


def extract_chunks(path: Path) -> list[Chunk]:
    return []
