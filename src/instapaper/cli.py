"""CLI commands for Instapaper."""

import click

from instapaper.api import InstapaperAPI
from instapaper.config import (
    TOKEN_FILE,
    get_consumer_credentials,
    load_tokens,
    save_tokens,
)


def get_api() -> InstapaperAPI:
    """Create an authenticated API client from stored tokens."""
    key, secret = get_consumer_credentials()
    tokens = load_tokens()
    if not tokens:
        click.echo("Not logged in. Run 'instapaper login' first.", err=True)
        raise SystemExit(1)
    return InstapaperAPI(
        consumer_key=key,
        consumer_secret=secret,
        oauth_token=tokens["oauth_token"],
        oauth_token_secret=tokens["oauth_token_secret"],
    )


@click.group()
def cli():
    """Instapaper CLI — manage your reading list from the terminal."""
    pass


@cli.command()
def login():
    """Authenticate with Instapaper using username and password."""
    key, secret = get_consumer_credentials()
    username = click.prompt("Email or username")
    password = click.prompt("Password", hide_input=True)

    api = InstapaperAPI(consumer_key=key, consumer_secret=secret)
    try:
        token, token_secret = api.login(username, password)
    except Exception as e:
        click.echo(f"Login failed: {e}", err=True)
        raise SystemExit(1)

    save_tokens(token, token_secret, path=TOKEN_FILE)
    click.echo("Logged in successfully.")
