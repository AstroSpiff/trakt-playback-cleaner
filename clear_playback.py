import os
import sys
import time

import requests

REQUEST_TIMEOUT_SECONDS = float(os.getenv("TRAKT_REQUEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("TRAKT_MAX_RETRIES", "3"))
RETRY_BASE_SECONDS = float(os.getenv("TRAKT_RETRY_BASE_SECONDS", "1"))


def require_env(name):
    value = os.getenv(name)
    if not value:
        print(f"Missing required env var: {name}", file=sys.stderr)
    return value


CLIENT_ID = require_env("TRAKT_CLIENT_ID")
ACCESS_TOKEN = require_env("TRAKT_ACCESS_TOKEN")

if not CLIENT_ID or not ACCESS_TOKEN:
    sys.exit(1)

session = requests.Session()
session.headers.update(
    {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "trakt-api-version": "2",
        "trakt-api-key": CLIENT_ID,
    }
)


def retry_seconds(response, attempt):
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(1, int(retry_after))
        except ValueError:
            pass
    return RETRY_BASE_SECONDS * (2 ** (attempt - 1))


def request_with_retry(method, url):
    last_response = None
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.request(method, url, timeout=REQUEST_TIMEOUT_SECONDS)
            last_response = response
        except requests.RequestException as exc:
            last_error = exc
            response = None

        if response is not None and response.status_code != 429:
            return response

        if attempt == MAX_RETRIES:
            break

        if response is None:
            wait_seconds = RETRY_BASE_SECONDS * (2 ** (attempt - 1))
            print(
                f"Request error, retrying in {wait_seconds}s: {last_error}",
                file=sys.stderr,
            )
        else:
            wait_seconds = retry_seconds(response, attempt)
            print(
                f"Rate limit raggiunto, retry in {wait_seconds}s...",
                file=sys.stderr,
            )
        time.sleep(wait_seconds)

    if last_response is None:
        print(
            f"Request failed after {MAX_RETRIES} attempts: {last_error}",
            file=sys.stderr,
        )
        return None
    return last_response


response = request_with_retry("GET", "https://api.trakt.tv/sync/playback")
if response is None:
    sys.exit(1)

if response.status_code != 200:
    print("Errore nel recupero dei playback:", file=sys.stderr)
    print("Status Code:", response.status_code, file=sys.stderr)
    print("Response:", response.text, file=sys.stderr)
    sys.exit(1)

try:
    playbacks = response.json()
except ValueError:
    print("Errore nella risposta JSON dei playback.", file=sys.stderr)
    sys.exit(1)

if not isinstance(playbacks, list):
    print("Formato inatteso per la lista playback.", file=sys.stderr)
    sys.exit(1)

if not playbacks:
    print("Nessun playback da cancellare.")
    sys.exit(0)

successes = 0
failures = 0

for playback in playbacks:
    playback_id = playback.get("id")
    if not playback_id:
        print("Playback senza ID, salto.", file=sys.stderr)
        failures += 1
        continue

    del_response = request_with_retry(
        "DELETE", f"https://api.trakt.tv/sync/playback/{playback_id}"
    )
    if del_response is None:
        failures += 1
        continue

    if del_response.status_code == 204:
        print(f"Playback {playback_id} cancellato.")
        successes += 1
    else:
        print(
            f"Errore durante la cancellazione del playback {playback_id}: "
            f"{del_response.status_code} {del_response.text}",
            file=sys.stderr,
        )
        failures += 1

if failures:
    print(
        f"Completato con errori. Successi: {successes}, errori: {failures}.",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"Completato. Successi: {successes}.")
