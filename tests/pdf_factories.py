"""Reportlab-based PDF generators for tests of the ebless.format.pdf extractor."""

from pathlib import Path

from pypdf import PdfWriter
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

_LEFT_MARGIN = 72
_TOP_MARGIN = 72
_LINE_HEIGHT = 14
_BLANK_LINES_BETWEEN_CHUNKS = 3


def make_simple_pdf(path: Path, pages: list[list[str]]) -> None:
    width, height = LETTER
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 12)
    for page in pages:
        y = height - _TOP_MARGIN
        for chunk_index, chunk in enumerate(page):
            for line in chunk.splitlines() or [chunk]:
                c.drawString(_LEFT_MARGIN, y, line)
                y -= _LINE_HEIGHT
            if chunk_index < len(page) - 1:
                y -= _LINE_HEIGHT * _BLANK_LINES_BETWEEN_CHUNKS
        c.showPage()
    c.save()


def make_encrypted_pdf(
    path: Path,
    pages: list[list[str]],
    password: str = "test",
) -> None:
    plain_path = path.with_suffix(path.suffix + ".plain")
    try:
        make_simple_pdf(plain_path, pages)
        writer = PdfWriter(clone_from=str(plain_path))
        writer.encrypt(user_password=password, owner_password=password)
        with path.open("wb") as fh:
            writer.write(fh)
    finally:
        if plain_path.exists():
            plain_path.unlink()


def make_image_only_pdf(path: Path) -> None:
    width, height = LETTER
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.rect(_LEFT_MARGIN, height / 2, 200, 100, stroke=1, fill=1)
    c.showPage()
    c.save()
