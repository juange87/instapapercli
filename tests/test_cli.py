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
