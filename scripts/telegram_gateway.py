#!/usr/bin/env python3
"""Telegram long-polling gateway. Deterministic records do not call an LLM."""
from __future__ import annotations

import getpass
import json
import os
import sys
import time
import tempfile
import urllib.error
import urllib.parse
import re
import sqlite3
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fitness_manager.db import initialize, session, DB_PATH  # noqa: E402
from fitness_manager.ingestion import (  # noqa: E402
    confirm_event, create_inbound_event, get_offset, mark_event_error, parse_message, reject_event, save_offset,
)
from fitness_manager.local_llm import ask_local_model  # noqa: E402
from fitness_manager.audio import MAX_AUDIO_BYTES, transcribe_audio_local  # noqa: E402


class TelegramClient:
    def __init__(self, token: str):
        self.token = token
        self.base = f"https://api.telegram.org/bot{token}/"

    def call(self, method: str, payload: dict | None = None, timeout: int = 40):
        data = json.dumps(payload or {}).encode("utf-8")
        request = urllib.request.Request(self.base + method, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Falha de comunicacao com Telegram ({type(exc).__name__}).") from exc
        if not result.get("ok"):
            raise RuntimeError("Telegram retornou erro na operacao solicitada.")
        return result.get("result")

    def send(self, chat_id: int, text: str):
        return self.call("sendMessage", {"chat_id": chat_id, "text": text[:4000]}, timeout=20)

    def download_audio(self, file_id: str, max_bytes: int = MAX_AUDIO_BYTES) -> bytes:
        """Download a Telegram voice/audio file with a strict size and path limit."""
        metadata = self.call("getFile", {"file_id": file_id}, timeout=20)
        file_path = str(metadata.get("file_path", ""))
        file_size = int(metadata.get("file_size", 0) or 0)
        if (not file_path or ".." in file_path.split("/")
                or not re.fullmatch(r"[A-Za-z0-9_./-]+", file_path)):
            raise RuntimeError("Telegram retornou um caminho de arquivo invalido.")
        if file_size > max_bytes:
            raise RuntimeError("Audio acima do limite de 15 MB.")
        safe_path = urllib.parse.quote(file_path, safe="/._-")
        url = f"https://api.telegram.org/file/bot{self.token}/{safe_path}"
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = response.read(max_bytes + 1)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("Nao foi possivel baixar o audio do Telegram.") from exc
        if not data or len(data) > max_bytes:
            raise RuntimeError("Audio vazio ou acima do limite de 15 MB.")
        return data


def _context_summary() -> str:
    with session() as conn:
        rows = conn.execute("SELECT measured_at,value,unit FROM measurements WHERE kind='weight' ORDER BY measured_at DESC,id DESC LIMIT 3").fetchall()
        waist = conn.execute("SELECT measured_at,value,unit FROM measurements WHERE kind='waist' ORDER BY measured_at DESC,id DESC LIMIT 1").fetchone()
        runs = conn.execute("SELECT performed_at,distance_km,duration_sec,pace_sec_per_km FROM runs ORDER BY performed_at DESC,id DESC LIMIT 3").fetchall()
    bits = []
    if rows:
        bits.append("Pesagens recentes: " + "; ".join(f"{r['value']} {r['unit']} em {r['measured_at']}" for r in rows))
    if waist:
        bits.append(f"Ultima cintura: {waist['value']} {waist['unit']} em {waist['measured_at']}")
    if runs:
        bits.append("Corridas recentes: " + "; ".join(f"{r['distance_km']} km em {r['duration_sec']} s" for r in runs))
    return "\n".join(bits) or "Ainda nao ha historico registrado."


def _help_text() -> str:
    return (
        "Fitness Manager - comandos sem IA:\n"
        "/peso 72,4\n/cintura 83\n/corrida 4;42  (km;minutos)\n"
        "/treino A;Supino reto;3;12;20  (sessao;exercicio;series;reps;kg)\n"
        "/alimento almoco;arroz;150  (refeicao;alimento;gramas)\n"
        "/confirmar ID | /cancelar ID\n/perguntar sua pergunta (usa apenas modelo local configurado)\n"
        "Tambem aceito texto simples: 'peso 72,4 kg', 'cintura 83 cm' e 'corrida 4 km em 42 min'.\n"
        "Envie tambem uma mensagem de voz: a transcricao local sera exibida para confirmacao. "
        "Audio original e temporario e sera apagado apos o processamento. "
        "Registros ficam pendentes ate sua confirmacao. Macros nao informados nao serao inventados."
    )


def _command_payload(text: str):
    raw = text.strip()
    low = raw.lower()
    if low.startswith('/peso '):
        return parse_message('peso ' + raw.split(None, 1)[1])
    if low.startswith('/cintura '):
        return parse_message('cintura ' + raw.split(None, 1)[1])
    if low.startswith('/corrida '):
        parts = raw.split(None, 1)[1].replace(',', '.').split(';')
        if len(parts) == 2:
            return parse_message(f'corrida {parts[0].strip()} km em {parts[1].strip()} min')
        return None
    if low.startswith('/treino '):
        return parse_message('treino ' + raw.split(None, 1)[1])
    if low.startswith('/alimento '):
        return parse_message('alimento ' + raw.split(None, 1)[1])
    return None


def _format_candidate(payload: dict) -> str:
    kind = payload['type']
    if kind == 'measurement':
        return f"Medida: {payload['kind']} = {payload['value']} {payload['unit']} em {payload['date']}"
    if kind == 'run':
        return f"Corrida: {payload['distance_km']} km em {payload['duration_min']} min"
    if kind == 'workout':
        return f"Treino {payload['session']}: {payload['exercise']} - {payload['sets']}x{payload['reps']} com {payload['load_kg']} kg"
    if kind == 'food':
        return f"Alimento: {payload['food']} - {payload['quantity_g']} g ({payload['meal']}); macros nao informados"
    return 'Registro identificado.'


def _handle_voice_message(client, message: dict, sender_id: int, chat_id: int) -> None:
    media = message.get("voice") or message.get("audio") or {}
    file_id = media.get("file_id")
    file_size = int(media.get("file_size", 0) or 0)
    duration = int(media.get("duration", 0) or 0)
    message_id = str(message.get("message_id", ""))
    if not file_id or not message_id:
        client.send(chat_id, "Nao consegui identificar o arquivo de audio. Nada foi registrado.")
        return
    if file_size > MAX_AUDIO_BYTES:
        client.send(chat_id, "Audio acima do limite de 15 MB. Nada foi registrado.")
        return
    if duration > 300:
        client.send(chat_id, "Audio acima do limite de 5 minutos. Envie uma mensagem mais curta.")
        return

    try:
        audio_bytes = client.download_audio(file_id, MAX_AUDIO_BYTES)
        mime = str(media.get("mime_type", "")).lower()
        suffix = ".ogg" if message.get("voice") or "ogg" in mime else ".mp3" if "mpeg" in mime else ".m4a" if "mp4" in mime else ".wav" if "wav" in mime else ".audio"
        with tempfile.TemporaryDirectory(prefix="fm-audio-") as temp_dir:
            audio_path = Path(temp_dir) / ("incoming" + suffix)
            audio_path.write_bytes(audio_bytes)
            result = transcribe_audio_local(audio_path, language="pt")
        transcript = result["text"].strip()
    except RuntimeError as exc:
        client.send(chat_id, f"Nao foi possivel processar o audio localmente: {exc} Nenhum registro foi criado.")
        return
    except Exception:
        client.send(chat_id, "Falha inesperada ao processar o audio. Nenhum registro foi criado.")
        return

    payload = parse_message(transcript)
    source = "telegram_voice"
    with session() as conn:
        event_id, inserted = create_inbound_event(
            conn, source=source, external_event_id=message_id,
            sender_id=str(sender_id), chat_id=str(chat_id),
            message_text=transcript, payload=payload,
        )
    if not inserted:
        client.send(chat_id, f"Esse audio ja foi processado (registro {event_id}); nao dupliquei a gravacao.")
        return
    if payload is None:
        client.send(chat_id, f"Transcricao local: \"{transcript[:1200]}\"\n\nNao consegui identificar um registro suportado com seguranca. Nada foi gravado. Voce pode enviar a informacao em texto usando /ajuda.")
        return
    client.send(
        chat_id,
        f"Transcricao local: \"{transcript[:1000]}\"\n\n"
        f"O que entendi:\n{_format_candidate(payload)}\n\n"
        f"Confirma o registro? Envie /confirmar {event_id}. Para descartar: /cancelar {event_id}.",
    )


def handle_message(client: TelegramClient, message: dict, allowed_user_id: int) -> None:
    sender = message.get('from') or {}
    chat = message.get('chat') or {}
    if chat.get('type') != 'private' or sender.get('id') != allowed_user_id:
        return
    if message.get("voice") or message.get("audio"):
        _handle_voice_message(client, message, int(sender["id"]), int(chat["id"]))
        return
    text = (message.get('text') or '').strip()
    if not text:
        client.send(chat['id'], 'Envie texto ou uma mensagem de voz. Imagens ainda nao sao processadas.')
        return

    if text == '/ajuda' or text == '/start':
        client.send(chat['id'], _help_text())
        return
    if text.startswith('/confirmar '):
        event_id = None
        try:
            event_id = int(text.split(None, 1)[1])
            with session() as conn:
                summary = confirm_event(conn, event_id)
            client.send(chat['id'], summary)
        except (ValueError, TypeError) as exc:
            client.send(chat['id'], str(exc))
        except sqlite3.IntegrityError:
            # A constraint failure must not poison Telegram polling forever.
            if event_id is not None:
                with session() as conn:
                    mark_event_error(conn, event_id)
            client.send(chat['id'], 'O registro violou uma regra de integridade e foi colocado em estado de erro. Nenhum dado foi salvo. Envie novamente com valores corrigidos.')
        return
    if text.startswith('/cancelar '):
        try:
            event_id = int(text.split(None, 1)[1])
            with session() as conn:
                reject_event(conn, event_id)
            client.send(chat['id'], f"Registro {event_id} cancelado. Nenhum dado fitness foi gravado.")
        except (ValueError, TypeError) as exc:
            client.send(chat['id'], str(exc))
        return
    if text.startswith('/perguntar '):
        question = text.split(None, 1)[1].strip()
        if not question:
            client.send(chat['id'], 'Informe a pergunta depois de /perguntar.')
            return
        try:
            answer = ask_local_model(question, _context_summary())
            client.send(chat['id'], answer)
        except RuntimeError as exc:
            client.send(chat['id'], str(exc) + '\nNenhum provedor remoto sera chamado automaticamente.')
        return
    if text == '/status':
        with session() as conn:
            pending = conn.execute("SELECT COUNT(*) FROM integration_events WHERE status='pending'").fetchone()[0]
            count = conn.execute("SELECT COUNT(*) FROM integration_events WHERE source='telegram'").fetchone()[0]
        client.send(chat['id'], f"Gateway ativo. Mensagens recebidas: {count}. Registros aguardando confirmacao: {pending}. Banco: {DB_PATH}")
        return

    payload = _command_payload(text) if text.startswith('/') else parse_message(text)
    if payload is None:
        with session() as conn:
            event_id, _ = create_inbound_event(conn, source='telegram', external_event_id=str(message.get('message_id')), sender_id=str(sender['id']), chat_id=str(chat['id']), message_text=text, payload=None)
        client.send(chat['id'], f"Nao consegui classificar essa mensagem com seguranca. Nada foi registrado. Use /ajuda. Referencia local: {event_id}.")
        return

    with session() as conn:
        event_id, inserted = create_inbound_event(conn, source='telegram', external_event_id=str(message.get('message_id')), sender_id=str(sender['id']), chat_id=str(chat['id']), message_text=text, payload=payload)
    if not inserted:
        client.send(chat['id'], f"Essa mensagem ja foi recebida (registro {event_id}); nao dupliquei a gravacao. Se estiver pendente, confirme com /confirmar {event_id} ou descarte com /cancelar {event_id}.")
        return
    client.send(chat['id'], f"Identifiquei:\n{_format_candidate(payload)}\n\nConfirma o registro? Envie /confirmar {event_id}. Para descartar: /cancelar {event_id}.")


def process_updates(client: TelegramClient, updates: list[dict], allowed_user_id: int, offset: int | None) -> int | None:
    """Process each Telegram update independently and advance past poison messages.

    Event writes are idempotent, so replay after a process restart is safe.
    Offset persistence failures are logged; the in-memory offset still advances.
    """
    for update in updates:
        update_id = int(update['update_id'])
        message = update.get('message')
        try:
            if message:
                handle_message(client, message, allowed_user_id)
        except Exception as exc:
            # Do not log message contents, tokens, or health payloads.
            print(f"Telegram update {update_id} failed: {type(exc).__name__}", file=sys.stderr)
            sender = (message or {}).get('from') or {}
            chat = (message or {}).get('chat') or {}
            if chat.get('type') == 'private' and sender.get('id') == allowed_user_id:
                try:
                    client.send(chat['id'], 'Nao consegui processar esta mensagem. O erro foi isolado e as proximas mensagens continuarao sendo processadas.')
                except Exception:
                    pass
        finally:
            offset = update_id + 1
            try:
                with session() as conn:
                    save_offset(conn, 'telegram_update_offset', str(offset))
            except Exception as exc:
                # Keep the in-memory offset moving; a restart may replay, and
                # the ingestion unique key prevents duplicate health records.
                print(f"Telegram offset persistence failed: {type(exc).__name__}", file=sys.stderr)
    return offset


def main() -> int:
    token = os.environ.get('FITNESS_MANAGER_TELEGRAM_BOT_TOKEN', '').strip()
    allowed = os.environ.get('FITNESS_MANAGER_TELEGRAM_ALLOWED_USER_ID', '').strip()
    if not token and sys.stdin.isatty():
        token = getpass.getpass('Telegram bot token (entrada oculta): ').strip()
    if not allowed and sys.stdin.isatty():
        allowed = input('Seu Telegram numeric user ID: ').strip()
    if not token or not allowed:
        print('Defina FITNESS_MANAGER_TELEGRAM_BOT_TOKEN e FITNESS_MANAGER_TELEGRAM_ALLOWED_USER_ID, ou execute em terminal interativo.', file=sys.stderr)
        return 2
    try:
        allowed_user_id = int(allowed)
    except ValueError:
        print('FITNESS_MANAGER_TELEGRAM_ALLOWED_USER_ID deve ser numerico.', file=sys.stderr)
        return 2

    initialize()
    client = TelegramClient(token)
    with session() as conn:
        offset = get_offset(conn, 'telegram_update_offset')
    print('Fitness Manager Telegram Gateway iniciado. Ctrl+C para encerrar.')
    while True:
        try:
            polling_args = {'timeout': 25, 'allowed_updates': ['message']}
            if offset is not None:
                polling_args['offset'] = offset
            updates = client.call('getUpdates', polling_args, timeout=40)
            offset = process_updates(client, updates, allowed_user_id, offset)
        except KeyboardInterrupt:
            print('\nGateway encerrado.')
            return 0
        except Exception as exc:
            # Never print token-bearing URLs or message bodies.
            print(f"Gateway error: {type(exc).__name__}: {exc}", file=sys.stderr)
            time.sleep(5)


if __name__ == '__main__':
    raise SystemExit(main())
