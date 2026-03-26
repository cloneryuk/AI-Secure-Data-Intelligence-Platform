import io
import logging 
logger=logging.getLogger("ai_platform")
def extract_text(raw_bytes: bytes, extension: str) -> str:
    ext = extension.lower()
    if ext in ("txt", "log", ""):
        return raw_bytes.decode("utf-8", errors="replace")
    if ext=="pdf":
        return _extract_pdf(raw_bytes)
    if ext in ("docx","doc"):
        return _extract_docx(raw_bytes)

    logger.warning("Unknown extension '%s', treating as plain text",ext)
    return raw_bytes.decode("utf-8",errors="replace")

def _extract_pdf(raw_bytes: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(raw_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages)
    except Exception as e:
        logger.error("PDF extraction failed: %s", e)
        return "[Error: Could not extract PDF]"
def _extract_docx(raw_bytes: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(raw_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error("DOCX extraction failed: %s", e)
        return "[Error: Could not extract DOCX]"
        

