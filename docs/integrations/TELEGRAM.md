# Telegram Gateway (local-first, no LLM for logging)

The Telegram gateway receives private messages using Telegram Bot API long polling. Deterministic text commands and supported voice messages are processed locally and written to SQLite only after explicit confirmation. No LLM is called for registration or speech transcription.

## Security prerequisites

1. Create a bot with Telegram's BotFather.
2. Send `/start` to the bot from your private Telegram account.
3. Set `FITNESS_MANAGER_TELEGRAM_BOT_TOKEN` temporarily and run `python scripts/telegram_whoami.py` to display pending private-chat sender IDs (message text is not printed).
4. Set these environment variables in the local shell or OS secret manager:
   - `FITNESS_MANAGER_TELEGRAM_BOT_TOKEN`
   - `FITNESS_MANAGER_TELEGRAM_ALLOWED_USER_ID`
5. Do not commit the token, chat history, database, or local `.env` file.
6. Use a private chat. Group messages and messages from other user IDs are ignored.

The bot token is a credential, not an AI token. Interactive mode uses a hidden prompt; avoid placing the token directly in shell commands or source files. Telegram transport still requires an internet connection. Long polling avoids exposing a local webhook port to the public internet.

## Start

```powershell
python scripts/fitness_manager.py init
python scripts/telegram_gateway.py
```

For optional local voice transcription, install:

```powershell
pip install -r requirements-audio.txt
```

The first transcription may download the configured faster-whisper model weights. By default the model is `base`, language is Portuguese, device is CPU, and compute type is `int8`. Cached model weights allow subsequent local/offline inference. Set `FITNESS_MANAGER_WHISPER_MODEL`, `FITNESS_MANAGER_WHISPER_DEVICE`, or `FITNESS_MANAGER_WHISPER_COMPUTE_TYPE` to customize. The gateway accepts voice/audio up to 15 MB and five minutes.

## Supported commands

```text
/ajuda
/peso 72,4
/cintura 83
/corrida 4;42
/treino A;Supino reto;3;12;20
/alimento almoco;arroz;150
/confirmar 12
/cancelar 12
/status
/perguntar Como esta minha evolucao?
```

Free-text deterministic patterns currently supported:

```text
peso 72,4 kg
cintura 83 cm
corrida 4 km em 42 min
```

Every parsed health record first becomes a pending event. The user must send `/confirmar ID` before it is written to the corresponding history table. `/cancelar ID` rejects it. Unsupported messages are retained as unsupported ingestion events but do not create health records. Duplicate Telegram message IDs are idempotent.

Food records do not receive invented calories or macronutrients. If the user does not supply nutrition values, those columns remain null.

## Optional local LLM questions

The `/perguntar` command is disabled until a local OpenAI-compatible endpoint and model are configured:

- `FITNESS_MANAGER_LOCAL_LLM_URL`, for example `http://127.0.0.1:11434/v1`
- `FITNESS_MANAGER_LOCAL_LLM_MODEL`, for example the exact model tag installed in Ollama

The initial adapter accepts loopback endpoints only (`localhost`, `127.0.0.1`, `::1`). It does not silently fall back to a cloud provider. The question and a small summary of recent weight, waist, and running records are sent to the local model. Do not configure a remote URL unless you intentionally change and review this security boundary.

## Data and reliability

- `integration_events` stores inbound message metadata, parse result, confirmation state, and local result ID.
- `integration_state` stores the last processed Telegram update offset.
- `(source, external_event_id)` is unique, preventing duplicate message ingestion.
- A message is persisted before the polling offset advances. On restart, a repeated update will not duplicate the health record.
- Telegram retains pending updates for a limited period; SQLite is the permanent history.

## Voice messages

The gateway accepts Telegram voice notes and audio files. It downloads the file only after sender authorization, applies size/duration limits, transcribes in a temporary directory, and deletes the audio after processing. The bot returns the transcript and structured candidate for review. Use `/confirmar ID` to save or `/cancelar ID` to discard. If local transcription dependencies/model are unavailable, the bot reports the issue and creates no health record. Supported speech grammar is intentionally limited; ambiguous speech must be corrected by the user.

## Limitations

- Image input and OCR are not implemented.
- Free-text parsing is intentionally narrow. Ambiguous messages are not recorded as health data.
- Long polling requires the local gateway process to remain running.
- Telegram Bot API is an external messaging service; message content necessarily passes through Telegram.

The Telegram service itself still receives the original message/audio. Local transcription means the audio is not sent to an external AI transcription provider; it does not mean Telegram transport is end-to-end private storage.
