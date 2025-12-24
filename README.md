# Trakt Playback Cleaner

Automatizza la pulizia dei playback su Trakt tramite GitHub Actions. Il sistema gestisce automaticamente il refresh dei token OAuth2 e la pulizia periodica dei playback in corso.

## Caratteristiche

- 🔄 **Auto-refresh token**: rinnovo automatico ogni 12 ore
- 🧹 **Pulizia automatica**: rimozione playback ogni 30 minuti
- 🔐 **Sicurezza**: token mascherati nei log, nessun dato sensibile esposto
- ⚙️ **Zero manutenzione**: completamente automatizzato

## Requisiti

- Un account GitHub (per GitHub Actions)
- Un'app Trakt con permessi `sync`
- Python 3.11+ (solo per uso locale)

## Configurazione rapida

### 1. Crea un'app Trakt

1. Vai su https://trakt.tv/oauth/applications
2. Clicca "New Application"
3. Compila i campi richiesti:
   - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob`
   - **Permissions**: seleziona `sync`
4. Salva l'applicazione e annota `Client ID` e `Client Secret`

### 2. Ottieni il refresh token

Apri nel browser (sostituisci `TUO_CLIENT_ID` con il tuo Client ID):

```
https://trakt.tv/oauth/authorize?response_type=code&client_id=TUO_CLIENT_ID&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=sync&state=xyz
```

Autorizza l'app e copia il **code** che appare.

Poi esegui questo comando (sostituisci i valori):

```bash
curl -s -X POST https://api.trakt.tv/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "code":"IL_CODE_COPIATO",
    "client_id":"TUO_CLIENT_ID",
    "client_secret":"TUO_CLIENT_SECRET",
    "redirect_uri":"urn:ietf:wg:oauth:2.0:oob",
    "grant_type":"authorization_code"
  }'
```

Dalla risposta JSON, copia il valore di `refresh_token`.

### 3. Crea un GitHub Personal Access Token (PAT)

Il PAT è necessario per permettere ai workflow di aggiornare automaticamente i secrets.

1. Vai su GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Clicca "Generate new token (classic)"
3. Assegna un nome (es. "Trakt Playback Cleaner")
4. Seleziona lo scope `repo` (accesso completo ai repository privati)
5. Clicca "Generate token" e copia il token generato

**Oppure** usa un Fine-grained token:
1. Vai su Personal access tokens → Fine-grained tokens
2. Crea un token con accesso al repository specifico
3. Permessi richiesti: "Secrets" → Read and write

### 4. Configura i secrets su GitHub

1. Apri il tuo repository su GitHub
2. Vai su **Settings** → **Secrets and variables** → **Actions**
3. Clicca **New repository secret** e aggiungi i seguenti secrets:

| Nome | Valore | Descrizione |
|------|--------|-------------|
| `TRAKT_CLIENT_ID` | Il tuo Client ID | ID dell'app Trakt |
| `TRAKT_CLIENT_SECRET` | Il tuo Client Secret | Secret dell'app Trakt |
| `TRAKT_REFRESH_TOKEN` | Il refresh token ottenuto | Token per rinnovare l'accesso |
| `GH_PAT` | Il tuo Personal Access Token | Permette l'aggiornamento automatico dei secrets |

**Nota**: Non è necessario creare manualmente `TRAKT_ACCESS_TOKEN` - verrà generato automaticamente dal workflow "Refresh Trakt Token".

### 5. Avvia il primo refresh

1. Vai su **Actions** nel tuo repository
2. Seleziona il workflow **"Refresh Trakt Token"**
3. Clicca **Run workflow** → **Run workflow**
4. Attendi il completamento (circa 1 minuto)

Questo genererà e salverà automaticamente il primo `TRAKT_ACCESS_TOKEN`.

### 6. Verifica il funzionamento

1. Esegui manualmente il workflow **"Trakt Playback Cleaner"**
2. Controlla i log per verificare che non ci siano errori
3. Dovresti vedere: `Nessun playback da cancellare.` (se non hai playback attivi)

## Come funziona

### Workflow "Refresh Trakt Token"

- **Pianificazione**: ogni 12 ore (automatico)
- **Funzione**: rinnova access e refresh token
- **Output**: aggiorna automaticamente i secrets `TRAKT_ACCESS_TOKEN` e `TRAKT_REFRESH_TOKEN`

Il workflow:
1. Usa il `TRAKT_REFRESH_TOKEN` salvato per ottenere nuovi token
2. Maschera i token nei log per sicurezza
3. Salva i nuovi token nei secrets tramite GitHub CLI

### Workflow "Trakt Playback Cleaner"

- **Pianificazione**: ogni 30 minuti (automatico)
- **Funzione**: rimuove tutti i playback in corso su Trakt
- **Output**: log del numero di playback cancellati

Il workflow usa `TRAKT_ACCESS_TOKEN` per autenticarsi e rimuovere i playback tramite l'API `/sync/playback`.

## Modificare la pianificazione

Puoi modificare la frequenza dei workflow editando i file in `.github/workflows/`:

**Refresh Trakt Token** (`.github/workflows/refresh-token.yml`):
```yaml
schedule:
  - cron: '0 */12 * * *'  # Ogni 12 ore
```

**Trakt Playback Cleaner** (`.github/workflows/trakt-playback-cleaner.yml`):
```yaml
schedule:
  - cron: '*/30 * * * *'  # Ogni 30 minuti
```

Usa [crontab.guru](https://crontab.guru/) per creare la tua pianificazione personalizzata.

## Uso locale (opzionale)

Se vuoi testare gli script localmente:

### Installazione dipendenze

```bash
pip install -r requirements.txt
```

### Refresh token manuale

```bash
export TRAKT_CLIENT_ID="il_tuo_client_id"
export TRAKT_CLIENT_SECRET="il_tuo_client_secret"
export TRAKT_REFRESH_TOKEN="il_tuo_refresh_token"
python refresh_token.py
```

Output:
```json
{"access_token":"...","refresh_token":"...","expires_in":7776000,...}
```

### Pulizia playback manuale

```bash
export TRAKT_CLIENT_ID="il_tuo_client_id"
export TRAKT_ACCESS_TOKEN="access_token_dall_output_precedente"
python clear_playback.py
```

## Variabili di configurazione (opzionali)

Puoi personalizzare il comportamento tramite variabili d'ambiente:

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `TRAKT_REQUEST_TIMEOUT` | `10` | Timeout richieste HTTP (secondi) |
| `TRAKT_MAX_RETRIES` | `3` | Numero massimo di tentativi |
| `TRAKT_RETRY_BASE_SECONDS` | `1` | Tempo base tra i tentativi (secondi) |
| `TRAKT_REDIRECT_URI` | `urn:ietf:wg:oauth:2.0:oob` | Redirect URI per OAuth2 |

## Risoluzione problemi

### Errore `invalid_grant`

**Causa**: Il refresh token è scaduto, revocato o non valido.

**Soluzione**:
1. Revoca l'accesso all'app su https://trakt.tv/oauth/authorized_applications
2. Rigenera un nuovo refresh token (vedi sezione "Ottieni il refresh token")
3. Aggiorna il secret `TRAKT_REFRESH_TOKEN` su GitHub
4. Esegui manualmente "Refresh Trakt Token"

### Errore `401 Unauthorized`

**Causa**: L'access token non è valido o è scaduto.

**Soluzione**:
1. Esegui manualmente il workflow "Refresh Trakt Token"
2. Verifica che il secret `TRAKT_ACCESS_TOKEN` sia stato creato
3. Riprova "Trakt Playback Cleaner"

### Errore `redirect_uri mismatch`

**Causa**: La redirect URI non corrisponde a quella configurata nell'app Trakt.

**Soluzione**:
1. Verifica che la Redirect URI nell'app Trakt sia: `urn:ietf:wg:oauth:2.0:oob`
2. Usa la stessa URI quando generi il refresh token

### I workflow non partono automaticamente

**Causa**: GitHub Actions potrebbe essere disabilitato o i workflow non hanno i permessi.

**Soluzione**:
1. Vai su **Settings** → **Actions** → **General**
2. Verifica che "Allow all actions and reusable workflows" sia selezionato
3. In "Workflow permissions", assicurati che i workflow abbiano i permessi necessari

## Sicurezza

- ✅ Tutti i token sono mascherati nei log con `::add-mask::`
- ✅ I secrets sono criptati da GitHub
- ✅ Nessun dato sensibile viene mai committato nel repository
- ✅ Il `GH_PAT` ha accesso solo ai secrets del repository

## Licenza

Questo progetto è fornito "as is" senza garanzie. Usalo a tuo rischio.
