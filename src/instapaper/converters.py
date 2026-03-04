"""Convert local files (Markdown, PDF) to HTML for Instapaper upload."""

from pathlib import Path

import markdown
import pymupdf


def markdown_to_html(source: str | Path) -> str:
    """Convert Markdown to HTML. Accepts a string or a file path."""
    if isinstance(source, Path):
        source = source.read_text()
    return markdown.markdown(source)


def pdf_to_html(path: Path) -> str:
    """Extract text from a PDF and return simple HTML with <p> tags per page."""
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    doc = pymupdf.open(str(path))
    paragraphs = []
    for page in doc:
        text = page.get_text("text").strip()
        if text:
            paragraphs.append(f"<p>{text}</p>")
    doc.close()
    return "\n".join(paragraphs)
