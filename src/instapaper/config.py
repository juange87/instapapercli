"""Configuration: environment variables and token storage."""

import json
import os
import sys
from pathlib import Path

import click

TOKEN_DIR = Path.home() / ".config" / "instapaper"
TOKEN_FILE = TOKEN_DIR / "tokens.json"

DEFAULT_CONSUMER_KEY = "88d5ce5b8bfd4279b895753f6974cc61"
DEFAULT_CONSUMER_SECRET = "81736445da504585b797d709054c6f21"


def get_consumer_credentials() -> tuple[str, str]:
    """Read OAuth consumer key/secret from env vars, falling back to built-in defaults."""
    key = os.environ.get("INSTAPAPER_CONSUMER_KEY", DEFAULT_CONSUMER_KEY)
    secret = os.environ.get("INSTAPAPER_CONSUMER_SECRET", DEFAULT_CONSUMER_SECRET)
    if key == "YOUR_CONSUMER_KEY_HERE" or secret == "YOUR_CONSUMER_SECRET_HERE":
        click.echo(
            "Error: Set INSTAPAPER_CONSUMER_KEY and INSTAPAPER_CONSUMER_SECRET "
            "environment variables, or update the defaults in config.py.",
            err=True,
        )
        sys.exit(1)
    return key, secret


def save_tokens(
    oauth_token: str, oauth_token_secret: str, path: Path = TOKEN_FILE
) -> None:
    """Save OAuth access tokens to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"oauth_token": oauth_token, "oauth_token_secret": oauth_token_secret}
    path.write_text(json.dumps(data))


def load_tokens(path: Path = TOKEN_FILE) -> dict | None:
    """Load OAuth access tokens from JSON file. Returns None if not found."""
    if not path.exists():
        return None
    return json.loads(path.read_text())
