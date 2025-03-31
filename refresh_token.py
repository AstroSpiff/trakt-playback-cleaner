import os
import requests
import json

CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
CLIENT_SECRET = os.getenv('TRAKT_CLIENT_SECRET')
CURRENT_REFRESH_TOKEN = os.getenv('TRAKT_REFRESH_TOKEN')  # Assicurati di impostare questo secret

payload = {
    "refresh_token": CURRENT_REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "refresh_token"
}

response = requests.post("https://api.trakt.tv/oauth/token", json=payload)

if response.status_code == 200:
    data = response.json()
    new_access_token = data.get("access_token")
    new_refresh_token = data.get("refresh_token")
    print("Nuovo Access Token:", new_access_token)
    print("Nuovo Refresh Token:", new_refresh_token)
    # Qui puoi salvare i nuovi token dove ti servono (ad esempio, in un file o inviarli a un sistema di gestione dei segreti)
else:
    print("Errore nel refresh token:")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
