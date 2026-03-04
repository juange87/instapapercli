# tests/test_api.py
import pytest
import responses


@responses.activate
def test_login_returns_tokens():
    """xAuth login should exchange username/password for OAuth tokens."""
    from instapaper.api import InstapaperAPI

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        body="oauth_token=tok123&oauth_token_secret=sec456",
        status=200,
        content_type="application/x-www-form-urlencoded",
    )

    api = InstapaperAPI(consumer_key="ck", consumer_secret="cs")
    token, secret = api.login("user@example.com", "password123")
    assert token == "tok123"
    assert secret == "sec456"


@responses.activate
def test_login_failure_raises():
    """Login should raise on 403."""
    from instapaper.api import InstapaperAPI, InstapaperError

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/oauth/access_token",
        status=403,
    )

    api = InstapaperAPI(consumer_key="ck", consumer_secret="cs")
    with pytest.raises(InstapaperError, match="Login failed"):
        api.login("user@example.com", "wrong")


@responses.activate
def test_verify_credentials():
    """verify_credentials should return user info."""
    from instapaper.api import InstapaperAPI

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/account/verify_credentials",
        json=[{"type": "user", "user_id": 123, "username": "user@example.com"}],
        status=200,
    )

    api = InstapaperAPI(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="tok",
        oauth_token_secret="sec",
    )
    user = api.verify_credentials()
    assert user["user_id"] == 123


@responses.activate
def test_list_bookmarks():
    """list_bookmarks should return bookmark dicts."""
    from instapaper.api import InstapaperAPI

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/list",
        json=[
            {"type": "meta"},
            {
                "type": "bookmark",
                "bookmark_id": 1001,
                "title": "Test Article",
                "url": "https://example.com/article",
                "progress": 0.0,
            },
        ],
        status=200,
    )

    api = InstapaperAPI(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="tok",
        oauth_token_secret="sec",
    )
    bookmarks = api.list_bookmarks(limit=10)
    assert len(bookmarks) == 1
    assert bookmarks[0]["bookmark_id"] == 1001


@responses.activate
def test_add_bookmark():
    """add_bookmark should return the created bookmark."""
    from instapaper.api import InstapaperAPI

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/add",
        json=[
            {"type": "bookmark", "bookmark_id": 2002, "title": "New Article", "url": "https://example.com/new"}
        ],
        status=200,
    )

    api = InstapaperAPI(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="tok",
        oauth_token_secret="sec",
    )
    bookmark = api.add_bookmark("https://example.com/new")
    assert bookmark["bookmark_id"] == 2002


@responses.activate
def test_add_bookmark_with_content():
    """add_bookmark with content should send content and is_private_from_source."""
    from instapaper.api import InstapaperAPI

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/add",
        json=[
            {"type": "bookmark", "bookmark_id": 4004, "title": "Uploaded File"}
        ],
        status=200,
    )

    api = InstapaperAPI(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="tok",
        oauth_token_secret="sec",
    )
    bookmark = api.add_bookmark(
        "https://instapaper.com/upload",
        content="<p>File content here</p>",
        is_private_from_source=True,
    )
    assert bookmark["bookmark_id"] == 4004
    # Verify content was sent in the request body
    body = responses.calls[-1].request.body.decode()
    assert "content" in body
    assert "is_private_from_source" in body


@responses.activate
def test_get_text():
    """get_text should return article HTML."""
    from instapaper.api import InstapaperAPI

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/get_text",
        body="<p>Article content here</p>",
        status=200,
        content_type="text/html",
    )

    api = InstapaperAPI(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="tok",
        oauth_token_secret="sec",
    )
    html = api.get_text(1001)
    assert "Article content here" in html


@responses.activate
def test_archive_bookmark():
    """archive should return the archived bookmark."""
    from instapaper.api import InstapaperAPI

    responses.add(
        responses.POST,
        "https://www.instapaper.com/api/1/bookmarks/archive",
        json=[{"type": "bookmark", "bookmark_id": 1001}],
        status=200,
    )

    api = InstapaperAPI(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="tok",
        oauth_token_secret="sec",
    )
    result = api.archive(1001)
    assert result["bookmark_id"] == 1001
