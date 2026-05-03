from click.testing import CliRunner

from ebless.cli import cli
from ebless.indexer import index_books


def test_index_happy_path_empty(tmp_path):
    result = CliRunner().invoke(cli, ["index", str(tmp_path)])
    assert result.exit_code == 0
    assert result.stdout == ""


def test_index_prints_resolved_pdf_path(tmp_path):
    pdf = tmp_path / "fixture.pdf"
    pdf.touch()
    result = CliRunner().invoke(cli, ["index", str(tmp_path)])
    assert result.exit_code == 0
    expected = tmp_path.resolve() / "fixture.pdf"
    assert result.stdout == f"{expected}\n"


def test_index_lists_all_pdfs_sorted(tmp_path):
    top = tmp_path / "top.pdf"
    sub = tmp_path / "sub"
    sub.mkdir()
    nested = sub / "nested.pdf"
    hidden = tmp_path / ".hidden.pdf"
    non_pdf = tmp_path / "notes.txt"
    top.touch()
    nested.touch()
    hidden.touch()
    non_pdf.touch()

    result = CliRunner().invoke(cli, ["index", str(tmp_path)])
    assert result.exit_code == 0

    resolved_root = tmp_path.resolve()
    expected = sorted(
        [
            resolved_root / ".hidden.pdf",
            resolved_root / "top.pdf",
            resolved_root / "sub" / "nested.pdf",
        ]
    )
    expected_output = "".join(f"{p}\n" for p in expected)
    assert result.stdout == expected_output


def test_index_missing_path(tmp_path):
    missing = tmp_path / "does-not-exist"
    result = CliRunner().invoke(cli, ["index", str(missing)])
    assert result.exit_code != 0


def test_help_lists_index():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "index" in result.output


def test_index_books_orchestrates_discovery_and_inventory(tmp_path, capsys):
    library = tmp_path / "library"
    library.mkdir()
    pdf = library / "fresh.pdf"
    pdf.write_bytes(b"data")

    index_books(library)

    out = capsys.readouterr().out
    assert out == f"{(library.resolve() / 'fresh.pdf')}\n"
