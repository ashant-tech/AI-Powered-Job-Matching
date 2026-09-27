import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.cv_processing import pdf_parser


def test_parse_pdf_missing_file_is_graceful():
    # A missing/unreadable file must return '' rather than raise.
    assert pdf_parser.parse_pdf("does/not/exist.pdf") == ""


def test_parse_pdf_bytes_invalid_is_graceful():
    assert pdf_parser.parse_pdf_bytes(b"not a real pdf") == ""


def test_ocr_disabled_does_not_crash(monkeypatch):
    # With OCR disabled, extraction falls back to the text layer (empty here)
    # and still returns a string instead of raising.
    from app.config.settings import settings
    monkeypatch.setattr(settings, "OCR_ENABLED", False)
    assert isinstance(pdf_parser.parse_pdf("does/not/exist.pdf"), str)
