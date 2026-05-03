from pathlib import Path

from ebless.discovery import find_indexable_files


def index_books(path: Path) -> None:
    for found in find_indexable_files(path):
        print(found.resolve())
