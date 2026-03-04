"""Tests for CLI commands."""

import json
from unittest.mock import patch

from click.testing import CliRunner


def test_login_success(tmp_path, monkeypatch):
    """Login command should save tokens on success."""
    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"

    with patch("instapaper.cli.InstapaperAPI") as MockAPI:
        mock_api = MockAPI.return_value
        mock_api.login.return_value = ("tok123", "sec456")
        with patch("instapaper.cli.TOKEN_FILE", token_file):
            runner = CliRunner()
            result = runner.invoke(cli, ["login"], input="user@test.com\npassword\n")

    assert result.exit_code == 0
    assert "Logged in successfully" in result.output
    assert token_file.exists()


def test_login_missing_credentials(monkeypatch):
    """Login should fail if consumer credentials are missing."""
    from instapaper.cli import cli

    monkeypatch.delenv("INSTAPAPER_CONSUMER_KEY", raising=False)
    monkeypatch.delenv("INSTAPAPER_CONSUMER_SECRET", raising=False)

    runner = CliRunner()
    result = runner.invoke(cli, ["login"], input="user@test.com\npassword\n")
    assert result.exit_code != 0


def test_add_bookmark(monkeypatch, tmp_path):
    """Add command should add a URL and show confirmation."""
    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"
    token_file.write_text(json.dumps({
        "oauth_token": "tok", "oauth_token_secret": "sec"
    }))

    with patch("instapaper.cli.TOKEN_FILE", token_file), \
         patch("instapaper.cli.InstapaperAPI") as MockAPI:
        mock_api = MockAPI.return_value
        mock_api.add_bookmark.return_value = {
            "type": "bookmark",
            "bookmark_id": 3003,
            "title": "Example Article",
            "url": "https://example.com",
        }
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "https://example.com"])

    assert result.exit_code == 0
    assert "Added" in result.output


def test_list_bookmarks(monkeypatch, tmp_path):
    """List command should display bookmarks."""
    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"
    token_file.write_text(json.dumps({
        "oauth_token": "tok", "oauth_token_secret": "sec"
    }))

    with patch("instapaper.cli.TOKEN_FILE", token_file), \
         patch("instapaper.cli.InstapaperAPI") as MockAPI:
        mock_api = MockAPI.return_value
        mock_api.list_bookmarks.return_value = [
            {
                "type": "bookmark",
                "bookmark_id": 1001,
                "title": "Article One",
                "url": "https://example.com/1",
                "progress": 0.5,
            },
        ]
        runner = CliRunner()
        result = runner.invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "Article One" in result.output


def test_add_markdown_file(monkeypatch, tmp_path):
    """Add command should detect .md file, convert to HTML, and upload with content."""
    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"
    token_file.write_text(json.dumps({
        "oauth_token": "tok", "oauth_token_secret": "sec"
    }))
    md_file = tmp_path / "notes.md"
    md_file.write_text("# My Notes\n\nSome content here.")

    with patch("instapaper.cli.TOKEN_FILE", token_file), \
         patch("instapaper.cli.InstapaperAPI") as MockAPI:
        mock_api = MockAPI.return_value
        mock_api.add_bookmark.return_value = {
            "type": "bookmark",
            "bookmark_id": 5005,
            "title": "notes.md",
        }
        runner = CliRunner()
        result = runner.invoke(cli, ["add", str(md_file)])

    assert result.exit_code == 0
    assert "Added" in result.output
    mock_api.add_bookmark.assert_called_once()
    call_kwargs = mock_api.add_bookmark.call_args
    assert call_kwargs.kwargs.get("content") is not None
    assert "<h1>" in call_kwargs.kwargs["content"]
    assert call_kwargs.kwargs.get("is_private_from_source") is True


def test_add_pdf_file(monkeypatch, tmp_path):
    """Add command should detect .pdf file, convert to HTML, and upload with content."""
    import pymupdf

    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"
    token_file.write_text(json.dumps({
        "oauth_token": "tok", "oauth_token_secret": "sec"
    }))
    pdf_file = tmp_path / "report.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "PDF report content")
    doc.save(str(pdf_file))
    doc.close()

    with patch("instapaper.cli.TOKEN_FILE", token_file), \
         patch("instapaper.cli.InstapaperAPI") as MockAPI:
        mock_api = MockAPI.return_value
        mock_api.add_bookmark.return_value = {
            "type": "bookmark",
            "bookmark_id": 6006,
            "title": "report.pdf",
        }
        runner = CliRunner()
        result = runner.invoke(cli, ["add", str(pdf_file)])

    assert result.exit_code == 0
    assert "Added" in result.output
    call_kwargs = mock_api.add_bookmark.call_args
    assert call_kwargs.kwargs.get("content") is not None
    assert "PDF report content" in call_kwargs.kwargs["content"]
    assert call_kwargs.kwargs.get("is_private_from_source") is True


def test_add_url_unchanged(monkeypatch, tmp_path):
    """Add command with a URL should still work as before (no content param)."""
    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"
    token_file.write_text(json.dumps({
        "oauth_token": "tok", "oauth_token_secret": "sec"
    }))

    with patch("instapaper.cli.TOKEN_FILE", token_file), \
         patch("instapaper.cli.InstapaperAPI") as MockAPI:
        mock_api = MockAPI.return_value
        mock_api.add_bookmark.return_value = {
            "type": "bookmark",
            "bookmark_id": 3003,
            "title": "Example",
            "url": "https://example.com",
        }
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "https://example.com"])

    assert result.exit_code == 0
    call_kwargs = mock_api.add_bookmark.call_args
    assert call_kwargs.kwargs.get("content") is None
    assert call_kwargs.kwargs.get("is_private_from_source") is False


def test_add_missing_file(monkeypatch, tmp_path):
    """Add command should fail gracefully for a non-existent file."""
    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"
    token_file.write_text(json.dumps({
        "oauth_token": "tok", "oauth_token_secret": "sec"
    }))

    with patch("instapaper.cli.TOKEN_FILE", token_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["add", "/nonexistent/file.md"])

    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "not found" in (result.output + str(result.exception)).lower()


def test_export_single(monkeypatch, tmp_path):
    """Export command should create an EPUB file."""
    from instapaper.cli import cli

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "ck")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "cs")
    token_file = tmp_path / "tokens.json"
    token_file.write_text(json.dumps({
        "oauth_token": "tok", "oauth_token_secret": "sec"
    }))

    with patch("instapaper.cli.TOKEN_FILE", token_file), \
         patch("instapaper.cli.InstapaperAPI") as MockAPI:
        mock_api = MockAPI.return_value
        mock_api.list_bookmarks.return_value = [
            {
                "type": "bookmark",
                "bookmark_id": 1001,
                "title": "Test Export",
                "url": "https://example.com/test",
            }
        ]
        mock_api.get_text.return_value = "<p>Article content</p>"
        runner = CliRunner()
        result = runner.invoke(
            cli, ["export", "1001", "--output-dir", str(tmp_path)]
        )

    assert result.exit_code == 0
    assert "Exported" in result.output
    epub_files = list(tmp_path.glob("*.epub"))
    assert len(epub_files) == 1
