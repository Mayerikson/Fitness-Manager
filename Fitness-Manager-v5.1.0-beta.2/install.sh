#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$(pwd)"
CLAUDE=false
CODEX=false
QWEN=false
GROK=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) CLAUDE=true; shift ;;
    --codex) CODEX=true; shift ;;
    --qwen) QWEN=true; shift ;;
    --grok) GROK=true; shift ;;
    --all) CLAUDE=true; CODEX=true; QWEN=true; GROK=true; shift ;;
    --project) PROJECT_PATH="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: bash install.sh [--claude] [--codex] [--qwen] [--grok] [--all] [--project PATH]"
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

if ! $CLAUDE && ! $CODEX && ! $QWEN && ! $GROK; then
  echo "Select at least one target: --claude, --codex, --qwen, --grok or --all" >&2
  exit 2
fi

install_to() {
  local target="$1"
  mkdir -p "$(dirname "$target")"
  if [[ -e "$target" ]]; then
    local stamp backup
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    backup="${target}.backup-${stamp}"
    cp -a "$target" "$backup"
    echo "Existing installation backed up to: $backup"
  fi
  mkdir -p "$target"
  cp "$ROOT/SKILL.md" "$target/SKILL.md"
  if [[ -f "$ROOT/requirements-backup-encryption.txt" ]]; then cp "$ROOT/requirements-backup-encryption.txt" "$target/requirements-backup-encryption.txt"; fi
  for dir in agents workflows governance references fitness_manager scripts docs; do
    if [[ -d "$ROOT/$dir" ]]; then
      rm -rf "$target/$dir"
      cp -a "$ROOT/$dir" "$target/$dir"
    fi
  done
  echo "Installed Fitness Manager: $target"
}

if $CLAUDE; then install_to "$PROJECT_PATH/.claude/skills/fitness-manager"; fi
if $CODEX; then install_to "$PROJECT_PATH/.agents/skills/fitness-manager"; fi
if $QWEN; then install_to "$PROJECT_PATH/.qwen/skills/fitness-manager"; fi
if $GROK; then install_to "$PROJECT_PATH/.grok/skills/fitness-manager"; fi
