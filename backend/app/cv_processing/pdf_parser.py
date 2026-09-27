"""PDF text extraction with OCR fallback for scanned/image-only PDFs.

Strategy per page:
  1. Try the embedded text layer (PyMuPDF/fitz, falling back to PyPDF2).
  2. If a page yields (almost) no text, render it to an image and OCR it with
     Tesseract — this is what makes scanned CVs readable.

OCR is best-effort: if PyMuPDF or Tesseract aren't installed, extraction
degrades to whatever text layer exists rather than raising.
"""
import io
import logging

from app.config.settings import settings

logger = logging.getLogger("cv-processing")

# A page with fewer than this many non-space characters is treated as "no text
# layer" and sent to OCR (scanned pages usually extract 0).
_MIN_TEXT_CHARS = 20


def _fitz_open(file_path: str):
    try:
        import pymupdf
    except ImportError:
        return None
    try:
        return pymupdf.open(file_path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("PyMuPDF could not open %s: %s", file_path, exc)
        return None


def _text_layer_pages(file_path: str) -> list[str]:
    """Per-page text using fitz if available, else PyPDF2."""
    doc = _fitz_open(file_path)
    if doc is not None:
        try:
            return [page.get_text() or "" for page in doc]
        finally:
            doc.close()

    try:
        import PyPDF2
        with open(file_path, "rb") as handle:
            reader = PyPDF2.PdfReader(handle)
            return [(page.extract_text() or "") for page in reader.pages]
    except ImportError:
        logger.warning("Neither PyMuPDF nor PyPDF2 is installed; cannot read PDF text")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Error reading PDF text layer from %s: %s", file_path, exc)
    return []


def _configure_tesseract():
    if not settings.OCR_ENABLED:
        return None
    try:
        import pytesseract
    except ImportError:
        logger.warning("pytesseract not installed; OCR disabled")
        return None

    cmd = settings.TESSERACT_CMD
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd

    # Fail fast with a clear message if the Tesseract binary isn't reachable.
    try:
        pytesseract.get_tesseract_version()
    except Exception:  # noqa: BLE001
        logger.warning(
            "Tesseract binary not found. Install Tesseract-OCR and set "
            "TESSERACT_CMD (e.g. C:\\Program Files\\Tesseract-OCR\\tesseract.exe). "
            "Scanned PDFs will not be readable until then."
        )
        return None
    return pytesseract


def _ocr_pages(file_path: str, page_indices: list[int]) -> dict[int, str]:
    """Render the given pages to images and OCR them. Returns {index: text}."""
    if not page_indices:
        return {}
    pytesseract = _configure_tesseract()
    if pytesseract is None:
        return {}

    doc = _fitz_open(file_path)
    if doc is None:
        logger.warning("PyMuPDF unavailable; cannot render pages for OCR")
        return {}

    results: dict[int, str] = {}
    try:
        import pymupdf
        from PIL import Image
        dpi = getattr(settings, "OCR_DPI", 300)
        zoom = dpi / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)
        for index in page_indices:
            try:
                page = doc[index]
                pix = page.get_pixmap(matrix=matrix)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                results[index] = pytesseract.image_to_string(image) or ""
            except Exception as exc:  # noqa: BLE001
                logger.warning("OCR failed on page %s of %s: %s", index, file_path, exc)
    except ImportError:
        logger.warning("Pillow not installed; cannot OCR rendered pages")
    finally:
        doc.close()
    return results


def _extract(file_path: str) -> str:
    pages = _text_layer_pages(file_path)
    empty = [i for i, text in enumerate(pages) if len((text or "").strip()) < _MIN_TEXT_CHARS]
    if empty:
        ocr = _ocr_pages(file_path, empty)
        for index, text in ocr.items():
            if text and text.strip():
                merged = (pages[index].strip() + "\n" + text).strip() if index < len(pages) else text.strip()
                if index < len(pages):
                    pages[index] = merged
                else:
                    pages.append(merged)
    return "\n".join(pages).strip()


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF, OCR-ing scanned pages. Returns '' on failure."""
    try:
        return _extract(file_path)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error parsing PDF %s: %s", file_path, exc)
        return ""


def parse_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes (writes to a temp file for fitz/OCR)."""
    import os
    import tempfile

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        return parse_pdf(tmp_path)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error parsing PDF bytes: %s", exc)
        return ""
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
