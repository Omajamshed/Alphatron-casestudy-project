from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings


def parse_pdf(file_path: Path) -> List[Dict[str, Any]]:
    pages_data = []
    # Try pypdf first
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_data.append({"page": idx + 1, "text": text})
    except Exception:
        # Fallback to pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(str(file_path)) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    pages_data.append({"page": idx + 1, "text": text})
        except Exception as e:
            raise ValueError(f"Failed to parse PDF file: {e}")
    return pages_data


def parse_docx(file_path: Path) -> List[Dict[str, Any]]:
    try:
        import docx
        doc = docx.Document(str(file_path))
        full_text = []
        for p in doc.paragraphs:
            if p.text.strip():
                full_text.append(p.text)
        # Combine into one or multiple pages (approx 500 words per page)
        combined = "\n\n".join(full_text)
        return [{"page": 1, "text": combined}]
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX file: {e}")


def parse_text(file_path: Path) -> List[Dict[str, Any]]:
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        return [{"page": 1, "text": text}]
    except Exception as e:
        raise ValueError(f"Failed to read text file: {e}")


def parse_document(file_path: Path) -> List[Dict[str, Any]]:
    """Validates and parses file, returning a list of dicts with page and text."""
    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_MB:
        raise ValueError(f"File size exceeds maximum limit of {settings.MAX_UPLOAD_MB} MB")

    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return parse_docx(file_path)
    elif ext in [".txt", ".md"]:
        return parse_text(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only PDF, DOCX, and TXT are supported.")
