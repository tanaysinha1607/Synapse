"""Resume parsing stubs for PDF/DOCX/TXT.

Integrate libraries later (pypdf, python-docx, textract). For now, a naive
reader that returns text for .txt and a placeholder for others.
"""

from __future__ import annotations

from pathlib import Path

try:  # optional deps for local demo
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None  # type: ignore

try:
    import docx  # type: ignore
except Exception:  # pragma: no cover
    docx = None  # type: ignore


def extract_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf" and PdfReader is not None:
        try:
            reader = PdfReader(str(path))
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            return "\n".join(parts)
        except Exception:
            pass
    if path.suffix.lower() in {".docx", ".doc"} and docx is not None:
        try:
            doc = docx.Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            pass
    return f"[PARSER NOTICE] Could not parse {path.name}. Try a .txt export."


