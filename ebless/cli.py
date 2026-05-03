import pathlib

import click

from ebless.indexer import index_books
from ebless.logconfig import configure


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    show_default=True,
)
@click.option(
    "--log-file",
    type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path),
    default=None,
)
def cli(log_level: str, log_file: pathlib.Path | None) -> None:
    """ebless — eBook LLM Empowered Semantic Search."""
    configure(level=log_level, log_file=log_file)


@cli.command("index")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path),
)
def index_cmd(path: pathlib.Path) -> None:
    """Index every supported eBook under PATH."""
    index_books(path)
