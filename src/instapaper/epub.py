"""EPUB generation from Instapaper article HTML."""

import re
from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import epub


def sanitize_filename(title: str) -> str:
    """Remove special characters from title for use as filename."""
    cleaned = re.sub(r'[^\w\s-]', '', title)
    return re.sub(r'[\s]+', '_', cleaned).strip('_')


def create_epub(title: str, html: str, output_path: Path, url: str = "") -> Path:
    """Create an EPUB file from HTML content."""
    book = epub.EpubBook()
    book.set_identifier(f"instapaper-{hash(title)}")
    book.set_title(title)
    book.set_language("en")

    # Clean HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    clean_html = str(soup)

    chapter = epub.EpubHtml(title=title, file_name="article.xhtml", lang="en")
    chapter.content = f"<h1>{title}</h1>{clean_html}"

    book.add_item(chapter)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", chapter]
    book.toc = [epub.Link("article.xhtml", title, "article")]

    epub.write_epub(str(output_path), book)
    return output_path


def create_epub_from_bookmark(
    bookmark: dict, html: str, output_dir: Path = Path(".")
) -> Path:
    """Create an EPUB from a bookmark dict and its HTML text."""
    title = bookmark.get("title", f"bookmark-{bookmark['bookmark_id']}")
    filename = f"{sanitize_filename(title)}.epub"
    output_path = output_dir / filename
    return create_epub(
        title=title,
        html=html,
        output_path=output_path,
        url=bookmark.get("url", ""),
    )
