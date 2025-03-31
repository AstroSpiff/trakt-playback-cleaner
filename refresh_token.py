import os
import requests
import json

CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
CLIENT_SECRET = os.getenv('TRAKT_CLIENT_SECRET')
CURRENT_REFRESH_TOKEN = os.getenv('TRAKT_REFRESH_TOKEN')

payload = {
    "refresh_token": CURRENT_REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "refresh_token"
}

response = requests.post("https://api.trakt.tv/oauth/token", json=payload)

# Per debug: stampa l'intero JSON restituito
print("Output API (debug):")
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data))  # Output finale in formato JSON
else:
    error_data = {
        "error": response.text,
        "status_code": response.status_code
    }
    print(json.dumps(error_data))
