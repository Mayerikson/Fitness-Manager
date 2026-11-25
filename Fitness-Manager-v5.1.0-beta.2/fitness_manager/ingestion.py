"""Deterministic message ingestion with explicit confirmation and idempotency."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import date
from typing import Any


def _number(value: str) -> float:
    return float(value.replace(',', '.'))


def _normalize_spoken_numbers(text: str) -> str:
    """Normalize a bounded Portuguese number vocabulary for deterministic parsing."""
    import re

    units = {
        "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3,
        "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
        "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12,
        "treze": 13, "catorze": 14, "quatorze": 14, "quinze": 15,
        "dezesseis": 16, "dezasseis": 16, "dezessete": 17,
        "dezoito": 18, "dezenove": 19,
    }
    tens = {"vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50,
            "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90}
    phrases: dict[str, int] = {"cento": 100, "cem": 100}
    for word, value in units.items():
        phrases[word] = value
    for word, value in tens.items():
        phrases[word] = value
        for unit_word, unit_value in units.items():
            if 1 <= unit_value <= 9:
                phrases[f"{word} e {unit_word}"] = value + unit_value
    hundreds = {"duzentos": 200, "trezentos": 300, "quatrocentos": 400,
                "quinhentos": 500, "seiscentos": 600, "setecentos": 700,
                "oitocentos": 800, "novecentos": 900}
    for word, value in hundreds.items():
        phrases[word] = value
        for tens_word, tens_value in tens.items():
            phrases[f"{word} e {tens_word}"] = value + tens_value
            for unit_word, unit_value in units.items():
                if 1 <= unit_value <= 9:
                    phrases[f"{word} e {tens_word} e {unit_word}"] = value + tens_value + unit_value
        for unit_word, unit_value in units.items():
            if 1 <= unit_value <= 9:
                phrases[f"{word} e {unit_word}"] = value + unit_value
    phrases["cento e onze"] = 111
    phrases["cento e oito"] = 108
    phrases["cento e doze"] = 112

    normalized = text.lower().replace("vírgula", " virgula ").replace("virgula", " virgula ")
    for phrase, value in sorted(phrases.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = r"(?<![\w])" + re.escape(phrase) + r"(?![\w])"
        normalized = re.sub(pattern, str(value), normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(?<=\d)\s+virgula\s+(?=\d)", ",", normalized)
    return normalized


def parse_message(text: str) -> dict[str, Any] | None:
    """Parse a deliberately small, explicit Portuguese command vocabulary.

    Unknown or ambiguous messages return None and are never written as health data.
    Supported examples:
      peso 72,4 kg | cintura 83 cm
      corrida 4 km 42 min
      treino A;Supino reto;3;12;20
      alimento almoco;arroz;150
    """
    raw = _normalize_spoken_numbers(text.strip())
    if not raw or raw.startswith('/'):
        return None

    # Natural-language variants intentionally remain narrow and deterministic.
    m = re.fullmatch(r"(?i)(?:hoje\s+)?(?:estou\s+com|meu\s+peso(?:\s+atual)?\s+(?:e|é)|peso\s+atual(?:\s+e|é)?)\s*(\d+(?:[.,]\d+)?)\s*(?:kg|quilos?)", raw)
    if m:
        value = _number(m.group(1))
        if value <= 0:
            return None
        return {"type": "measurement", "kind": "weight", "value": value, "unit": "kg", "date": date.today().isoformat(), "source": "user_reported"}

    m = re.fullmatch(r"(?i)(?:minha\s+cintura\s+(?:e|é|esta|está)|medi\s+(?:a\s+)?cintura(?:\s+e|é)?)\s*(\d+(?:[.,]\d+)?)\s*(?:cm|centimetros?)", raw)
    if m:
        value = _number(m.group(1))
        if value <= 0:
            return None
        return {"type": "measurement", "kind": "waist", "value": value, "unit": "cm", "date": date.today().isoformat(), "method": "horizontal at navel", "source": "user_reported"}

    m = re.fullmatch(r"(?i)(?:hoje\s+)?(?:corri|fiz\s+uma\s+corrida\s+de)\s*(\d+(?:[.,]\d+)?)\s*(?:km|quilometros?)\s+(?:em|por)\s+(\d+(?:[.,]\d+)?)\s*(?:min|minutos)", raw)
    if m:
        distance, minutes = _number(m.group(1)), _number(m.group(2))
        if 0 < distance <= 15 and minutes > 0:
            return {"type": "run", "distance_km": distance, "duration_min": minutes, "date": date.today().isoformat(), "source": "user_reported"}
        return None

    m = re.fullmatch(r"(?i)(?:peso|pesagem)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*(?:kg)?", raw)
    if m:
        value = _number(m.group(1))
        if value <= 0:
            return None
        return {"type": "measurement", "kind": "weight", "value": value, "unit": "kg", "date": date.today().isoformat(), "source": "telegram"}

    m = re.fullmatch(r"(?i)(?:cintura|circunferencia da cintura)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*(?:cm)?", raw)
    if m:
        value = _number(m.group(1))
        if value <= 0:
            return None
        return {"type": "measurement", "kind": "waist", "value": value, "unit": "cm", "date": date.today().isoformat(), "method": "horizontal at navel", "source": "telegram"}

    m = re.fullmatch(r"(?i)(?:corrida|corri|run)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*km\s*(?:em|,|/)\s*(\d+(?:[.,]\d+)?)\s*(?:min|minutos)", raw)
    if m:
        distance = _number(m.group(1))
        minutes = _number(m.group(2))
        if distance <= 0 or distance > 15 or minutes <= 0:
            return None
        return {"type": "run", "distance_km": distance, "duration_min": minutes, "date": date.today().isoformat(), "source": "telegram"}

    m = re.fullmatch(
        r"(?i)(?:hoje\s+)?fiz\s+(.{2,80}?)[,;]?\s*(\d{1,2})\s+s[eé]ries?\s+(?:de\s+)?(\d{1,3})"
        r"(?:\s+repeti[cç][oõ]es?)?[,;]?\s+(?:usando|com)\s+(\d+(?:[.,]\d+)?)\s*(?:kg|quilos?)"
        r"(?:\s+em\s+cada\s+(?:m[aã]o|halter|haltere))?",
        raw,
    )
    if m:
        exercise, sets, reps, load = m.groups()
        if int(sets) <= 0 or int(reps) <= 0:
            return None
        return {
            "type": "workout", "session": "livre", "exercise": exercise.strip(),
            "sets": int(sets), "reps": int(reps), "load_kg": _number(load),
            "date": date.today().isoformat(), "source": "user_reported",
            "notes": "Carga informada por halter/mao; confirmar unidade e equipamento" if "halter" in raw.lower() or "mão" in raw.lower() or "mao" in raw.lower() else None,
        }

    m = re.fullmatch(r"(?i)treino\s*[:=]?\s*([^;]{1,30});\s*([^;]{1,100});\s*(\d{1,2});\s*(\d{1,3});\s*(\d+(?:[.,]\d+)?)", raw)
    if m:
        session_name, exercise, sets, reps, load = m.groups()
        if int(sets) <= 0 or int(reps) <= 0:
            return None
        return {"type": "workout", "session": session_name.strip(), "exercise": exercise.strip(), "sets": int(sets), "reps": int(reps), "load_kg": _number(load), "date": date.today().isoformat(), "source": "telegram"}

    m = re.fullmatch(r"(?i)alimento\s*[:=]?\s*([^;]{1,30});\s*([^;]{1,100});\s*(\d+(?:[.,]\d+)?)", raw)
    if m:
        meal, food, quantity = m.groups()
        quantity_g = _number(quantity)
        if quantity_g <= 0:
            return None
        return {"type": "food", "meal": meal.strip(), "food": food.strip(), "quantity_g": quantity_g, "date": date.today().isoformat(), "source": "telegram"}

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
