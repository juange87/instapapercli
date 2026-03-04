"""CLI commands for Instapaper."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from instapaper.api import InstapaperAPI
from instapaper.config import (
    TOKEN_FILE,
    get_consumer_credentials,
    load_tokens,
    save_tokens,
)
from instapaper.epub import create_epub_from_bookmark


def get_api() -> InstapaperAPI:
    """Create an authenticated API client from stored tokens."""
    key, secret = get_consumer_credentials()
    tokens = load_tokens(path=TOKEN_FILE)
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


@cli.command()
@click.argument("url")
@click.option("--title", "-t", default=None, help="Custom title for the bookmark.")
@click.option("--folder", "-f", default=None, help="Folder ID to save to.")
def add(url, title, folder):
    """Add a URL to your Instapaper reading list."""
    api = get_api()
    bookmark = api.add_bookmark(url, title=title, folder_id=folder)
    click.echo(f"Added: {bookmark.get('title', url)} (ID: {bookmark['bookmark_id']})")


@cli.command("list")
@click.option("--limit", "-l", default=25, help="Number of bookmarks to show.")
@click.option("--folder", "-f", default=None, help="Folder ID to filter by.")
def list_bookmarks(limit, folder):
    """List your saved bookmarks."""
    api = get_api()
    bookmarks = api.list_bookmarks(limit=limit, folder_id=folder)
    if not bookmarks:
        click.echo("No bookmarks found.")
        return

    console = Console()
    table = Table(title="Bookmarks")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Progress", style="green", justify="right")

    for b in bookmarks:
        progress = f"{b.get('progress', 0) * 100:.0f}%"
        table.add_row(str(b["bookmark_id"]), b.get("title", "Untitled"), progress)

    console.print(table)


@cli.command()
@click.argument("bookmark_id", required=False, type=int)
@click.option("--all", "export_all", is_flag=True, help="Export all unread bookmarks.")
@click.option(
    "--output-dir", "-o", default=".", type=click.Path(), help="Output directory."
)
def export(bookmark_id, export_all, output_dir):
    """Export bookmark(s) as EPUB files."""
    api = get_api()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if export_all:
        bookmarks = api.list_bookmarks(limit=500)
    elif bookmark_id:
        bookmarks = [b for b in api.list_bookmarks(limit=500) if b["bookmark_id"] == bookmark_id]
        if not bookmarks:
            click.echo(f"Bookmark {bookmark_id} not found.", err=True)
            raise SystemExit(1)
    else:
        click.echo("Provide a bookmark ID or use --all.", err=True)
        raise SystemExit(1)

    for b in bookmarks:
        try:
            html = api.get_text(b["bookmark_id"])
            path = create_epub_from_bookmark(b, html, output_dir=output_path)
            click.echo(f"Exported: {path.name}")
        except Exception as e:
            click.echo(f"Failed to export {b.get('title', b['bookmark_id'])}: {e}", err=True)
