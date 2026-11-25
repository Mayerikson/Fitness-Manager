"""Deterministic Portuguese message ingestion with confirmation and idempotency."""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from datetime import date
from typing import Any


_UNITS = {
    "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2,
    "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
    "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12,
    "treze": 13, "catorze": 14, "quatorze": 14, "quinze": 15,
    "dezesseis": 16, "dezasseis": 16, "dezessete": 17,
    "dezoito": 18, "dezenove": 19,
}
_TENS = {
    "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50,
    "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90,
}
_HUNDREDS = {
    "cento": 100, "cem": 100, "duzentos": 200, "trezentos": 300,
    "quatrocentos": 400, "quinhentos": 500, "seiscentos": 600,
    "setecentos": 700, "oitocentos": 800, "novecentos": 900,
}
_WORD_NUMBER = r"(?:zero|um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|catorze|quatorze|quinze|dezesseis|dezasseis|dezessete|dezoito|dezenove|vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa|cento|cem|duzentos|trezentos|quatrocentos|quinhentos|seiscentos|setecentos|oitocentos|novecentos)"
_SIMPLE_NUMBER = rf"(?:\d+(?:[.,]\d+)?|{_WORD_NUMBER}(?:\s+e\s+{_WORD_NUMBER}){{0,2}})"
# Spoken decimals: "setenta e dois virgula quatro", "72 virgula 4".
_NUMBER = rf"{_SIMPLE_NUMBER}(?:\s+virgula\s+{_SIMPLE_NUMBER})?"


def _fold_with_offsets(text: str) -> tuple[str, list[int]]:
    """Normalize Portuguese text and retain offsets into the original string.

    Diacritic removal can change string length. Keeping an offset map prevents
    exercise names such as "elevação pélvica" from being sliced incorrectly.
    """
    chars: list[str] = []
    offsets: list[int] = []
    for original_index, original_char in enumerate(text):
        decomposed = unicodedata.normalize("NFD", original_char.lower())
        for char in decomposed:
            if unicodedata.combining(char):
                continue
            if char.isspace():
                if chars and chars[-1] != " ":
                    chars.append(" ")
                    offsets.append(original_index)
            else:
                chars.append(char)
                offsets.append(original_index)

    # Match _fold's edge punctuation behavior while preserving source offsets.
    edge_punctuation = set(" \t\r\n.,;:!?\"'“”‘’()[]{}")
    start = 0
    end = len(chars)
    while start < end and chars[start] in edge_punctuation:
        start += 1
    while end > start and chars[end - 1] in edge_punctuation:
        end -= 1
    return "".join(chars[start:end]), offsets[start:end]


def _fold(text: str) -> str:
    """Lowercase, remove diacritics, trim edge punctuation and normalize spaces."""
    return _fold_with_offsets(text)[0]


def _number(value: str) -> float:
    value = _fold(value)
    if " virgula " in value:
        whole, _, fraction = value.partition(" virgula ")
        whole_number = _number(whole)
        # "zero cinco" is not supported; digits keep their leading zeros.
        digits = fraction if fraction.isdigit() else str(int(_number(fraction)))
        if not whole_number.is_integer():
            raise ValueError("Numero decimal invalido.")
        return float(f"{int(whole_number)}.{digits}")
    if re.fullmatch(r"\d+(?:[.,]\d+)?", value):
        return float(value.replace(",", "."))

    tokens = [token for token in value.split() if token != "e"]
    if not tokens or len(tokens) > 3:
        raise ValueError("Numero por extenso invalido.")

    total = 0
    index = 0
    if tokens[index] in _HUNDREDS:
        total += _HUNDREDS[tokens[index]]
        index += 1
    if index < len(tokens):
        token = tokens[index]
        if token in _TENS:
            total += _TENS[token]
            index += 1
            if index < len(tokens) and tokens[index] in _UNITS and 1 <= _UNITS[tokens[index]] <= 9:
                total += _UNITS[tokens[index]]
                index += 1
        elif token in _UNITS:
            total += _UNITS[token]
            index += 1
        else:
            raise ValueError("Numero por extenso invalido.")
    if index != len(tokens):
        raise ValueError("Numero por extenso invalido.")
    return float(total)


def _exercise_from_original(original: str, normalized_match: re.Match[str],
                            offsets: list[int], group: str = "exercise") -> str:
    """Recover the exercise label with original accents and exact source offsets."""
    start, end = normalized_match.span(group)
    if start >= end or end > len(offsets):
        return ""
    original_start = offsets[start]
    original_end = offsets[end - 1] + 1
    label = original[original_start:original_end].strip(" \t\r\n,;:.!?-\"'“”‘’")
    return re.sub(r"\s+", " ", label)


def _original_field(original: str, match: re.Match[str], offsets: list[int], group: str) -> str:
    """Return a command field exactly as typed (accents, case and punctuation)."""
    start, end = match.span(group)
    return original[offsets[start]:offsets[end - 1] + 1].strip()


def parse_message(text: str) -> dict[str, Any] | None:
    """Parse supported natural Portuguese records without an LLM.

    Parsing is intentionally conservative: unsupported or ambiguous text returns None.
    Number words are interpreted only inside numeric fields, never in exercise names.
    """
    raw = text.strip()
    normalized, source_offsets = _fold_with_offsets(raw)
    if not normalized or normalized.startswith("/"):
        return None
    today = date.today().isoformat()

    # Body weight: "peso 72 kg", "Peso 72 quilos.", "estou com 72 quilos",
    # and "meu peso e cento e quinze quilos".
    m = re.fullmatch(
        rf"(?:hoje\s+)?(?:peso|pesagem|estou\s+com|estou\s+pesando|"
        rf"meu\s+peso(?:\s+atual)?(?:\s+(?:e|esta))?)\s*[:=]?\s*"
        rf"(?P<value>{_NUMBER})\s*(?:kg|quilos?|quilogramas?)?",
        normalized,
    )
    if m:
        try:
            value = _number(m.group("value"))
        except ValueError:
            return None
        if not 0 < value <= 500:
            return None
        return {"type": "measurement", "kind": "weight", "value": value,
                "unit": "kg", "date": today, "source": "user_reported"}

    # Waist: supports common forms and spoken numbers.
    m = re.fullmatch(
        rf"(?:hoje\s+)?(?:cintura|circunferencia\s+da\s+cintura|"
        rf"minha\s+cintura(?:\s+(?:e|esta))?|medi\s+(?:a\s+)?cintura(?:\s+(?:e|esta))?)"
        rf"\s*[:=]?\s*(?P<value>{_NUMBER})\s*(?:cm|centimetros?)?",
        normalized,
    )
    if m:
        try:
            value = _number(m.group("value"))
        except ValueError:
            return None
        if not 0 < value <= 400:
            return None
        return {"type": "measurement", "kind": "waist", "value": value,
                "unit": "cm", "date": today, "method": "horizontal at navel",
                "source": "user_reported"}

    # Running: "corri 4 km em 30 minutos" and
    # "fiz uma corrida de quatro quilometros em trinta minutos".
    m = re.fullmatch(
        rf"(?:hoje\s+)?(?:corri|fiz\s+(?:uma\s+)?corrida\s+de|corrida\s+de|corrida)\s+"
        rf"(?P<distance>{_NUMBER})\s*(?:km|quilometros?)\s+(?:em|por)\s+"
        rf"(?P<minutes>{_NUMBER})\s*(?:min|minuto|minutos)",
        normalized,
    )
    if m:
        try:
            distance = _number(m.group("distance"))
            minutes = _number(m.group("minutes"))
        except ValueError:
            return None
        if 0 < distance <= 15 and 0 < minutes <= 1440:
            return {"type": "run", "distance_km": distance,
                    "duration_min": minutes, "date": today,
                    "source": "user_reported"}
        return None

    # Workout: preserve the original exercise label. Number conversion applies only
    # to sets, reps and load, so "rosca com um braco" remains an exercise name.
    m = re.fullmatch(
        rf"(?:hoje\s+)?fiz\s+(?P<exercise>.+?)[,;]\s*"
        rf"(?P<sets>{_NUMBER})\s+series\s+(?:de\s+)?"
        rf"(?P<reps>{_NUMBER})(?:\s+repeticoes?)?[,;]?\s+(?:com|usando)\s+"
        rf"(?P<load>{_NUMBER})\s*(?:kg|quilos?|quilogramas?)"
        rf"(?:\s+em\s+cada\s+(?:mao|halter|haltere))?",
        normalized,
    )
    if m:
        try:
            sets = int(_number(m.group("sets")))
            reps = int(_number(m.group("reps")))
            load = _number(m.group("load"))
        except ValueError:
            return None
        exercise = _exercise_from_original(raw, m, source_offsets)
        if not exercise or not (1 <= sets <= 30 and 1 <= reps <= 300 and 0 <= load <= 1000):
            return None
        folded_raw = _fold(raw)
        notes = "Carga informada por halter/mao; confirmar unidade e equipamento" if re.search(r"\b(?:halter|haltere|mao)\b", folded_raw) else None
        return {"type": "workout", "session": "livre", "exercise": exercise,
                "sets": sets, "reps": reps, "load_kg": load, "date": today,
                "source": "user_reported", "notes": notes}

    # Explicit semicolon commands remain supported for bot and CLI use.
    m = re.fullmatch(r"(?i)treino\s*[:=]?\s*(?P<session>[^;]{1,30});\s*(?P<exercise>[^;]{1,100});\s*(\d{1,2});\s*(\d{1,3});\s*(\d+(?:[.,]\d+)?)", normalized)
    if m:
        sets, reps, load = m.groups()[2:]
        session_name = _original_field(raw, m, source_offsets, "session")
        exercise = _original_field(raw, m, source_offsets, "exercise")
        if int(sets) <= 0 or int(reps) <= 0 or _number(load) < 0:
            return None
        return {"type": "workout", "session": session_name.strip(),
                "exercise": exercise.strip(), "sets": int(sets), "reps": int(reps),
                "load_kg": _number(load), "date": today, "source": "telegram"}

    m = re.fullmatch(r"(?i)alimento\s*[:=]?\s*(?P<meal>[^;]{1,30});\s*(?P<food>[^;]{1,100});\s*(\d+(?:[.,]\d+)?)", normalized)
    if m:
        quantity = m.groups()[2]
        meal = _original_field(raw, m, source_offsets, "meal")
        food = _original_field(raw, m, source_offsets, "food")
        quantity_g = _number(quantity)
        if quantity_g <= 0:
            return None
        return {"type": "food", "meal": meal.strip(), "food": food.strip(),
                "quantity_g": quantity_g, "date": today, "source": "telegram"}

    return None


def create_inbound_event(conn: sqlite3.Connection, *, source: str, external_event_id: str,
                         sender_id: str, chat_id: str, message_text: str,
                         payload: dict[str, Any] | None) -> tuple[int, bool]:
    """Insert once; duplicate external IDs return the original local event."""
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) if payload else None
    # Data minimization: unsupported free text is not retained in the health database.
    stored_text = message_text[:4000] if payload else "[unsupported input not retained]"
    cur = conn.execute(
        """INSERT OR IGNORE INTO integration_events
           (source,external_event_id,sender_id,chat_id,message_text,payload_json,status)
           VALUES(?,?,?,?,?,?,?)""",
        (source, str(external_event_id), str(sender_id), str(chat_id), stored_text, encoded,
         "pending" if payload else "unsupported"),
    )
    inserted = cur.rowcount == 1
    if inserted:
        return int(cur.lastrowid), True
    row = conn.execute(
        "SELECT id FROM integration_events WHERE source=? AND external_event_id=?",
        (source, str(external_event_id)),
    ).fetchone()
    return int(row[0]), False


def confirm_event(conn: sqlite3.Connection, event_id: int) -> str:
    """Atomically persist a pending parsed event. Returns a safe human summary."""
    row = conn.execute(
        "SELECT source,payload_json,status FROM integration_events WHERE id=?", (event_id,)
    ).fetchone()
    if not row:
        raise ValueError("Registro pendente nao encontrado.")
    if row["status"] != "pending" or not row["payload_json"]:
        raise ValueError("Esse registro nao esta pendente de confirmacao.")
    source = row["source"]
    payload = json.loads(row["payload_json"])
    kind = payload["type"]
    if kind == "measurement":
        cur = conn.execute(
            "INSERT INTO measurements(measured_at,kind,value,unit,method,source) VALUES(?,?,?,?,?,?)",
            (payload["date"], payload["kind"], payload["value"], payload["unit"], payload.get("method"), source),
        )
        summary = f"Medida registrada: {payload['kind']} {payload['value']} {payload['unit']} (ID {cur.lastrowid})."
    elif kind == "run":
        duration_sec = int(round(payload["duration_min"] * 60))
        pace = duration_sec / payload["distance_km"]
        cur = conn.execute(
            "INSERT INTO runs(performed_at,distance_km,duration_sec,pace_sec_per_km,notes) VALUES(?,?,?,?,?)",
            (payload["date"], payload["distance_km"], duration_sec, pace, f"Registrado via {source}"),
        )
        summary = f"Corrida registrada: {payload['distance_km']} km em {payload['duration_min']} min (ID {cur.lastrowid})."
    elif kind == "workout":
        cur = conn.execute(
            "INSERT INTO workout_sessions(performed_at,session_name,notes) VALUES(?,?,?)",
            (payload["date"], payload["session"], f"Registrado via {source}"),
        )
        session_id = cur.lastrowid
        entry = conn.execute(
            "INSERT INTO workout_entries(session_id,exercise,sets,reps,load_kg,notes) VALUES(?,?,?,?,?,?)",
            (session_id, payload["exercise"], payload["sets"], payload["reps"], payload["load_kg"], payload.get("notes") or f"Registrado via {source}"),
        )
        summary = f"Treino registrado: {payload['exercise']}, {payload['sets']}x{payload['reps']}, {payload['load_kg']} kg (ID {entry.lastrowid})."
    elif kind == "food":
        cur = conn.execute(
            "INSERT INTO food_logs(consumed_at,meal,food,quantity_g,source,notes) VALUES(?,?,?,?,?,?)",
            (payload["date"], payload["meal"], payload["food"], payload["quantity_g"], source, "Macros nao informados"),
        )
        summary = f"Alimento registrado: {payload['food']} {payload['quantity_g']} g (ID {cur.lastrowid}). Calorias e macros ficaram sem estimativa."
    else:
        raise ValueError("Tipo de registro nao suportado.")
    conn.execute(
        "UPDATE integration_events SET status='confirmed',processed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),result_record_id=? WHERE id=?",
        (cur.lastrowid, event_id),
    )
    return summary


def mark_event_error(conn: sqlite3.Connection, event_id: int) -> None:
    """Move a poison/invalid pending event to a terminal error state."""
    cur = conn.execute(
        "UPDATE integration_events SET status='error',processed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=? AND status='pending'",
        (event_id,),
    )
    if cur.rowcount != 1:
        raise ValueError("Registro pendente nao encontrado ou ja processado.")


def reject_event(conn: sqlite3.Connection, event_id: int) -> None:
    cur = conn.execute(
        "UPDATE integration_events SET status='rejected',processed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=? AND status='pending'",
        (event_id,),
    )
    if cur.rowcount != 1:
        raise ValueError("Registro pendente nao encontrado ou ja processado.")


def save_offset(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO integration_state(state_key,state_value) VALUES(?,?) ON CONFLICT(state_key) DO UPDATE SET state_value=excluded.state_value,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')",
        (key, value),
    )


def get_offset(conn: sqlite3.Connection, key: str) -> int | None:
    row = conn.execute("SELECT state_value FROM integration_state WHERE state_key=?", (key,)).fetchone()
    return int(row[0]) if row else None
