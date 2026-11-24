#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
NAME="fitness-manager"
usage(){ echo "Usage: $0 --claude|--qwen|--codex|--grok|--all [--project DIR]"; }
TARGETS=(); PROJECT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) TARGETS+=(claude);;
    --qwen) TARGETS+=(qwen);;
    --codex) TARGETS+=(codex);;
    --grok) TARGETS+=(grok);;
    --all) TARGETS+=(claude qwen codex grok);;
    --project) shift; PROJECT="${1:?project directory required}";;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1"; usage; exit 2;;
  esac
  shift
done
[[ ${#TARGETS[@]} -gt 0 ]] || { usage; exit 2; }
STAMP="$(date +%Y%m%d_%H%M%S)"
for t in "${TARGETS[@]}"; do
  case "$t" in
    claude) base=".claude/skills";;
    qwen|codex) base=".agents/skills";;
    grok) base=".grok/skills";;
  esac
  homebase="${PROJECT:-$HOME}"
  dest="$homebase/$base/$NAME"
  parent="$(dirname "$dest")"
  mkdir -p "$parent"
  stage="$dest.__staging_$STAMP"
  backup_root="$HOME/.fitness-manager-install-backups/$t"
  mkdir -p "$backup_root"
  backup="$backup_root/${NAME}_$STAMP"
  mkdir -p "$stage"
  cp -a "$ROOT/." "$stage/"
  if [[ -e "$dest" ]]; then mv "$dest" "$backup"; fi
  if mv "$stage" "$dest"; then
    echo "Installed $t -> $dest"
    [[ -e "$backup" ]] && echo "Previous installation preserved -> $backup"
  else
    [[ -e "$backup" && ! -e "$dest" ]] && mv "$backup" "$dest"
    rm -rf "$stage"
    exit 1
  fi
done
