import os
import sys
from pathlib import Path

_INDEXABLE_EXTENSIONS = frozenset({".pdf"})


def find_indexable_files(root: Path) -> list[Path]:
    results: list[Path] = []
    _walk(root, results)
    return sorted(results)


def _walk(directory: Path, results: list[Path]) -> None:
    try:
        entries = list(os.scandir(directory))
    except (PermissionError, OSError) as exc:
        print(f"discovery: cannot read {directory}: {exc}", file=sys.stderr)
        return

    for entry in entries:
        try:
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                _walk(Path(entry.path), results)
            elif entry.is_file(follow_symlinks=False):
                if Path(entry.name).suffix.lower() in _INDEXABLE_EXTENSIONS:
                    results.append(Path(entry.path))
        except OSError as exc:
            print(f"discovery: cannot read {entry.path}: {exc}", file=sys.stderr)
