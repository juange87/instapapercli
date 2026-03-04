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
