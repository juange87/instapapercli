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
