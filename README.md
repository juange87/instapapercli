# instapaper-cli

A command-line interface for [Instapaper](https://www.instapaper.com) that lets you manage your reading list and export articles as EPUB files — perfect for sending articles to your Kobo e-reader.

## Features

- **Add articles** — Save any URL to your Instapaper account directly from the terminal
- **Upload local files** — Add Markdown (`.md`) and PDF (`.pdf`) files directly from your filesystem
- **List bookmarks** — Browse your reading list with a formatted table showing titles and reading progress
- **Export to EPUB** — Download articles as EPUB files, ready for your Kobo or any e-reader
- **Kobo integration** — Articles added via the CLI sync automatically to your Kobo over WiFi through Instapaper's native integration

## Installation

### From source

```bash
git clone https://github.com/juange87/instapapercli.git
cd instapapercli
pip install .
```

### For development

```bash
git clone https://github.com/juange87/instapapercli.git
cd instapapercli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Setup

### 1. Get API credentials

Request OAuth consumer tokens from Instapaper:

https://www.instapaper.com/main/request_oauth_consumer_token

### 2. Set environment variables

```bash
export INSTAPAPER_CONSUMER_KEY="your_consumer_key"
export INSTAPAPER_CONSUMER_SECRET="your_consumer_secret"
```

You can add these to your `~/.bashrc`, `~/.zshrc`, or use a tool like [direnv](https://direnv.net/).

### 3. Log in

```bash
instapaper login
```

This prompts for your Instapaper email and password, exchanges them for OAuth tokens via xAuth, and stores the tokens securely at `~/.config/instapaper/tokens.json`. You only need to do this once.

## Usage

### Add an article

```bash
instapaper add https://example.com/interesting-article
```

With a custom title:

```bash
instapaper add https://example.com/article --title "Must read later"
```

Save to a specific folder:

```bash
instapaper add https://example.com/article --folder 12345
```

If you have the Kobo-Instapaper integration enabled, added articles will sync to your Kobo automatically the next time it connects to WiFi.

### Upload a local file

Upload a Markdown file:

```bash
instapaper add ./notes.md
```

Upload a PDF:

```bash
instapaper add report.pdf
```

The CLI auto-detects `.md` and `.pdf` files, converts them to HTML, and uploads the content directly to Instapaper. The filename is used as the title by default (override with `--title`).

### List your bookmarks

```bash
instapaper list
```

Output:

```
          Bookmarks
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID      ┃ Title               ┃ Progress ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 1234567 │ How CSS Grid Works  │      45% │
│ 1234568 │ Rust for Beginners  │       0% │
│ 1234569 │ The Art of Cooking  │     100% │
└─────────┴─────────────────────┴──────────┘
```

Show more results:

```bash
instapaper list --limit 50
```

Filter by folder:

```bash
instapaper list --folder 12345
```

### Export articles as EPUB

Export a single article by its ID (shown in `instapaper list`):

```bash
instapaper export 1234567
```

Export all unread articles:

```bash
instapaper export --all
```

Specify an output directory:

```bash
instapaper export 1234567 --output-dir ~/Books
instapaper export --all --output-dir ~/Books
```

Each article is saved as a separate EPUB file named after its title (e.g., `How_CSS_Grid_Works.epub`).

### Transfer EPUBs to Kobo via USB

After exporting, connect your Kobo via USB and copy the files:

```bash
instapaper export --all --output-dir /Volumes/KOBOeReader/
```

## Command Reference

```
instapaper --help
```

| Command | Description |
|---------|-------------|
| `instapaper login` | Authenticate with Instapaper |
| `instapaper add <url or file>` | Add a URL or local file (.md, .pdf) to your reading list |
| `instapaper list` | List saved bookmarks |
| `instapaper export [ID]` | Export article(s) as EPUB |

### Options

#### `instapaper add`

| Option | Short | Description |
|--------|-------|-------------|
| `--title` | `-t` | Custom title for the bookmark |
| `--folder` | `-f` | Folder ID to save the article to |

#### `instapaper list`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--limit` | `-l` | 25 | Number of bookmarks to show (max 500) |
| `--folder` | `-f` | — | Filter by folder ID |

#### `instapaper export`

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--all` | — | — | Export all unread bookmarks |
| `--output-dir` | `-o` | `.` | Output directory for EPUB files |

## Kobo Workflow

There are two ways to get articles on your Kobo:

### Option A: Automatic sync (recommended)

1. [Link your Instapaper account to your Kobo](https://www.instapaper.com/user) in Instapaper settings
2. Add articles from the terminal:
   ```bash
   instapaper add https://example.com/article
   ```
3. Your Kobo downloads the articles automatically when connected to WiFi

### Option B: Manual EPUB transfer

1. Export articles as EPUB:
   ```bash
   instapaper export --all --output-dir ~/Desktop/kobo-articles
   ```
2. Connect your Kobo via USB
3. Copy the `.epub` files to your Kobo's root directory or a subfolder
4. Eject and disconnect — the articles appear in your library

## Project Structure

```
instapapercli/
├── pyproject.toml              # Package metadata and dependencies
├── src/
│   └── instapaper/
│       ├── __init__.py
│       ├── cli.py              # Click commands (login, add, list, export)
│       ├── api.py              # OAuth 1.0a API client
│       ├── converters.py        # Markdown/PDF → HTML conversion
│       ├── epub.py             # HTML → EPUB conversion
│       └── config.py           # Credential management
└── tests/
    ├── test_api.py             # API client tests (8 tests)
    ├── test_cli.py             # CLI command tests (9 tests)
    ├── test_config.py          # Config module tests (4 tests)
    ├── test_converters.py      # File converter tests (4 tests)
    └── test_epub.py            # EPUB export tests (3 tests)
```

## How It Works

### Authentication

Instapaper uses OAuth 1.0a with [xAuth](https://developer.twitter.com/en/docs/authentication/oauth-1-0a/xauth). Instead of the typical OAuth browser redirect flow, xAuth allows the CLI to exchange your username and password directly for OAuth access tokens. This happens once during `instapaper login`, and the tokens are stored locally for all subsequent requests.

- **Consumer key/secret** — Stored as environment variables (`INSTAPAPER_CONSUMER_KEY`, `INSTAPAPER_CONSUMER_SECRET`)
- **Access tokens** — Stored at `~/.config/instapaper/tokens.json` after login

### API Communication

All Instapaper API calls use HTTPS POST requests with OAuth 1.0a HMAC-SHA1 signatures. The API returns JSON arrays containing typed objects (`bookmark`, `user`, `meta`, `error`). The client filters these to return only the relevant types.

### EPUB Generation

The export pipeline:
1. Fetches the processed HTML text of an article via the Instapaper API
2. Cleans the HTML with BeautifulSoup
3. Wraps it in a valid EPUB structure using ebooklib
4. Saves the file with a sanitized filename based on the article title

## Running Tests

```bash
pytest tests/ -v
```

All 28 tests use mocked HTTP responses (via the `responses` library), so no Instapaper account or network connection is needed to run the test suite.

## Dependencies

| Package | Purpose |
|---------|---------|
| [click](https://click.palletsprojects.com/) | CLI framework with commands, options, and prompts |
| [requests](https://requests.readthedocs.io/) | HTTP client |
| [requests-oauthlib](https://requests-oauthlib.readthedocs.io/) | OAuth 1.0a authentication for requests |
| [ebooklib](https://github.com/aerkalov/ebooklib) | EPUB file generation |
| [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing and cleanup |
| [rich](https://rich.readthedocs.io/) | Formatted terminal tables |
| [markdown](https://python-markdown.github.io/) | Markdown to HTML conversion |
| [pymupdf](https://pymupdf.readthedocs.io/) | PDF text extraction |

## License

MIT
