from click.testing import CliRunner

from ebless.cli import cli
from ebless.indexer import index_books


def test_index_happy_path(tmp_path):
    result = CliRunner().invoke(cli, ["index", str(tmp_path)])
    assert result.exit_code == 0
    assert f"would index {tmp_path}" in result.output


def test_index_missing_path(tmp_path):
    missing = tmp_path / "does-not-exist"
    result = CliRunner().invoke(cli, ["index", str(missing)])
    assert result.exit_code != 0


def test_help_lists_index():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "index" in result.output


def test_index_books_stub_contract(tmp_path, capsys):
    index_books(tmp_path)
    captured = capsys.readouterr()
    assert captured.out == f"would index {tmp_path}\n"
