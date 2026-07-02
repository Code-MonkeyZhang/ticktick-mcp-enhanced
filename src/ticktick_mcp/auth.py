"""
TickTick OAuth authentication module.

This module handles the OAuth 2.0 flow logic and token management.
Credentials are provided at runtime via the login tool, not environment variables.
"""

import os
import json
import base64
import logging
import urllib.parse
import webbrowser
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

logger = logging.getLogger(__name__)

PACKAGE_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent
CONFIG_FILE = PROJECT_ROOT / ".ticktick_config.json"

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
    """TickTick OAuth authentication manager.

    Credentials are provided at runtime via configure() and persisted to
    a local config file. On startup, __init__ loads the config file to
    restore a previous session without requiring environment variables.
    """

    def __init__(self):
        self.account_type = None
        self.config = None
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = "http://localhost:8000/callback"
        self.access_token = None
        self._raw_token = None
        self._server = None
        self._server_thread = None
        self._auth_event = threading.Event()
        self._auth_error = None
        self._load_config()

    def configure(self, client_id: str, client_secret: str,
                  account_type: str = "china",
                  redirect_uri: str = "http://localhost:8000/callback") -> bool:
        """Set credentials at runtime and persist them to the config file.

        Called by the login MCP tool when the user provides their OAuth
        credentials.

        Args:
            client_id: OAuth application Client ID
            client_secret: OAuth application Client Secret
            account_type: "china" for Dida365 or "global" for TickTick international
            redirect_uri: Callback URL registered in the developer console

        Returns:
            True if configuration succeeded, False if account_type is invalid
        """
        account_type = account_type.lower()
        if account_type not in VERSION_CONFIGS:
            logger.error(f"Invalid account_type: {account_type}")
            return False

        self.client_id = client_id
        self.client_secret = client_secret
        self.account_type = account_type
        self.config = VERSION_CONFIGS[account_type]
        self.redirect_uri = redirect_uri
        self._save_config()

        logger.info(f"Credentials configured for {self.config['name']}")
        return True

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

            logger.info(f"Callback server started on port {port}")
        except Exception as e:
            logger.warning(f"Failed to start callback server: {e}")

    def get_auth_url(self) -> str:
        """Generate the authorization URL for the user."""
        if not self.is_configured():
            raise ValueError(
                "Missing client_id or client_secret. Call configure() first."
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
        """Exchange auth code for access token.

        On completion, signals the _auth_event so that start_oauth_flow
        can stop blocking, regardless of success or failure.
        """
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
            logger.info("Token exchange successful")
            return True
        except Exception as e:
            self._auth_error = str(e)
            logger.error(f"Token exchange failed: {e}")
            return False
        finally:
            self._auth_event.set()

    def start_oauth_flow(self) -> str:
        """Run the full OAuth flow and block until callback, error, or timeout.

        Starts the local callback server, opens the browser for the user
        to authorize, then blocks on _auth_event until exchange_code signals
        completion. The blocking wait has a 120-second timeout.

        Returns:
            - "success" if authentication completed
            - "error:{message}" if the code exchange failed
            - "timeout:{url}" if the user did not authorize in time
        """
        self._auth_event.clear()
        self._auth_error = None

        self.start_local_server()
        url = self.get_auth_url()

        try:
            webbrowser.open(url)
            logger.info("Browser opened for authorization")
        except Exception as e:
            logger.warning(f"Failed to open browser: {e}")

        self._auth_event.wait(timeout=120)

        if self.is_authenticated():
            return "success"
        if self._auth_error:
            return f"error:{self._auth_error}"

        logger.warning("OAuth flow timed out waiting for callback")
        return f"timeout:{url}"

    def save_token(self, token_data: dict):
        """Store the access token and persist the full config."""
        self.access_token = token_data.get("access_token")
        self._raw_token = token_data
        self._save_config()

    def _save_config(self):
        """Persist credentials and token to CONFIG_FILE."""
        data = {
            "account_type": self.account_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "token": self._raw_token,
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def _load_config(self):
        """Load credentials and token from CONFIG_FILE on startup."""
        if not CONFIG_FILE.exists():
            return
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)

            self.account_type = data.get("account_type")
            self.config = VERSION_CONFIGS.get(self.account_type)
            self.client_id = data.get("client_id")
            self.client_secret = data.get("client_secret")
            self.redirect_uri = data.get(
                "redirect_uri", "http://localhost:8000/callback"
            )

            token = data.get("token")
            if token:
                self.access_token = token.get("access_token")
                self._raw_token = token

            if self.is_configured():
                logger.info(f"Config loaded for {self.config['name']}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def get_headers(self) -> dict:
        """Get headers for API requests."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_base_url(self) -> str:
        """Get the API base URL for the configured account type."""
        if not self.config:
            return ""
        return self.config["base_url"]
