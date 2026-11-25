"""Deterministic message ingestion with explicit confirmation and idempotency."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import date
from typing import Any


def _number(value: str) -> float:
    return float(value.replace(',', '.'))


def parse_message(text: str) -> dict[str, Any] | None:
    """Parse a deliberately small, explicit Portuguese command vocabulary.

    Unknown or ambiguous messages return None and are never written as health data.
    Supported examples:
      peso 111,4 kg | cintura 108 cm
      corrida 4 km 42 min
      treino A;Supino reto;3;12;20
      alimento almoco;arroz;150
    """
    raw = text.strip()
    if not raw or raw.startswith('/'):
        return None

    m = re.fullmatch(r"(?i)(?:peso|pesagem)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*(?:kg)?", raw)
    if m:
        return {"type": "measurement", "kind": "weight", "value": _number(m.group(1)), "unit": "kg", "date": date.today().isoformat(), "source": "telegram"}

    m = re.fullmatch(r"(?i)(?:cintura|circunferencia da cintura)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*(?:cm)?", raw)
    if m:
        return {"type": "measurement", "kind": "waist", "value": _number(m.group(1)), "unit": "cm", "date": date.today().isoformat(), "method": "horizontal at navel", "source": "telegram"}

    m = re.fullmatch(r"(?i)(?:corrida|corri|run)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*km\s*(?:em|,|/)\s*(\d+(?:[.,]\d+)?)\s*(?:min|minutos)", raw)
    if m:
        distance = _number(m.group(1))
        minutes = _number(m.group(2))
        if distance <= 0 or distance > 15 or minutes <= 0:
            return None
        return {"type": "run", "distance_km": distance, "duration_min": minutes, "date": date.today().isoformat(), "source": "telegram"}

    m = re.fullmatch(r"(?i)treino\s*[:=]?\s*([^;]{1,30});\s*([^;]{1,100});\s*(\d{1,2});\s*(\d{1,3});\s*(\d+(?:[.,]\d+)?)", raw)
    if m:
        session_name, exercise, sets, reps, load = m.groups()
        return {"type": "workout", "session": session_name.strip(), "exercise": exercise.strip(), "sets": int(sets), "reps": int(reps), "load_kg": _number(load), "date": date.today().isoformat(), "source": "telegram"}

    m = re.fullmatch(r"(?i)alimento\s*[:=]?\s*([^;]{1,30});\s*([^;]{1,100});\s*(\d+(?:[.,]\d+)?)", raw)
    if m:
        meal, food, quantity = m.groups()
        return {"type": "food", "meal": meal.strip(), "food": food.strip(), "quantity_g": _number(quantity), "date": date.today().isoformat(), "source": "telegram"}

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
        "SELECT payload_json,status FROM integration_events WHERE id=?", (event_id,)
    ).fetchone()
    if not row:
        raise ValueError("Registro pendente nao encontrado.")
    if row["status"] != "pending" or not row["payload_json"]:
        raise ValueError("Esse registro nao esta pendente de confirmacao.")
    payload = json.loads(row["payload_json"])
    kind = payload["type"]
    if kind == "measurement":
        cur = conn.execute(
            "INSERT INTO measurements(measured_at,kind,value,unit,method,source) VALUES(?,?,?,?,?,?)",
            (payload["date"], payload["kind"], payload["value"], payload["unit"], payload.get("method"), "telegram"),
        )
        summary = f"Medida registrada: {payload['kind']} {payload['value']} {payload['unit']} (ID {cur.lastrowid})."
    elif kind == "run":
        duration_sec = int(round(payload["duration_min"] * 60))
        pace = duration_sec / payload["distance_km"]
        cur = conn.execute(
            "INSERT INTO runs(performed_at,distance_km,duration_sec,pace_sec_per_km,notes) VALUES(?,?,?,?,?)",
            (payload["date"], payload["distance_km"], duration_sec, pace, "Registrado via Telegram"),
        )
        summary = f"Corrida registrada: {payload['distance_km']} km em {payload['duration_min']} min (ID {cur.lastrowid})."
    elif kind == "workout":
        cur = conn.execute(
            "INSERT INTO workout_sessions(performed_at,session_name,notes) VALUES(?,?,?)",
            (payload["date"], payload["session"], "Registrado via Telegram"),
        )
        session_id = cur.lastrowid
        entry = conn.execute(
            "INSERT INTO workout_entries(session_id,exercise,sets,reps,load_kg,notes) VALUES(?,?,?,?,?,?)",
            (session_id, payload["exercise"], payload["sets"], payload["reps"], payload["load_kg"], "Registrado via Telegram"),
        )
        summary = f"Treino registrado: {payload['exercise']}, {payload['sets']}x{payload['reps']}, {payload['load_kg']} kg (ID {entry.lastrowid})."
    elif kind == "food":
        cur = conn.execute(
            "INSERT INTO food_logs(consumed_at,meal,food,quantity_g,source,notes) VALUES(?,?,?,?,?,?)",
            (payload["date"], payload["meal"], payload["food"], payload["quantity_g"], "telegram", "Macros nao informados"),
        )
        summary = f"Alimento registrado: {payload['food']} {payload['quantity_g']} g (ID {cur.lastrowid}). Calorias e macros ficaram sem estimativa."
    else:
        raise ValueError("Tipo de registro nao suportado.")
    conn.execute(
        "UPDATE integration_events SET status='confirmed',processed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),result_record_id=? WHERE id=?",
        (cur.lastrowid, event_id),
    )
    return summary


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
