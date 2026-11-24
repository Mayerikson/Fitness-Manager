#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(command -v python3 || command -v python)"
SCRIPT="$ROOT/scripts/fitness_manager.py"
CRON_LINE="0 20 * * * $PYTHON '$SCRIPT' backup >/dev/null 2>&1"
( crontab -l 2>/dev/null | grep -Fv "$SCRIPT" || true; echo "$CRON_LINE" ) | crontab -
echo "Backup diário agendado para 20:00."
echo "Confirme a configuração do diretório Google Drive sincronizado antes do próximo backup."
