import os
import requests

CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
ACCESS_TOKEN = os.getenv('TRAKT_ACCESS_TOKEN')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'trakt-api-version': '2',
    'trakt-api-key': CLIENT_ID
}

# Ottieni la lista dei playback attuali
response = requests.get('https://api.trakt.tv/sync/playback', headers=headers)

if response.status_code != 200:
    print("Errore nel recupero dei playback:", response.text)
    exit(1)

playbacks = response.json()

# Cancella tutti i playback
for playback in playbacks:
    playback_id = playback['id']
    del_response = requests.delete(f'https://api.trakt.tv/sync/playback/{playback_id}', headers=headers)
    if del_response.status_code == 204:
        print(f"Playback {playback_id} cancellato.")
    else:
        print(f"Errore durante la cancellazione del playback {playback_id}: {del_response.text}")

print("Script completato con successo.")
