"""Instapaper API client using OAuth 1.0a."""

from urllib.parse import parse_qs

from requests_oauthlib import OAuth1Session

BASE_URL = "https://www.instapaper.com"


class InstapaperError(Exception):
    """Error from the Instapaper API."""


class InstapaperAPI:
    """Client for the Instapaper Full API."""

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        oauth_token: str | None = None,
        oauth_token_secret: str | None = None,
    ):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

    def _session(self) -> OAuth1Session:
        """Create an OAuth1 session with current credentials."""
        return OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret,
        )

    def login(self, username: str, password: str) -> tuple[str, str]:
        """Authenticate via xAuth and return (oauth_token, oauth_token_secret)."""
        session = OAuth1Session(
            self.consumer_key, client_secret=self.consumer_secret
        )
        resp = session.post(
            f"{BASE_URL}/api/1/oauth/access_token",
            data={
                "x_auth_username": username,
                "x_auth_password": password,
                "x_auth_mode": "client_auth",
            },
        )
        if resp.status_code != 200:
            raise InstapaperError(f"Login failed (HTTP {resp.status_code})")

        parsed = parse_qs(resp.text)
        token = parsed["oauth_token"][0]
        secret = parsed["oauth_token_secret"][0]
        self.oauth_token = token
        self.oauth_token_secret = secret
        return token, secret

    def _post(self, path: str, **params) -> list:
        """Make authenticated POST request, return parsed JSON."""
        session = self._session()
        resp = session.post(f"{BASE_URL}{path}", data=params)
        if resp.status_code != 200:
            raise InstapaperError(
                f"API error: {path} returned HTTP {resp.status_code}"
            )
        return resp.json()

    def verify_credentials(self) -> dict:
        """Verify OAuth credentials, return user dict."""
        result = self._post("/api/1/account/verify_credentials")
        return result[0]

    def list_bookmarks(
        self, limit: int = 25, folder_id: str | None = None
    ) -> list[dict]:
        """List bookmarks. Returns only bookmark-type entries."""
        params = {"limit": limit}
        if folder_id:
            params["folder_id"] = folder_id
        result = self._post("/api/1/bookmarks/list", **params)
        return [item for item in result if item.get("type") == "bookmark"]

    def add_bookmark(
        self,
        url: str,
        title: str | None = None,
        folder_id: str | None = None,
        content: str | None = None,
        is_private_from_source: bool = False,
    ) -> dict:
        """Add a bookmark. Returns the bookmark dict."""
        params = {"url": url}
        if title:
            params["title"] = title
        if folder_id:
            params["folder_id"] = folder_id
        if content:
            params["content"] = content
        if is_private_from_source:
            params["is_private_from_source"] = "1"
        result = self._post("/api/1/bookmarks/add", **params)
        return [item for item in result if item.get("type") == "bookmark"][0]

    def get_text(self, bookmark_id: int) -> str:
        """Get processed HTML text of a bookmark."""
        session = self._session()
        resp = session.post(
            f"{BASE_URL}/api/1/bookmarks/get_text",
            data={"bookmark_id": bookmark_id},
        )
        if resp.status_code != 200:
            raise InstapaperError(
                f"Failed to get text for bookmark {bookmark_id} "
                f"(HTTP {resp.status_code})"
            )
        return resp.text

    def archive(self, bookmark_id: int) -> dict:
        """Archive a bookmark."""
        result = self._post(
            "/api/1/bookmarks/archive", bookmark_id=bookmark_id
        )
        return [item for item in result if item.get("type") == "bookmark"][0]

    def delete(self, bookmark_id: int) -> None:
        """Permanently delete a bookmark."""
        self._post("/api/1/bookmarks/delete", bookmark_id=bookmark_id)
