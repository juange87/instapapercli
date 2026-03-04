# Instapaper CLI Design

## Purpose

A focused Python CLI for Instapaper that enables:
- Adding articles to Instapaper from the terminal
- Listing saved bookmarks
- Exporting articles as EPUB files for Kobo e-readers

## Commands

```
instapaper login              # Authenticate with username/password → OAuth tokens
instapaper add <url>          # Add article to Instapaper
instapaper list               # List bookmarks (--folder, --limit)
instapaper export <id>        # Export article as EPUB
instapaper export --all       # Export all unread articles as EPUBs
```

## Architecture

Approach: monolithic simple — a single Python package with 4 modules.

```
instapapercli/
├── pyproject.toml
├── src/
│   └── instapaper/
│       ├── __init__.py
│       ├── cli.py          # Click commands
│       ├── api.py          # OAuth 1.0a client + API endpoints
│       ├── epub.py         # HTML → EPUB conversion
│       └── config.py       # Env vars + token storage
├── tests/
└── README.md
```

## Authentication

OAuth 1.0a with xAuth:
1. Consumer key/secret via `INSTAPAPER_CONSUMER_KEY` and `INSTAPAPER_CONSUMER_SECRET` env vars
2. `instapaper login` exchanges username/password for OAuth access tokens
3. Tokens stored in `~/.config/instapaper/tokens.json`
4. Subsequent commands use stored tokens automatically

## Dependencies

- **click** — CLI framework
- **requests** + **requests-oauthlib** — HTTP + OAuth 1.0a
- **ebooklib** — EPUB generation
- **beautifulsoup4** — HTML cleanup for EPUB
- **rich** (optional) — Pretty terminal tables

## Data Flow: Export EPUB

```
instapaper export <id>
  → API get_text → processed HTML
  → beautifulsoup4 cleanup
  → ebooklib generates EPUB
  → file saved to disk
```

## Data Flow: Add Article → Kobo

```
instapaper add <url>
  → API bookmarks/add → stored in Instapaper
  → Kobo syncs automatically via WiFi (native integration)
```

## Error Handling

- No tokens → "Run `instapaper login` first"
- No consumer keys → "Set INSTAPAPER_CONSUMER_KEY and INSTAPAPER_CONSUMER_SECRET"
- Rate limit (1040) → "Too many requests, wait a moment"
- Article not found → "Article with ID X not found"

## Credential Management

- Consumer key/secret: environment variables
- Access tokens: `~/.config/instapaper/tokens.json`
