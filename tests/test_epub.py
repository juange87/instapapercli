# tests/test_epub.py
from pathlib import Path


def test_create_epub(tmp_path):
    """Should create a valid EPUB file from HTML and title."""
    from instapaper.epub import create_epub

    html = "<h1>Test</h1><p>Hello world paragraph.</p>"
    output = tmp_path / "test.epub"
    create_epub(title="Test Article", html=html, output_path=output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_create_epub_sanitizes_filename(tmp_path):
    """Should handle special characters in title for filename."""
    from instapaper.epub import sanitize_filename

    assert sanitize_filename("Hello / World: Test?") == "Hello_World_Test"


def test_create_epub_from_bookmark(tmp_path):
    """Should create EPUB from a bookmark dict and HTML."""
    from instapaper.epub import create_epub_from_bookmark

    bookmark = {
        "bookmark_id": 1001,
        "title": "My Great Article",
        "url": "https://example.com/article",
    }
    html = "<p>Some article content</p>"
    path = create_epub_from_bookmark(bookmark, html, output_dir=tmp_path)
    assert path.exists()
    assert "My_Great_Article" in path.name
    assert path.suffix == ".epub"
