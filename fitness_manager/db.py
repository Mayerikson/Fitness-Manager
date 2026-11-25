"""SQLite persistence for Fitness Manager. Standard-library only."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

APP_DIR = Path(os.environ.get("FITNESS_MANAGER_HOME", Path.home() / ".fitness-manager")).expanduser()
DB_PATH = Path(os.environ.get("FITNESS_MANAGER_DB", APP_DIR / "fitness_manager.sqlite")).expanduser()

SCHEMA_VERSION = 2

SCHEMA = r"""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    sex TEXT,
    age_years INTEGER CHECK(age_years IS NULL OR (age_years >= 18 AND age_years <= 120)),
    height_cm REAL CHECK(height_cm IS NULL OR (height_cm >= 80 AND height_cm <= 250)),
    goals_json TEXT NOT NULL DEFAULT '[]',
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measured_at TEXT NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('weight','waist','abdomen','hip','chest','arm_left','arm_right','thigh_left','thigh_right','other')),
    value REAL NOT NULL CHECK(value > 0),
    unit TEXT NOT NULL,
    method TEXT,
    source TEXT NOT NULL DEFAULT 'user_reported',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_measurements_kind_date ON measurements(kind, measured_at DESC);

CREATE TABLE IF NOT EXISTS food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consumed_at TEXT NOT NULL,
    meal TEXT NOT NULL,
    food TEXT NOT NULL,
    quantity_g REAL CHECK(quantity_g IS NULL OR quantity_g > 0),
    kcal REAL CHECK(kcal IS NULL OR kcal >= 0),
    protein_g REAL CHECK(protein_g IS NULL OR protein_g >= 0),
    carbs_g REAL CHECK(carbs_g IS NULL OR carbs_g >= 0),
    fat_g REAL CHECK(fat_g IS NULL OR fat_g >= 0),
    preparation TEXT,
    source TEXT NOT NULL DEFAULT 'user_reported',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_food_logs_date ON food_logs(consumed_at DESC);

CREATE TABLE IF NOT EXISTS workout_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    performed_at TEXT NOT NULL,
    session_name TEXT NOT NULL,
    duration_min REAL CHECK(duration_min IS NULL OR duration_min > 0),
    rpe REAL CHECK(rpe IS NULL OR (rpe >= 1 AND rpe <= 10)),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_workout_sessions_date ON workout_sessions(performed_at DESC);

CREATE TABLE IF NOT EXISTS workout_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE RESTRICT,
    exercise TEXT NOT NULL,
    sets INTEGER NOT NULL CHECK(sets > 0),
    reps INTEGER NOT NULL CHECK(reps > 0),
    load_kg REAL CHECK(load_kg IS NULL OR load_kg >= 0),
    rir REAL CHECK(rir IS NULL OR (rir >= 0 AND rir <= 10)),
    substitution_for TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_workout_entries_session ON workout_entries(session_id);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    performed_at TEXT NOT NULL,
    distance_km REAL NOT NULL CHECK(distance_km > 0 AND distance_km <= 15),
    duration_sec INTEGER NOT NULL CHECK(duration_sec > 0),
    pace_sec_per_km REAL NOT NULL CHECK(pace_sec_per_km > 0),
    rpe REAL CHECK(rpe IS NULL OR (rpe >= 1 AND rpe <= 10)),
    avg_hr INTEGER CHECK(avg_hr IS NULL OR (avg_hr > 0 AND avg_hr < 260)),
    terrain TEXT,
    symptoms TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_runs_date ON runs(performed_at DESC);

CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checked_at TEXT NOT NULL,
    sleep_hours REAL CHECK(sleep_hours IS NULL OR (sleep_hours >= 0 AND sleep_hours <= 24)),
    recovery INTEGER CHECK(recovery IS NULL OR (recovery BETWEEN 1 AND 10)),
    soreness INTEGER CHECK(soreness IS NULL OR (soreness BETWEEN 1 AND 10)),
    energy INTEGER CHECK(energy IS NULL OR (energy BETWEEN 1 AND 10)),
    symptoms TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS plan_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decided_at TEXT NOT NULL,
    domain TEXT NOT NULL CHECK(domain IN ('training','nutrition','running','general')),
    current_plan TEXT,
    proposed_plan TEXT NOT NULL,
    evidence TEXT NOT NULL,
    rationale TEXT NOT NULL,
    uncertainty TEXT,
    approval_status TEXT NOT NULL DEFAULT 'proposed' CHECK(approval_status IN ('proposed','approved','rejected','implemented','reverted')),
    review_date TEXT,
    outcome TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    action TEXT NOT NULL,
    record_id INTEGER,
    occurred_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS integration_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    external_event_id TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    message_text TEXT NOT NULL,
    payload_json TEXT,
    status TEXT NOT NULL CHECK(status IN ('pending','unsupported','confirmed','rejected','error')),
    result_record_id INTEGER,
    received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    processed_at TEXT,
    UNIQUE(source, external_event_id)
);
CREATE INDEX IF NOT EXISTS idx_integration_events_status ON integration_events(status, received_at DESC);

CREATE TABLE IF NOT EXISTS integration_state (
    state_key TEXT PRIMARY KEY,
    state_value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TRIGGER IF NOT EXISTS audit_profile_insert AFTER INSERT ON profile BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('profile','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_profile_update AFTER UPDATE ON profile BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('profile','UPDATE',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_measurements_insert AFTER INSERT ON measurements BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('measurements','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_food_insert AFTER INSERT ON food_logs BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('food_logs','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_workout_session_insert AFTER INSERT ON workout_sessions BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('workout_sessions','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_workout_entry_insert AFTER INSERT ON workout_entries BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('workout_entries','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_runs_insert AFTER INSERT ON runs BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('runs','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_checkins_insert AFTER INSERT ON checkins BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('checkins','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_plan_decisions_insert AFTER INSERT ON plan_decisions BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('plan_decisions','INSERT',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_integration_events_insert AFTER INSERT ON integration_events BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('integration_events','RECEIVE',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_integration_events_update AFTER UPDATE ON integration_events BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('integration_events','STATUS',NEW.id);
END;
CREATE TRIGGER IF NOT EXISTS audit_checkins_insert AFTER INSERT ON checkins BEGIN
  INSERT INTO audit_log(table_name,action,record_id) VALUES('checkins','INSERT',NEW.id);
END;

-- Historical event records are append-only. Corrections are new records with notes.
CREATE TRIGGER IF NOT EXISTS immutable_measurements_update BEFORE UPDATE ON measurements BEGIN SELECT RAISE(ABORT,'measurements are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_measurements_delete BEFORE DELETE ON measurements BEGIN SELECT RAISE(ABORT,'measurements are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_food_update BEFORE UPDATE ON food_logs BEGIN SELECT RAISE(ABORT,'food logs are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_food_delete BEFORE DELETE ON food_logs BEGIN SELECT RAISE(ABORT,'food logs are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_runs_update BEFORE UPDATE ON runs BEGIN SELECT RAISE(ABORT,'runs are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_runs_delete BEFORE DELETE ON runs BEGIN SELECT RAISE(ABORT,'runs are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_sessions_update BEFORE UPDATE ON workout_sessions BEGIN SELECT RAISE(ABORT,'workout sessions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_sessions_delete BEFORE DELETE ON workout_sessions BEGIN SELECT RAISE(ABORT,'workout sessions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_entries_update BEFORE UPDATE ON workout_entries BEGIN SELECT RAISE(ABORT,'workout entries are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_entries_delete BEFORE DELETE ON workout_entries BEGIN SELECT RAISE(ABORT,'workout entries are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_checkins_update BEFORE UPDATE ON checkins BEGIN SELECT RAISE(ABORT,'check-ins are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_checkins_delete BEFORE DELETE ON checkins BEGIN SELECT RAISE(ABORT,'check-ins are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_decisions_update BEFORE UPDATE ON plan_decisions BEGIN SELECT RAISE(ABORT,'plan decisions are append-only; record a new decision'); END;
CREATE TRIGGER IF NOT EXISTS immutable_decisions_delete BEFORE DELETE ON plan_decisions BEGIN SELECT RAISE(ABORT,'plan decisions are append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_audit_update BEFORE UPDATE ON audit_log BEGIN SELECT RAISE(ABORT,'audit log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS immutable_audit_delete BEFORE DELETE ON audit_log BEGIN SELECT RAISE(ABORT,'audit log is append-only'); END;
"""


def _restrict_permissions(path: Path, directory: bool = False) -> None:
    if os.name != "nt":
        try:
            path.chmod(0o700 if directory else 0o600)
        except OSError:
            pass


def connect(path: Optional[Path] = None) -> sqlite3.Connection:
    target = Path(path or DB_PATH).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _restrict_permissions(target.parent, directory=True)
    conn = sqlite3.connect(str(target), timeout=15)
    _restrict_permissions(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=15000")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def session(path: Optional[Path] = None):
    conn = connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize(path: Optional[Path] = None) -> Path:
    target = Path(path or DB_PATH).expanduser()
    with session(target) as conn:
        current_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if current_version > SCHEMA_VERSION:
            raise RuntimeError(f"Database schema {current_version} is newer than this application supports ({SCHEMA_VERSION})")
        conn.executescript(SCHEMA)
        conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
    return target


def integrity_check(path: Path) -> str:
    conn = sqlite3.connect(str(path))
    try:
        row = conn.execute("PRAGMA integrity_check").fetchone()
        return str(row[0]) if row else "no-result"
    finally:
        conn.close()
