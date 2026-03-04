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
