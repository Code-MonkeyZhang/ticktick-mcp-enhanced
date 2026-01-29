"""
TickTick OAuth authentication module.

This module handles the OAuth 2.0 flow logic and token management.
Refactored to support 'headless' MCP operation.
"""

import os
import json
import base64
import urllib.parse
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent
TOKEN_FILE = PROJECT_ROOT / ".ticktick_token.json"

DEFAULT_SCOPES = ["tasks:read", "tasks:write"]

VERSION_CONFIGS = {
    "global": {
        "name": "TickTick International",
        "auth_url": "https://ticktick.com/oauth/authorize",
        "token_url": "https://ticktick.com/oauth/token",
        "base_url": "https://api.ticktick.com/open/v1",
    },
    "china": {
        "name": "TickTick China (Dida365)",
        "auth_url": "https://dida365.com/oauth/authorize",
        "token_url": "https://dida365.com/oauth/token",
        "base_url": "https://api.dida365.com/open/v1",
    },
}


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles the OAuth callback from the browser."""

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if "code" in query_params:
            code = query_params["code"][0]

            success = self.server.auth_instance.exchange_code(code)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            if success:
                html_content = """
                    <html>
                    <head>
                        <title>Login Successful</title>
                        <style>
                            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 50px; background-color: #f5f5f7; color: #1d1d1f; }
                            .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
                            h1 { color: #2ecc71; margin-bottom: 10px; }
                            p { font-size: 18px; line-height: 1.5; color: #86868b; }
                            .icon { font-size: 64px; margin-bottom: 20px; display: block; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <span class="icon">✅</span>
                            <h1>Authentication Successful!</h1>
                            <p>TickTick has been connected successfully.</p>
                            <p>You can now close this window and return to your AI agent.</p>
                        </div>
                        <script>window.close();</script>
                    </body>
                    </html>
                """
                self.wfile.write(html_content.encode("utf-8"))
            else:
                self.wfile.write(b"""
                    <html><body><h1>Authentication Failed</h1><p>Could not exchange code for token. Please check logs.</p></body></html>
                """)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


class TickTickAuth:
    """TickTick OAuth authentication manager."""

    def __init__(self):
        self.account_type = os.getenv("TICKTICK_ACCOUNT_TYPE", "global").lower()
        if self.account_type not in VERSION_CONFIGS:
            self.account_type = "global"

        self.config = VERSION_CONFIGS[self.account_type]

        self.client_id = os.getenv("TICKTICK_CLIENT_ID")
        self.client_secret = os.getenv("TICKTICK_CLIENT_SECRET")
        self.redirect_uri = os.getenv(
            "TICKTICK_REDIRECT_URI", "http://localhost:8000/callback"
        )

        self.access_token = None
        self.load_token()

        self._server = None
        self._server_thread = None

    def is_configured(self) -> bool:
        """Check if Client ID and Secret are provided."""
        return bool(self.client_id and self.client_secret)

    def is_authenticated(self) -> bool:
        """Check if we have a valid access token."""
        return bool(self.access_token)

    def start_local_server(self):
        """Start a local HTTP server to listen for OAuth callback."""
        if self._server:
            return

        try:
            parsed_uri = urllib.parse.urlparse(self.redirect_uri)
            port = parsed_uri.port or 80

            HTTPServer.allow_reuse_address = True
            self._server = HTTPServer(("localhost", port), OAuthCallbackHandler)
            self._server.auth_instance = self

            self._server_thread = threading.Thread(target=self._server.serve_forever)
            self._server_thread.daemon = True
            self._server_thread.start()

        except Exception as e:
            pass

    def get_auth_url(self) -> str:
        """Generate the authorization URL for the user."""
        if not self.is_configured():
            raise ValueError(
                "Missing TICKTICK_CLIENT_ID or TICKTICK_CLIENT_SECRET in environment."
            )

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(DEFAULT_SCOPES),
            "state": base64.urlsafe_b64encode(os.urandom(10)).decode("utf-8"),
        }
        query_string = urllib.parse.urlencode(params)
        return f"{self.config['auth_url']}?{query_string}"

    def exchange_code(self, code: str) -> bool:
        """Exchange auth code for access token."""
        if not self.is_configured():
            return False

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(DEFAULT_SCOPES),
        }

        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(
                self.config["token_url"], data=data, headers=headers
            )
            response.raise_for_status()
            token_data = response.json()

            self.save_token(token_data)
            return True
        except Exception as e:
            return False

    def save_token(self, token_data: dict):
        """Save token to local file."""
        try:
            self.access_token = token_data.get("access_token")
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f)
        except Exception as e:
            pass

    def load_token(self):
        """Load token from local file."""
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
            except Exception as e:
                pass

    def get_headers(self) -> dict:
        """Get headers for API requests."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_base_url(self) -> str:
        return self.config["base_url"]
