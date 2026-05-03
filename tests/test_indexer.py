import logging
import os

from ebless import inventory
from ebless.indexer import index_books


def _write_pdf(path, content=b"hello"):
    path.write_bytes(content)
    return path


def test_first_run_prints_all_found_files(tmp_path, capsys):
    library = tmp_path / "library"
    library.mkdir()
    a = _write_pdf(library / "a.pdf", b"aaa")
    b = _write_pdf(library / "b.pdf", b"bbb")

    index_books(library)

    out_lines = capsys.readouterr().out.splitlines()
    expected = sorted([str(library.resolve() / "a.pdf"), str(library.resolve() / "b.pdf")])
    assert out_lines == expected
    saved = inventory.load(library.resolve(), path=inventory.INVENTORY_PATH)
    assert set(saved.keys()) == {"a.pdf", "b.pdf"}
    assert saved["a.pdf"]["size"] == a.stat().st_size
    assert saved["b.pdf"]["size"] == b.stat().st_size


def test_second_run_prints_nothing_when_unchanged(tmp_path, capsys):
    library = tmp_path / "library"
    library.mkdir()
    _write_pdf(library / "book.pdf", b"data")

    index_books(library)
    capsys.readouterr()

    index_books(library)
    assert capsys.readouterr().out == ""


def test_modified_file_is_printed_on_rerun(tmp_path, capsys):
    library = tmp_path / "library"
    library.mkdir()
    stable = _write_pdf(library / "stable.pdf", b"stable")
    bumped = _write_pdf(library / "bumped.pdf", b"original")

    index_books(library)
    capsys.readouterr()

    future = bumped.stat().st_mtime + 5
    os.utime(bumped, (future, future))

    index_books(library)

    out_lines = capsys.readouterr().out.splitlines()
    assert out_lines == [str(library.resolve() / "bumped.pdf")]
    assert stable.exists()


def test_removed_file_is_logged_at_debug_and_pruned(tmp_path, capsys, caplog):
    library = tmp_path / "library"
    library.mkdir()
    keeper = _write_pdf(library / "keeper.pdf", b"keep")
    gone = _write_pdf(library / "gone.pdf", b"gone")

    index_books(library)
    capsys.readouterr()

    gone.unlink()

    caplog.set_level(logging.DEBUG, logger="ebless.indexer")
    index_books(library)

    debug_records = [
        r
        for r in caplog.records
        if r.levelname == "DEBUG"
        and r.msg == "file removed from library"
        and getattr(r, "path", None) == "gone.pdf"
    ]
    assert len(debug_records) == 1

    saved = inventory.load(library.resolve(), path=inventory.INVENTORY_PATH)
    assert "gone.pdf" not in saved
    assert "keeper.pdf" in saved
    assert keeper.exists()


def test_summary_info_record_carries_counts(tmp_path, capsys, caplog):
    library = tmp_path / "library"
    library.mkdir()
    stable = _write_pdf(library / "stable.pdf", b"stable")
    bumped = _write_pdf(library / "bumped.pdf", b"bumped")
    gone = _write_pdf(library / "gone.pdf", b"gone")

    index_books(library)
    capsys.readouterr()

    future = bumped.stat().st_mtime + 5
    os.utime(bumped, (future, future))
    gone.unlink()
    _write_pdf(library / "fresh.pdf", b"fresh")

    caplog.set_level(logging.DEBUG, logger="ebless.indexer")
    index_books(library)

    summaries = [r for r in caplog.records if r.levelname == "INFO" and r.msg == "indexed library"]
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.added == 1
    assert summary.modified == 1
    assert summary.removed == 1
    assert summary.unchanged == 1
    assert summary.library == str(library.resolve())
    assert stable.exists()
