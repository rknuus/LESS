import json

import pytest

from ebless.inventory import FileFingerprint, detect_changes, load, save


def _write_pdf(path, content=b"hello"):
    path.write_bytes(content)
    return path


def test_load_returns_empty_when_file_missing(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    inventory_path = tmp_path / "inventory.json"
    assert load(library, path=inventory_path) == {}


def test_load_returns_empty_when_library_section_missing(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    inventory_path = tmp_path / "inventory.json"
    inventory_path.write_text(
        json.dumps({str(other.resolve()): {"files": {"x.pdf": {"mtime": 1.0, "size": 1}}}}),
        encoding="utf-8",
    )
    assert load(library, path=inventory_path) == {}


def test_load_returns_files_dict_for_matching_library(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    inventory_path = tmp_path / "inventory.json"
    payload = {
        str(library.resolve()): {
            "files": {
                "a.pdf": {"mtime": 1.5, "size": 10},
                "sub/b.pdf": {"mtime": 2.5, "size": 20},
            }
        }
    }
    inventory_path.write_text(json.dumps(payload), encoding="utf-8")

    result = load(library, path=inventory_path)
    assert result == {
        "a.pdf": {"mtime": 1.5, "size": 10},
        "sub/b.pdf": {"mtime": 2.5, "size": 20},
    }


def test_load_ignores_unknown_fields_per_file(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    inventory_path = tmp_path / "inventory.json"
    payload = {
        str(library.resolve()): {
            "files": {
                "a.pdf": {"mtime": 1.0, "size": 5, "hash": "deadbeef", "future": [1, 2]},
            }
        }
    }
    inventory_path.write_text(json.dumps(payload), encoding="utf-8")

    result = load(library, path=inventory_path)
    assert result == {"a.pdf": {"mtime": 1.0, "size": 5}}


def test_detect_changes_marks_new_files_as_added(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    fresh = _write_pdf(library / "fresh.pdf")

    change = detect_changes(library, [fresh], previous={})
    assert change.added == ["fresh.pdf"]
    assert change.modified == []
    assert change.unchanged == []
    assert change.removed == []


def test_detect_changes_marks_unchanged_files_as_unchanged(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    file = _write_pdf(library / "book.pdf", b"data")
    info = file.stat()
    previous: dict[str, FileFingerprint] = {
        "book.pdf": {"mtime": info.st_mtime, "size": info.st_size}
    }

    change = detect_changes(library, [file], previous=previous)
    assert change.unchanged == ["book.pdf"]
    assert change.added == []
    assert change.modified == []
    assert change.removed == []


def test_detect_changes_marks_mtime_change_as_modified(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    file = _write_pdf(library / "book.pdf", b"data")
    info = file.stat()
    previous: dict[str, FileFingerprint] = {
        "book.pdf": {"mtime": info.st_mtime - 100.0, "size": info.st_size}
    }

    change = detect_changes(library, [file], previous=previous)
    assert change.modified == ["book.pdf"]


def test_detect_changes_marks_size_change_as_modified(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    file = _write_pdf(library / "book.pdf", b"data")
    info = file.stat()
    previous: dict[str, FileFingerprint] = {
        "book.pdf": {"mtime": info.st_mtime, "size": info.st_size + 1}
    }

    change = detect_changes(library, [file], previous=previous)
    assert change.modified == ["book.pdf"]


def test_detect_changes_marks_missing_files_as_removed(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    previous: dict[str, FileFingerprint] = {"gone.pdf": {"mtime": 1.0, "size": 10}}

    change = detect_changes(library, [], previous=previous)
    assert change.removed == ["gone.pdf"]


def test_detect_changes_relative_paths_are_posix_form(tmp_path):
    library = tmp_path / "library"
    nested = library / "sub" / "deep"
    nested.mkdir(parents=True)
    file = _write_pdf(nested / "deep.pdf")

    change = detect_changes(library, [file], previous={})
    assert change.added == ["sub/deep/deep.pdf"]


def test_save_creates_parent_directory_when_missing(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    file = _write_pdf(library / "a.pdf")
    inventory_path = tmp_path / "nested" / "deeper" / "inventory.json"

    save(library, [file], path=inventory_path)

    assert inventory_path.exists()
    document = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert str(library.resolve()) in document


def test_save_load_round_trips(tmp_path):
    library = tmp_path / "library"
    library.mkdir()
    a = _write_pdf(library / "a.pdf", b"aaa")
    b = _write_pdf(library / "b.pdf", b"bbbbb")
    inventory_path = tmp_path / "inventory.json"

    save(library, [a, b], path=inventory_path)
    loaded = load(library, path=inventory_path)

    assert set(loaded.keys()) == {"a.pdf", "b.pdf"}
    assert loaded["a.pdf"]["size"] == a.stat().st_size
    assert loaded["b.pdf"]["size"] == b.stat().st_size
    document = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert list(document.keys()) == [str(library.resolve())]


def test_save_preserves_other_library_sections(tmp_path):
    library_a = tmp_path / "A"
    library_b = tmp_path / "B"
    library_a.mkdir()
    library_b.mkdir()
    a_file = _write_pdf(library_a / "a.pdf", b"a")
    b_file = _write_pdf(library_b / "b.pdf", b"bb")
    inventory_path = tmp_path / "inventory.json"

    save(library_a, [a_file], path=inventory_path)
    save(library_b, [b_file], path=inventory_path)

    document = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert str(library_a.resolve()) in document
    assert str(library_b.resolve()) in document
    assert "a.pdf" in document[str(library_a.resolve())]["files"]
    a_loaded = load(library_a, path=inventory_path)
    assert set(a_loaded.keys()) == {"a.pdf"}


def test_save_is_atomic_under_replace_failure(tmp_path, monkeypatch):
    library = tmp_path / "library"
    library.mkdir()
    original_file = _write_pdf(library / "first.pdf", b"first")
    inventory_path = tmp_path / "inventory.json"
    save(library, [original_file], path=inventory_path)
    prior_contents = inventory_path.read_text(encoding="utf-8")

    new_file = _write_pdf(library / "second.pdf", b"second")

    def _raise_oserror(*_args, **_kwargs):
        raise OSError("simulated crash before replace")

    monkeypatch.setattr("os.replace", _raise_oserror)

    with pytest.raises(OSError, match="simulated crash"):
        save(library, [original_file, new_file], path=inventory_path)

    assert inventory_path.read_text(encoding="utf-8") == prior_contents
    assert load(library, path=inventory_path) == {
        "first.pdf": {
            "mtime": original_file.stat().st_mtime,
            "size": original_file.stat().st_size,
        }
    }
