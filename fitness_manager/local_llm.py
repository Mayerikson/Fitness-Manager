"""Optional loopback-only OpenAI-compatible local model adapter."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlparse


def ask_local_model(question: str, context: str = "") -> str:
    base = os.environ.get("FITNESS_MANAGER_LOCAL_LLM_URL", "").strip().rstrip("/")
    model = os.environ.get("FITNESS_MANAGER_LOCAL_LLM_MODEL", "").strip()
    if not base or not model:
        raise RuntimeError("Modelo local nao configurado. Defina FITNESS_MANAGER_LOCAL_LLM_URL e FITNESS_MANAGER_LOCAL_LLM_MODEL.")
    parsed = urlparse(base)
    if (parsed.scheme not in {"http", "https"} or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise RuntimeError("Por seguranca, use um endpoint local sem credenciais, query ou fragmento (localhost/127.0.0.1).")
    url = base if base.endswith("/chat/completions") else base + "/chat/completions"
    messages = [
        {"role": "system", "content": "Voce e um assistente de acompanhamento fitness. Diferencie fatos, estimativas e incertezas. Nao diagnostique nem altere planos sem aprovacao. Contexto local fornecido pelo usuario: " + context[:5000]},
        {"role": "user", "content": question[:3000]},
    ]
    body = json.dumps({"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 700}).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("Nao foi possivel consultar o modelo local. Verifique se Ollama/LM Studio esta ativo.") from exc
    try:
        return str(data["choices"][0]["message"]["content"]).strip()[:3500]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Resposta inesperada do endpoint local.") from exc
