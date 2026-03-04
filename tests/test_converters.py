"""Tests for file converters (Markdown → HTML, PDF → HTML)."""

from pathlib import Path

import pymupdf
import pytest

from instapaper.converters import markdown_to_html, pdf_to_html


def test_markdown_to_html_basic():
    """Markdown with heading and paragraph should produce valid HTML."""
    md = "# Hello\n\nThis is a **test**."
    html = markdown_to_html(md)
    assert "<h1>Hello</h1>" in html
    assert "<strong>test</strong>" in html


def test_markdown_to_html_from_file(tmp_path):
    """markdown_to_html should accept a file path and read it."""
    md_file = tmp_path / "notes.md"
    md_file.write_text("- item one\n- item two\n")
    html = markdown_to_html(md_file)
    assert "<li>item one</li>" in html
    assert "<li>item two</li>" in html


def test_pdf_to_html(tmp_path):
    """pdf_to_html should extract text and wrap in <p> tags."""
    pdf_path = tmp_path / "test.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello from PDF")
    doc.save(str(pdf_path))
    doc.close()

    html = pdf_to_html(pdf_path)
    assert "<p>" in html
    assert "Hello from PDF" in html


def test_pdf_to_html_missing_file():
    """pdf_to_html should raise FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        pdf_to_html(Path("/nonexistent/file.pdf"))
