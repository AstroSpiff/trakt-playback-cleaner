import os
import time
import requests

CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
ACCESS_TOKEN = os.getenv('TRAKT_ACCESS_TOKEN')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'trakt-api-version': '2',
    'trakt-api-key': CLIENT_ID
}

# Recupera tutti i playback attuali
response = requests.get('https://api.trakt.tv/sync/playback', headers=headers)
if response.status_code != 200:
    print("Errore nel recupero dei playback:")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    exit(1)

playbacks = response.json()

# Per ogni playback prova a cancellarlo
for playback in playbacks:
    playback_id = playback['id']
    del_response = requests.delete(f'https://api.trakt.tv/sync/playback/{playback_id}', headers=headers)
    
    if del_response.status_code == 204:
        print(f"Playback {playback_id} cancellato.")
    elif del_response.status_code == 429:  # Rate limit exceeded
        print(f"Rate limit raggiunto per il playback {playback_id}. Attendo 1 secondo e riprovo...")
        time.sleep(1)
        # Secondo tentativo
        del_response = requests.delete(f'https://api.trakt.tv/sync/playback/{playback_id}', headers=headers)
        if del_response.status_code == 204:
            print(f"Playback {playback_id} cancellato al secondo tentativo.")
        else:
            print(f"Errore durante la cancellazione del playback {playback_id} al secondo tentativo: {del_response.text}")
    else:
        print(f"Errore durante la cancellazione del playback {playback_id}: {del_response.text}")

print("Script completato con successo.")
