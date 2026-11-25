"""Optional fully local speech-to-text adapter using faster-whisper.

Audio is read from a caller-managed temporary file and is never persisted here.
The first model use may download model weights; subsequent transcription can run
offline when the model is cached locally.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

MAX_AUDIO_BYTES = 15 * 1024 * 1024
MAX_AUDIO_SECONDS = 300


@lru_cache(maxsize=2)
def _load_model(model_name: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Transcricao local indisponivel. Instale as dependencias opcionais com "
            "pip install -r requirements-audio.txt."
        ) from exc
    device = os.environ.get("FITNESS_MANAGER_WHISPER_DEVICE", "cpu")
    compute_type = os.environ.get("FITNESS_MANAGER_WHISPER_COMPUTE_TYPE", "int8")
    try:
        return WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as exc:
        raise RuntimeError(
            "Nao foi possivel carregar o modelo Whisper local. Verifique o nome/caminho, "
            "o cache do modelo e os recursos do computador."
        ) from exc


def transcribe_audio_local(audio_path: str | Path, language: str = "pt") -> dict:
    """Transcribe audio locally; return text and safe metadata, never the audio bytes."""
    path = Path(audio_path)
    if not path.is_file():
        raise RuntimeError("Arquivo de audio temporario nao encontrado.")
    size = path.stat().st_size
    if size <= 0 or size > MAX_AUDIO_BYTES:
        raise RuntimeError("Audio vazio ou acima do limite de 15 MB.")

    model_name = os.environ.get("FITNESS_MANAGER_WHISPER_MODEL", "base")
    model = _load_model(model_name)
    try:
        segments, info = model.transcribe(
            str(path),
            language=language,
            vad_filter=True,
            beam_size=3,
            condition_on_previous_text=False,
        )
        parts = []
        for segment in segments:
            if segment.end > MAX_AUDIO_SECONDS:
                raise RuntimeError("Audio acima do limite de 5 minutos.")
            text = str(segment.text).strip()
            if text:
                parts.append(text)
        transcript = " ".join(parts).strip()
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Falha na transcricao local do audio.") from exc

    if not transcript:
        raise RuntimeError("Nao foi possivel reconhecer fala no audio.")
    return {
        "text": transcript[:4000],
        "language": getattr(info, "language", language),
        "duration_sec": min(float(getattr(info, "duration", 0.0) or 0.0), MAX_AUDIO_SECONDS),
        "engine": "faster-whisper-local",
        "model": model_name,
    }
