from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_file(filename: str, content: bytes) -> str:
    ext=Path(filename).suffix.lower()
    if ext in {'.txt','.md'}:
        return content.decode('utf-8', errors='ignore')
    if ext=='.pdf':
        import io
        reader=PdfReader(io.BytesIO(content))
        return '\n'.join((p.extract_text() or '') for p in reader.pages)
    if ext=='.docx':
        import io
        doc=Document(io.BytesIO(content))
        return '\n'.join(p.text for p in doc.paragraphs)
    raise ValueError(f'Unsupported file type: {ext}. Use PDF, DOCX, TXT or paste text.')
