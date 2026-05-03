"""Per-library inventory: JSON at ~/.ebless/inventory.json keyed by resolved
root, atomic temp+fsync+replace on save, single-process only."""

import json
import os
from pathlib import Path
from typing import NamedTuple, TypedDict

INVENTORY_PATH: Path = Path.home() / ".ebless" / "inventory.json"


class FileFingerprint(TypedDict):
    mtime: float
    size: int


class ChangeSet(NamedTuple):
    added: list[str]
    modified: list[str]
    unchanged: list[str]
    removed: list[str]


def load(library_root: Path, path: Path = INVENTORY_PATH) -> dict[str, FileFingerprint]:
    document = _read_document(path)
    section = _as_str_object_dict(document.get(_root_key(library_root)))
    files = _as_str_object_dict(section.get("files"))
    result: dict[str, FileFingerprint] = {}
    for name, entry in files.items():
        fingerprint = _coerce_fingerprint(entry)
        if fingerprint is not None:
            result[name] = fingerprint
    return result


def classify(
    library_root: Path,
    found: list[Path],
    previous: dict[str, FileFingerprint],
) -> ChangeSet:
    root = library_root.resolve()
    current = {_relative(root, file): _stat_fingerprint(file) for file in found}
    added: list[str] = []
    modified: list[str] = []
    unchanged: list[str] = []
    for name, fingerprint in current.items():
        prior = previous.get(name)
        if prior is None:
            added.append(name)
        elif (prior["mtime"], prior["size"]) == (fingerprint["mtime"], fingerprint["size"]):
            unchanged.append(name)
        else:
            modified.append(name)
    removed = [name for name in previous if name not in current]
    return ChangeSet(
        added=sorted(added),
        modified=sorted(modified),
        unchanged=sorted(unchanged),
        removed=sorted(removed),
    )


def save(library_root: Path, found: list[Path], path: Path = INVENTORY_PATH) -> None:
    root = library_root.resolve()
    document = _read_document(path)
    document[str(root)] = {
        "files": {_relative(root, file): _stat_fingerprint(file) for file in found},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, document)


def _atomic_write(path: Path, payload: dict[str, object]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _read_document(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        return {}
    return {str(key): value for key, value in data.items()}


def _root_key(library_root: Path) -> str:
    return str(library_root.resolve())


def _relative(root: Path, file: Path) -> str:
    return file.relative_to(root).as_posix()


def _stat_fingerprint(file: Path) -> FileFingerprint:
    info = file.stat()
    return {"mtime": info.st_mtime, "size": info.st_size}


def _coerce_fingerprint(entry: object) -> FileFingerprint | None:
    fields = _as_str_object_dict(entry)
    mtime = fields.get("mtime")
    size = fields.get("size")
    if not isinstance(mtime, int | float) or not isinstance(size, int):
        return None
    return {"mtime": float(mtime), "size": size}


def _as_str_object_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}
