import pathlib

import click

from ebless.indexer import index_books


@click.group()
def cli() -> None:
    """ebless — eBook LLM Empowered Semantic Search."""


@cli.command("index")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path),
)
def index_cmd(path: pathlib.Path) -> None:
    """Index every supported eBook under PATH."""
    index_books(path)
