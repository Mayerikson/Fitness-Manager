#!/usr/bin/env python3
"""Print the sender ID from private Telegram updates without displaying message text."""
from __future__ import annotations

import getpass
import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    token = os.environ.get('FITNESS_MANAGER_TELEGRAM_BOT_TOKEN', '').strip()
    if not token and sys.stdin.isatty():
        token = getpass.getpass('Telegram bot token (entrada oculta): ').strip()
    if not token:
        print('Defina FITNESS_MANAGER_TELEGRAM_BOT_TOKEN ou execute em terminal interativo.', file=sys.stderr)
        return 2
    url = f'https://api.telegram.org/bot{token}/getUpdates'
    payload = json.dumps({'timeout': 5, 'limit': 20, 'allowed_updates': ['message']}).encode('utf-8')
    request = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            result = json.loads(response.read().decode('utf-8'))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f'Falha ao consultar Telegram: {type(exc).__name__}', file=sys.stderr)
        return 2
    if not result.get('ok'):
        print('Telegram nao confirmou a consulta. Verifique token e webhook configurado.', file=sys.stderr)
        return 2
    found = set()
    for update in result.get('result', []):
        message = update.get('message') or {}
        chat = message.get('chat') or {}
        sender = message.get('from') or {}
        if chat.get('type') == 'private' and sender.get('id') is not None:
            found.add(int(sender['id']))
    if not found:
        print('Nenhuma mensagem privada pendente. Envie /start ao seu bot e execute novamente.')
        return 1
    for user_id in sorted(found):
        print(user_id)
    print('Use o ID correspondente a sua conta em FITNESS_MANAGER_TELEGRAM_ALLOWED_USER_ID.')
    print('O script nao exibe nem armazena o conteudo das mensagens.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
