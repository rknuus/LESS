import dataclasses
from pathlib import Path

import pytest


def test_module_imports():
    from ebless.format.pdf import Chunk, extract_chunks

    assert Chunk is not None
    assert callable(extract_chunks)


def test_chunk_is_frozen_dataclass():
    from ebless.format.pdf import Chunk

    chunk = Chunk(text="x", source_book=Path("/a"), page_number=1, ordinal=0)
    assert chunk.text == "x"
    assert chunk.source_book == Path("/a")
    assert chunk.page_number == 1
    assert chunk.ordinal == 0
    with pytest.raises(dataclasses.FrozenInstanceError):
        chunk.text = "y"  # ty: ignore[invalid-assignment]


def test_extract_chunks_returns_empty_list_on_placeholder(tmp_path):
    from ebless.format.pdf import extract_chunks

    result = extract_chunks(tmp_path / "noop.pdf")
    assert result == []
