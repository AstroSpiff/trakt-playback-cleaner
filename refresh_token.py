import json
import os
import sys

import requests

REQUEST_TIMEOUT_SECONDS = float(os.getenv("TRAKT_REQUEST_TIMEOUT", "10"))


def require_env(name):
    value = os.getenv(name)
    if not value:
        print(f"Missing required env var: {name}", file=sys.stderr)
    return value


CLIENT_ID = require_env("TRAKT_CLIENT_ID")
CLIENT_SECRET = require_env("TRAKT_CLIENT_SECRET")
CURRENT_REFRESH_TOKEN = require_env("TRAKT_REFRESH_TOKEN")

if not CLIENT_ID or not CLIENT_SECRET or not CURRENT_REFRESH_TOKEN:
    sys.exit(1)

payload = {
    "refresh_token": CURRENT_REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "refresh_token",
}


def output_token_json(data):
    output_json = json.dumps(data)
    # Stampa sempre il JSON su stdout per il workflow
    print(output_json)


try:
    response = requests.post(
        "https://api.trakt.tv/oauth/token",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
except requests.RequestException as exc:
    error_data = {"error": str(exc)}
    print(json.dumps(error_data), file=sys.stderr)
    sys.exit(1)

if response.status_code == 200:
    try:
        token_data = response.json()
    except ValueError:
        print(
            json.dumps({"error": "Invalid JSON in token response."}),
            file=sys.stderr,
        )
        sys.exit(1)
    output_token_json(token_data)
else:
    error_data = {"error": response.text, "status_code": response.status_code}
    print(json.dumps(error_data), file=sys.stderr)
    sys.exit(1)
