"""Per-page blank-line chunking via pypdf; failures emit a static-msg WARNING
and return []; image-only PDFs yield an empty list with no warning."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)

_FAILURE_MSG = "could not extract chunks"


@dataclass(frozen=True)
class Chunk:
    text: str
    source_book: Path
    page_number: int
    ordinal: int


def extract_chunks(path: Path) -> list[Chunk]:
    resolved = path.resolve()
    if not resolved.exists():
        logger.warning(_FAILURE_MSG, extra={"path": str(resolved), "reason": "missing"})
        return []
    try:
        reader = PdfReader(resolved)
        if reader.is_encrypted:
            logger.warning(_FAILURE_MSG, extra={"path": str(resolved), "reason": "encrypted"})
            return []
        chunks: list[Chunk] = []
        ordinal = 0
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text(extraction_mode="layout") or ""
            for fragment in _split_page_text(text):
                chunks.append(
                    Chunk(
                        text=fragment,
                        source_book=resolved,
                        page_number=page_number,
                        ordinal=ordinal,
                    )
                )
                ordinal += 1
        return chunks
    except Exception as exc:
        logger.warning(
            _FAILURE_MSG,
            extra={"path": str(resolved), "reason": type(exc).__name__},
        )
        return []


def _split_page_text(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n+", text)
    return [p.strip() for p in parts if p.strip()]
