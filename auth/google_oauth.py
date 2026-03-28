# -*- coding: utf-8 -*-
"""Google OAuth authentication flow for Gmail and Calendar."""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from google_auth_oauthlib.flow import InstalledAppFlow

from copaw.agents.auth.storage import load_token, save_token, clear_token

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]

REDIRECT_URI = "http://localhost:9090/callback"


def get_credentials():
    """Load credentials from token file or return None if not authenticated.

    Returns:
        google.oauth2.credentials.Credentials or None
    """
    token_data = load_token()
    if token_data is None:
        return None

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    credentials = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=token_data.get("scopes"),
    )

    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            save_token({
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "scopes": list(credentials.scopes) if credentials.scopes else SCOPES,
            })
        except Exception:
            clear_token()
            return None

    return credentials


def _auth_callback_handler(code_holder: dict, server_holder: dict):
    """Returns a handler class for the OAuth callback."""
    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            if "code" in query:
                code_holder["code"] = query["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication successful!</h1><p>You can close this window.</p></body></html>")
            else:
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication failed.</h1></body></html>")

            threading.current_thread().do_run = False

        def log_message(self, format, *args):
            pass  # Suppress logging

    return CallbackHandler


def run_local_auth() -> bool:
    """Run local OAuth flow. Returns True if successful.

    Returns:
        True if authentication successful, False otherwise.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set")

    # Create the flow with explicit redirect_uri in the config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

    # Get authorization URL - library handles oob automatically for installed apps
    auth_url = flow.authorization_url()[0]

    print(f"\n=== Google OAuth Authentication ===")
    print(f"Please open this URL in your browser:\n")
    print(f"{auth_url}\n")
    print(f"After authorizing, Google will show a verification code.")
    print(f"Copy that code and enter it below.")
    print(f"\nEnter the verification code: ", end="", flush=True)

    code = input().strip()

    if not code:
        print("No code entered")
        return False

    flow.fetch_token(code=code)

    credentials = flow.credentials
    save_token({
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "scopes": list(credentials.scopes) if credentials.scopes else SCOPES,
    })

    print("Authentication successful!")
    return True
