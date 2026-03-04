# File Upload Support (PDF + Markdown) — Implementation Plan

## Context

The Instapaper API `bookmarks/add` endpoint supports a `content` parameter (HTML) and `is_private_from_source` for uploading content directly without a URL. We'll use this to let users upload local PDF and Markdown files from the CLI.

## Approach

Auto-detect file vs URL in the `add` command based on file extension (`.md`, `.pdf`). New `converters.py` module with two functions. Backward-compatible API change.

```
instapaper add https://example.com/article   # URL (existing)
instapaper add ./notes.md                     # Markdown file (new)
instapaper add report.pdf                     # PDF file (new)
```

## Changes

| File | Action | What |
|------|--------|------|
| `pyproject.toml` | Modify | Add `markdown>=3.4`, `pymupdf>=1.23` |
| `src/instapaper/converters.py` | **New** | `markdown_to_html()`, `pdf_to_html()` |
| `src/instapaper/api.py` | Modify | `add_bookmark()` gains `content` and `is_private_from_source` params |
| `src/instapaper/cli.py` | Modify | `add` command: auto-detect file, convert, upload with content |
| `tests/test_converters.py` | **New** | 4 tests |
| `tests/test_api.py` | Modify | 1 new test |
| `tests/test_cli.py` | Modify | 4 new tests |

## Execution (TDD)

1. **Dependencies**: Add `markdown`, `pymupdf` to pyproject.toml, reinstall
2. **Converters**: Write tests → implement `converters.py` → commit
3. **API**: Write test for `add_bookmark` with content → extend method → commit
4. **CLI**: Write tests for file upload → modify `add` command → commit
5. **Full suite**: Run all tests, push

## New dependencies

- **`markdown`** — Standard Python-Markdown lib, converts MD→HTML
- **`pymupdf`** — Fast PDF text extraction, `page.get_text("text")` → wrap in `<p>` tags

## Verification

```bash
pytest tests/ -v                          # All tests pass (19 existing + 9 new = 28)
instapaper add ./test.md                  # Should upload markdown content
instapaper add ./test.pdf                 # Should upload PDF content
instapaper add https://example.com        # Existing URL behavior unchanged
```
