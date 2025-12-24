import json
import os
import sys

import requests

REQUEST_TIMEOUT_SECONDS = float(os.getenv("TRAKT_REQUEST_TIMEOUT", "10"))
REDIRECT_URI = os.getenv("TRAKT_REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob")


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
    "redirect_uri": REDIRECT_URI,
    "grant_type": "refresh_token",
}


def output_token_json(data):
    output_json = json.dumps(data)
    if os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("GITHUB_OUTPUT"):
        for key in ("access_token", "refresh_token"):
            token_value = data.get(key)
            if token_value:
                print(f"::add-mask::{token_value}")
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            access_token = data.get("access_token", "")
            refresh_token = data.get("refresh_token", "")
            handle.write(f"access_token={access_token}\n")
            handle.write(f"refresh_token={refresh_token}\n")
            handle.write("token_json<<EOF\n")
            handle.write(output_json)
            handle.write("\nEOF\n")
        print("Token JSON written to GITHUB_OUTPUT.")
    else:
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
