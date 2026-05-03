import logging
import sys

import pytest

from ebless.discovery import find_indexable_files


def test_empty_dir_returns_empty_list(tmp_path):
    assert find_indexable_files(tmp_path) == []


def test_finds_pdf_at_top_level(tmp_path):
    pdf = tmp_path / "book.pdf"
    pdf.touch()
    assert find_indexable_files(tmp_path) == [pdf]


def test_recurses_into_subdirs(tmp_path):
    top = tmp_path / "top.pdf"
    sub = tmp_path / "sub"
    sub.mkdir()
    nested = sub / "nested.pdf"
    deeper = sub / "deeper"
    deeper.mkdir()
    deepest = deeper / "deepest.pdf"
    top.touch()
    nested.touch()
    deepest.touch()
    assert find_indexable_files(tmp_path) == sorted([top, nested, deepest])


def test_case_insensitive_extension(tmp_path):
    upper = tmp_path / "Book.PDF"
    mixed = tmp_path / "tome.Pdf"
    lower = tmp_path / "note.pdf"
    upper.touch()
    mixed.touch()
    lower.touch()
    assert find_indexable_files(tmp_path) == sorted([upper, mixed, lower])


def test_non_pdf_files_excluded(tmp_path):
    pdf = tmp_path / "real.pdf"
    pdf.touch()
    (tmp_path / "book.epub").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "image.png").touch()
    assert find_indexable_files(tmp_path) == [pdf]


def test_includes_hidden_files(tmp_path):
    hidden = tmp_path / ".hidden.pdf"
    hidden.touch()
    assert hidden in find_indexable_files(tmp_path)


def test_includes_hidden_directories(tmp_path):
    hidden_dir = tmp_path / ".hiddendir"
    hidden_dir.mkdir()
    pdf = hidden_dir / "secret.pdf"
    pdf.touch()
    assert pdf in find_indexable_files(tmp_path)


def test_skips_symlink_to_file(tmp_path):
    real_dir = tmp_path / "real"
    walk_root = tmp_path / "walk"
    real_dir.mkdir()
    walk_root.mkdir()
    real_pdf = real_dir / "real.pdf"
    real_pdf.touch()
    (walk_root / "link.pdf").symlink_to(real_pdf)
    assert find_indexable_files(walk_root) == []


def test_skips_symlink_to_directory(tmp_path):
    real_dir = tmp_path / "real"
    walk_root = tmp_path / "walk"
    real_dir.mkdir()
    walk_root.mkdir()
    (real_dir / "inside.pdf").touch()
    (walk_root / "link_to_dir").symlink_to(real_dir, target_is_directory=True)
    assert find_indexable_files(walk_root) == []


def test_broken_symlink_does_not_break_walk(tmp_path):
    pdf = tmp_path / "real.pdf"
    pdf.touch()
    (tmp_path / "broken.pdf").symlink_to(tmp_path / "missing.pdf")
    assert find_indexable_files(tmp_path) == [pdf]


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="chmod 0o000 doesn't strip read perms on Windows",
)
def test_unreadable_subdir_warns_and_continues(tmp_path, caplog):
    discovery_logger = logging.getLogger("ebless.discovery")
    caplog.set_level(logging.WARNING, logger="ebless.discovery")
    discovery_logger.addHandler(caplog.handler)
    readable = tmp_path / "open"
    closed = tmp_path / "closed"
    readable.mkdir()
    closed.mkdir()
    (readable / "ok.pdf").touch()
    (closed / "hidden.pdf").touch()
    closed.chmod(0o000)
    try:
        results = find_indexable_files(tmp_path)
        assert (readable / "ok.pdf") in results
        assert all("closed" not in str(p) for p in results)
        matching = [
            r
            for r in caplog.records
            if r.levelname == "WARNING"
            and r.msg == "cannot read directory"
            and getattr(r, "path", None) == str(closed)
        ]
        assert matching
    finally:
        closed.chmod(0o700)
        discovery_logger.removeHandler(caplog.handler)


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="chmod 0o000 doesn't strip read perms on Windows",
)
def test_unreadable_root_returns_empty(tmp_path, caplog):
    discovery_logger = logging.getLogger("ebless.discovery")
    caplog.set_level(logging.WARNING, logger="ebless.discovery")
    discovery_logger.addHandler(caplog.handler)
    closed = tmp_path / "closed_root"
    closed.mkdir()
    (closed / "x.pdf").touch()
    closed.chmod(0o000)
    try:
        results = find_indexable_files(closed)
        assert results == []
        matching = [
            r
            for r in caplog.records
            if r.levelname == "WARNING"
            and r.msg == "cannot read directory"
            and getattr(r, "path", None) == str(closed)
        ]
        assert matching
    finally:
        closed.chmod(0o700)
        discovery_logger.removeHandler(caplog.handler)


def test_returns_sorted_list(tmp_path):
    sub_b = tmp_path / "b"
    sub_a = tmp_path / "a"
    sub_b.mkdir()
    sub_a.mkdir()
    p1 = tmp_path / "z.pdf"
    p2 = sub_a / "alpha.pdf"
    p3 = sub_b / "beta.pdf"
    p1.touch()
    p2.touch()
    p3.touch()
    result = find_indexable_files(tmp_path)
    assert sorted(result) == result
    assert result == [p2, p3, p1]
