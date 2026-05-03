import logging
import os
from collections.abc import Iterator
from pathlib import Path

logger = logging.getLogger(__name__)

_INDEXABLE_EXTENSIONS = frozenset({".pdf"})


def find_indexable_files(root: Path) -> list[Path]:
    return sorted(_walk(root))


def _walk(directory: Path) -> Iterator[Path]:
    try:
        scanner = os.scandir(directory)
    except (PermissionError, OSError) as exc:
        logger.warning(
            "cannot read directory",
            extra={"path": str(directory), "error": str(exc)},
        )
        return

    with scanner:
        for entry in scanner:
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    yield from _walk(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    if Path(entry.name).suffix.lower() in _INDEXABLE_EXTENSIONS:
                        yield Path(entry.path)
            except OSError as exc:
                logger.warning(
                    "cannot read directory entry",
                    extra={"path": entry.path, "error": str(exc)},
                )
