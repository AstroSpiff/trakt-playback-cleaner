# Trakt Playback Cleaner

Questo tool pulisce i playback presenti in Trakt (endpoint `/sync/playback`).
È utile per rimuovere rapidamente gli elementi in stato "in riproduzione".

## Requisiti
- Python 3.11+
- Un'app Trakt con permessi `sync`

## Configurazione GitHub Actions
Il workflow è già presente in `.github/workflows/trakt-playback-cleaner.yml` e
gira ogni 30 minuti (più l'avvio manuale).

### Secrets richiesti
Imposta questi secrets nel repository:
- `TRAKT_CLIENT_ID`
- `TRAKT_CLIENT_SECRET`
- `TRAKT_REFRESH_TOKEN`
- `TRAKT_REDIRECT_URI` (opzionale, solo se non usi `urn:ietf:wg:oauth:2.0:oob`)

### Dove impostare i secrets su GitHub
1) Apri il repository su GitHub.
2) Vai su `Settings` → `Secrets and variables` → `Actions`.
3) Clicca `New repository secret` e aggiungi i valori richiesti.

Suggerimento: puoi rimuovere eventuali secrets non usati dal workflow per
ridurre confusione e superficie di rischio.

### Avvio e pianificazione del workflow
- Avvio manuale: `Actions` → `Trakt Playback Cleaner` → `Run workflow`.
- Pianificazione: è definita nel file
  `.github/workflows/trakt-playback-cleaner.yml` con cron ogni 30 minuti.
  Se non vuoi la schedulazione, rimuovi o commenta la sezione `schedule`.

### Come ottenere un refresh token
1) Crea o apri la tua app Trakt:
   `https://trakt.tv/oauth/applications`
2) Imposta la Redirect URI. Per la modalità manuale usa:
   `urn:ietf:wg:oauth:2.0:oob`
3) Ottieni un authorization code aprendo nel browser:

```
https://trakt.tv/oauth/authorize?response_type=code&client_id=TUO_CLIENT_ID&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=sync&state=xyz
```

4) Scambia il code con access + refresh token:

```bash
curl -s -X POST https://api.trakt.tv/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "code":"IL_TUO_CODE",
    "client_id":"TUO_CLIENT_ID",
    "client_secret":"TUO_CLIENT_SECRET",
    "redirect_uri":"urn:ietf:wg:oauth:2.0:oob",
    "grant_type":"authorization_code"
  }'
```

Nella risposta trovi `refresh_token`. Usa quel valore per il secret
`TRAKT_REFRESH_TOKEN`.

Nota: la `redirect_uri` deve essere la stessa usata durante l'autorizzazione.
Se aggiorni il refresh token, ricordati di aggiornare anche il secret
`TRAKT_REFRESH_TOKEN` su GitHub.

## Uso locale (opzionale)
Installazione dipendenze:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Refresh token -> access token:

```bash
export TRAKT_CLIENT_ID="..."
export TRAKT_CLIENT_SECRET="..."
export TRAKT_REFRESH_TOKEN="..."
export TRAKT_REDIRECT_URI="urn:ietf:wg:oauth:2.0:oob"  # opzionale
python refresh_token.py
```

Esempio di output:
```
{"access_token":"...","refresh_token":"...","expires_in":7776000,...}
```

Pulizia playback:

```bash
export TRAKT_CLIENT_ID="..."
export TRAKT_ACCESS_TOKEN="ACCESS_TOKEN_DALL_OUTPUT"
python clear_playback.py
```

## Variabili di configurazione (opzionali)
- `TRAKT_REQUEST_TIMEOUT` (default `10`)
- `TRAKT_MAX_RETRIES` (default `3`)
- `TRAKT_RETRY_BASE_SECONDS` (default `1`)
- `TRAKT_REDIRECT_URI` (default `urn:ietf:wg:oauth:2.0:oob`)

## Risoluzione problemi
- `invalid_grant`: refresh token scaduto, revocato o legato a un client diverso.
  Rigenera il refresh token e aggiorna i secrets.
- `redirect_uri mismatch`: la redirect URI non coincide con quella usata nella
  richiesta di autorizzazione iniziale.
