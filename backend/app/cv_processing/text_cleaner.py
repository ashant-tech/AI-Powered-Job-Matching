import re

from app.cv_processing.docx_parser import extract_text_from_docx
from app.cv_processing.pdf_parser import extract_text_from_pdf

_WHITESPACE = re.compile(r"[ \t]+")
_BLANK_LINES = re.compile(r"\n{3,}")
_NON_PRINTABLE = re.compile(r"[^\x09\x0a\x20-\x7e\u00a0-\uffff]")


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = _NON_PRINTABLE.sub(" ", text)
    text = _WHITESPACE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return _BLANK_LINES.sub("\n\n", text).strip()


def extract_text(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".pdf"):
        raw = extract_text_from_pdf(path)
    elif lower.endswith(".docx"):
        raw = extract_text_from_docx(path)
    else:
        with open(path, encoding="utf-8", errors="ignore") as f:
            raw = f.read()
    return clean_text(raw)
