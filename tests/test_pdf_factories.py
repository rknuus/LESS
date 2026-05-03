from pdf_factories import make_encrypted_pdf, make_image_only_pdf, make_simple_pdf
from pypdf import PdfReader


def test_make_simple_pdf_produces_readable_file(tmp_path):
    out = tmp_path / "simple.pdf"
    make_simple_pdf(out, [["p1c1", "p1c2"], ["p2c1"]])
    assert out.exists()
    assert out.stat().st_size > 0


def test_make_encrypted_pdf_is_actually_encrypted(tmp_path):
    out = tmp_path / "encrypted.pdf"
    make_encrypted_pdf(out, [["secret chunk"]])
    reader = PdfReader(str(out))
    assert reader.is_encrypted is True


def test_make_image_only_pdf_yields_no_text(tmp_path):
    out = tmp_path / "image_only.pdf"
    make_image_only_pdf(out)
    reader = PdfReader(str(out))
    assert reader.pages[0].extract_text().strip() == ""
