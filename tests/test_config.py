import json
import os
from pathlib import Path

import pytest


def test_get_consumer_credentials_from_env(monkeypatch):
    """Consumer key/secret should come from environment variables."""
    from instapaper.config import get_consumer_credentials

    monkeypatch.setenv("INSTAPAPER_CONSUMER_KEY", "test_key")
    monkeypatch.setenv("INSTAPAPER_CONSUMER_SECRET", "test_secret")
    key, secret = get_consumer_credentials()
    assert key == "test_key"
    assert secret == "test_secret"


def test_get_consumer_credentials_missing_raises(monkeypatch):
    """Should raise if consumer credentials are not set."""
    from instapaper.config import get_consumer_credentials

    monkeypatch.delenv("INSTAPAPER_CONSUMER_KEY", raising=False)
    monkeypatch.delenv("INSTAPAPER_CONSUMER_SECRET", raising=False)
    with pytest.raises(SystemExit):
        get_consumer_credentials()


def test_save_and_load_tokens(tmp_path):
    """Tokens should be saved to and loaded from JSON file."""
    from instapaper.config import load_tokens, save_tokens

    token_file = tmp_path / "tokens.json"
    save_tokens("oauth_token", "oauth_secret", token_file)
    tokens = load_tokens(token_file)
    assert tokens["oauth_token"] == "oauth_token"
    assert tokens["oauth_token_secret"] == "oauth_secret"


def test_load_tokens_missing_file(tmp_path):
    """Should return None when token file doesn't exist."""
    from instapaper.config import load_tokens

    token_file = tmp_path / "nonexistent.json"
    assert load_tokens(token_file) is None
