import dataclasses
import logging
from pathlib import Path

import pytest
from pdf_factories import make_encrypted_pdf, make_image_only_pdf, make_simple_pdf

from ebless.format.pdf import Chunk, extract_chunks

_LOGGER_NAME = "ebless.format.pdf"
_FAILURE_MSG = "could not extract chunks"

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "pdf"
_REAL_FIXTURES = sorted(_FIXTURE_DIR.glob("*.pdf"))


def test_module_imports():
    assert Chunk is not None
    assert callable(extract_chunks)


def test_chunk_is_frozen_dataclass():
    chunk = Chunk(text="x", source_book=Path("/a"), page_number=1, ordinal=0)
    assert chunk.text == "x"
    assert chunk.source_book == Path("/a")
    assert chunk.page_number == 1
    assert chunk.ordinal == 0
    with pytest.raises(dataclasses.FrozenInstanceError):
        chunk.text = "y"  # ty: ignore[invalid-assignment]


def test_three_pages_two_chunks_each_yields_six_chunks(tmp_path):
    pdf = tmp_path / "x.pdf"
    make_simple_pdf(pdf, [["p1c1", "p1c2"], ["p2c1", "p2c2"], ["p3c1", "p3c2"]])

    chunks = extract_chunks(pdf)

    assert len(chunks) == 6
    assert [c.page_number for c in chunks] == [1, 1, 2, 2, 3, 3]
    assert [c.ordinal for c in chunks] == [0, 1, 2, 3, 4, 5]
    for marker in ("p1c1", "p1c2", "p2c1", "p2c2", "p3c1", "p3c2"):
        assert any(marker in c.text for c in chunks)


def test_single_page_single_chunk(tmp_path):
    pdf = tmp_path / "y.pdf"
    make_simple_pdf(pdf, [["only one"]])

    chunks = extract_chunks(pdf)

    assert len(chunks) == 1
    assert chunks[0].page_number == 1
    assert chunks[0].ordinal == 0
    assert "only one" in chunks[0].text


def test_whitespace_around_chunks_is_stripped(tmp_path):
    pdf = tmp_path / "w.pdf"
    make_simple_pdf(pdf, [["  surrounded   "]])

    chunks = extract_chunks(pdf)

    assert len(chunks) == 1
    text = chunks[0].text
    assert text == text.strip()
    assert "surrounded" in text


def test_source_book_is_resolved_absolute(tmp_path):
    pdf = tmp_path / "x.pdf"
    make_simple_pdf(pdf, [["a", "b"], ["c"]])

    chunks = extract_chunks(pdf)

    expected = pdf.resolve()
    assert all(c.source_book == expected for c in chunks)


def test_encrypted_pdf_returns_empty_with_warning(tmp_path, caplog):
    pdf = tmp_path / "e.pdf"
    make_encrypted_pdf(pdf, [["secret"]])

    with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
        result = extract_chunks(pdf)

    assert result == []
    records = [r for r in caplog.records if r.name == _LOGGER_NAME]
    assert len(records) == 1
    assert records[0].msg == _FAILURE_MSG
    assert getattr(records[0], "reason", None) == "encrypted"
    assert getattr(records[0], "path", None) == str(pdf.resolve())


def test_image_only_pdf_returns_empty_silently(tmp_path, caplog):
    pdf = tmp_path / "img.pdf"
    make_image_only_pdf(pdf)

    with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
        result = extract_chunks(pdf)

    assert result == []
    records = [r for r in caplog.records if r.name == _LOGGER_NAME]
    assert records == []


def test_non_pdf_bytes_returns_empty_with_warning(tmp_path, caplog):
    pdf = tmp_path / "fake.pdf"
    pdf.write_bytes(b"this is not a pdf")

    with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
        result = extract_chunks(pdf)

    assert result == []
    records = [r for r in caplog.records if r.name == _LOGGER_NAME]
    assert len(records) == 1
    assert records[0].msg == _FAILURE_MSG
    reason = getattr(records[0], "reason", None)
    assert isinstance(reason, str) and reason


def test_missing_file_returns_empty_with_missing_reason(tmp_path, caplog):
    pdf = tmp_path / "nope.pdf"

    with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
        result = extract_chunks(pdf)

    assert result == []
    records = [r for r in caplog.records if r.name == _LOGGER_NAME]
    assert len(records) == 1
    assert records[0].msg == _FAILURE_MSG
    assert getattr(records[0], "reason", None) == "missing"


@pytest.mark.parametrize("fixture", _REAL_FIXTURES, ids=lambda p: p.name)
def test_real_fixture_extracts_sane_chunks(fixture):
    chunks = extract_chunks(fixture)

    assert len(chunks) > 0
    assert all(c.text and c.text == c.text.strip() for c in chunks)
    assert all(c.page_number >= 1 for c in chunks)
    assert [c.ordinal for c in chunks] == list(range(len(chunks)))
