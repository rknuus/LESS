import logging
from pathlib import Path

from ebless import inventory
from ebless.discovery import find_indexable_files

logger = logging.getLogger(__name__)


def index_books(path: Path) -> None:
    library_root = path.resolve()
    found = find_indexable_files(library_root)
    previous = inventory.load(library_root, path=inventory.INVENTORY_PATH)
    change_set = inventory.classify(library_root, found, previous)

    for relative in change_set.added + change_set.modified:
        print(library_root / relative)

    for relative in change_set.removed:
        logger.debug("file removed from library", extra={"path": relative})

    logger.info(
        "indexed library",
        extra={
            "library": str(library_root),
            "added": len(change_set.added),
            "modified": len(change_set.modified),
            "removed": len(change_set.removed),
            "unchanged": len(change_set.unchanged),
        },
    )

    inventory.save(library_root, found, path=inventory.INVENTORY_PATH)
