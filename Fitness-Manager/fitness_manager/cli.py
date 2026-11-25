"""Command-line interface for local Fitness Manager records."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from .db import APP_DIR, DB_PATH, initialize, session
from .storage import create_backup, maybe_encrypt_for_drive, restore_backup


def _date(value: str | None) -> str:
    if not value:
        return date.today().isoformat()
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must use YYYY-MM-DD") from exc


def _config_path() -> Path:
    return APP_DIR / "config.json"


def _read_config() -> dict:
    path = _config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid configuration file: {path}")


def _connect_ready() -> sqlite3.Connection:
    if not DB_PATH.exists():
        initialize()
    return session()


def cmd_init(_args) -> int:
    path = initialize()
    print(f"Database initialized: {path}")
    return 0


def cmd_weigh_in(args) -> int:
    return _insert_measurement("weight", args.weight, "kg", _date(args.date), "scale", args.source, args.notes)


def _insert_measurement(kind, value, unit, measured_at, method, source, notes) -> int:
    with _connect_ready() as conn:
        cursor = conn.execute(
            "INSERT INTO measurements(measured_at,kind,value,unit,method,source,notes) VALUES(?,?,?,?,?,?,?)",
            (measured_at, kind, value, unit, method, source, notes),
        )
        record_id = cursor.lastrowid
    print(f"Measurement saved: id={record_id} kind={kind} value={value} {unit} date={measured_at}")
    return 0


def cmd_measure(args) -> int:
    return _insert_measurement(args.kind, args.value, args.unit, args.date, args.method, args.source, args.notes)


def cmd_food(args) -> int:
    with _connect_ready() as conn:
        cursor = conn.execute(
            """INSERT INTO food_logs(consumed_at,meal,food,quantity_g,kcal,protein_g,carbs_g,fat_g,preparation,source,notes)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (_date(args.date), args.meal, args.food, args.quantity_g, args.kcal, args.protein_g,
             args.carbs_g, args.fat_g, args.preparation, args.source, args.notes),
        )
        record_id = cursor.lastrowid
    print(f"Food log saved: id={record_id} food={args.food} date={_date(args.date)}")
    return 0


def cmd_workout(args) -> int:
    with _connect_ready() as conn:
        if args.session_id:
            session = conn.execute("SELECT id FROM workout_sessions WHERE id=?", (args.session_id,)).fetchone()
            if not session:
                raise ValueError(f"Workout session not found: {args.session_id}")
            session_id = args.session_id
        else:
            cur = conn.execute(
                "INSERT INTO workout_sessions(performed_at,session_name,duration_min,rpe,notes) VALUES(?,?,?,?,?)",
                (_date(args.date), args.session, args.duration_min, args.session_rpe, args.session_notes),
            )
            session_id = cur.lastrowid
        cur = conn.execute(
            """INSERT INTO workout_entries(session_id,exercise,sets,reps,load_kg,rir,substitution_for,notes)
               VALUES(?,?,?,?,?,?,?,?)""",
            (session_id, args.exercise, args.sets, args.reps, args.load_kg, args.rir, args.substitution_for, args.notes),
        )
        record_id = cur.lastrowid
    print(f"Workout entry saved: id={record_id} session_id={session_id} exercise={args.exercise}")
    return 0


def cmd_run(args) -> int:
    duration_sec = int(round(args.duration_min * 60))
    pace = duration_sec / args.distance_km
    with _connect_ready() as conn:
        cur = conn.execute(
            """INSERT INTO runs(performed_at,distance_km,duration_sec,pace_sec_per_km,rpe,avg_hr,terrain,symptoms,notes)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (_date(args.date), args.distance_km, duration_sec, pace, args.rpe, args.avg_hr, args.terrain, args.symptoms, args.notes),
        )
        record_id = cur.lastrowid
    print(f"Run saved: id={record_id} distance={args.distance_km:.2f} km pace={int(pace//60)}:{int(pace%60):02d}/km")
    return 0


def cmd_checkin(args) -> int:
    with _connect_ready() as conn:
        cur = conn.execute(
            "INSERT INTO checkins(checked_at,sleep_hours,recovery,soreness,energy,symptoms,notes) VALUES(?,?,?,?,?,?,?)",
            (_date(args.date), args.sleep_hours, args.recovery, args.soreness, args.energy, args.symptoms, args.notes),
        )
        record_id = cur.lastrowid
    print(f"Check-in saved: id={record_id} date={_date(args.date)}")
    return 0


def cmd_decision(args) -> int:
    with _connect_ready() as conn:
        cur = conn.execute(
            """INSERT INTO plan_decisions(decided_at,domain,current_plan,proposed_plan,evidence,rationale,uncertainty,approval_status,review_date)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (_date(args.date), args.domain, args.current_plan, args.proposed_plan, args.evidence,
             args.rationale, args.uncertainty, args.approval_status, args.review_date),
        )
        record_id = cur.lastrowid
    print(f"Decision saved: id={record_id} domain={args.domain} status={args.approval_status}")
    return 0



def cmd_profile(args) -> int:
    with _connect_ready() as conn:
        if args.action == "show":
            row = conn.execute("SELECT sex,age_years,height_cm,goals_json,updated_at FROM profile WHERE id=1").fetchone()
            if not row:
                print("No profile saved.")
            else:
                print(json.dumps(dict(row), indent=2))
            return 0
        goals = json.dumps(args.goal or [], ensure_ascii=False)
        conn.execute(
            """INSERT INTO profile(id,sex,age_years,height_cm,goals_json) VALUES(1,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET sex=excluded.sex,age_years=excluded.age_years,
               height_cm=excluded.height_cm,goals_json=excluded.goals_json,
               updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')""",
            (args.sex, args.age, args.height_cm, goals),
        )
    print("Profile saved locally.")
    return 0


def cmd_report(_args) -> int:
    with _connect_ready() as conn:
        print(f"Database: {DB_PATH}")
        for kind, label in (("weight", "Latest weight"), ("waist", "Latest waist")):
            row = conn.execute("SELECT measured_at,value,unit FROM measurements WHERE kind=? ORDER BY measured_at DESC,id DESC LIMIT 1", (kind,)).fetchone()
            print(f"{label}: {row['value']} {row['unit']} ({row['measured_at']})" if row else f"{label}: no record")
        counts = {
            "measurements": "measurements", "food logs": "food_logs", "workout sessions": "workout_sessions",
            "workout entries": "workout_entries", "runs": "runs", "check-ins": "checkins", "plan decisions": "plan_decisions"
        }
        for label, table in counts.items():
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{label}: {count}")
    return 0



def cmd_audit(args) -> int:
    with _connect_ready() as conn:
        rows = conn.execute(
            "SELECT id,table_name,action,record_id,occurred_at FROM audit_log ORDER BY id DESC LIMIT ?",
            (args.limit,),
        ).fetchall()
        if not rows:
            print("No audit events.")
        for row in rows:
            print(f"{row['occurred_at']} | {row['table_name']} | {row['action']} | record={row['record_id']} | audit_id={row['id']}")
    return 0


def cmd_history(args) -> int:
    with _connect_ready() as conn:
        queries = [
            ("MEASUREMENTS", "SELECT measured_at AS date,kind AS item,value,unit AS detail FROM measurements ORDER BY measured_at DESC,id DESC LIMIT ?"),
            ("FOOD", "SELECT consumed_at AS date,food AS item,quantity_g AS value,'g' AS unit FROM food_logs ORDER BY consumed_at DESC,id DESC LIMIT ?"),
            ("WORKOUTS", "SELECT s.performed_at AS date,e.exercise AS item,e.sets AS value,'sets' AS unit FROM workout_entries e JOIN workout_sessions s ON s.id=e.session_id ORDER BY s.performed_at DESC,e.id DESC LIMIT ?"),
            ("RUNS", "SELECT performed_at AS date,printf('%.2f km',distance_km) AS item,duration_sec AS value,'seconds' AS unit FROM runs ORDER BY performed_at DESC,id DESC LIMIT ?"),
        ]
        for title, sql in queries:
            print(f"\n{title}")
            rows = conn.execute(sql, (args.limit,)).fetchall()
            if not rows:
                print("  (no records)")
            for row in rows:
                detail = row["detail"] if "detail" in row.keys() else row["unit"]
                print(f"  {row['date']} | {row['item']} | {row['value']} {detail}")
    return 0


def cmd_backup(args) -> int:
    backup = create_backup()
    print(f"Local backup created and verified: {backup}")
    config = _read_config()
    drive_dir = os.environ.get("FITNESS_MANAGER_DRIVE_BACKUP_DIR") or config.get("drive_backup_dir")
    if drive_dir:
        passphrase = os.environ.get("FITNESS_MANAGER_BACKUP_PASSPHRASE")
        encrypted = maybe_encrypt_for_drive(backup, Path(drive_dir), passphrase)
        print(f"Encrypted Drive-sync copy created: {encrypted}")
        print("Remote synchronization is not verified by this command; check the Drive client.")
    else:
        print("Cloud backup not configured; no upload attempted.")
    return 0


def cmd_configure_drive(args) -> int:
    target = Path(args.path).expanduser().resolve()
    if not target.exists() or not target.is_dir():
        raise ValueError("The Drive sync path must already exist and be a directory")
    APP_DIR.mkdir(parents=True, exist_ok=True)
    config = _read_config()
    config["drive_backup_dir"] = str(target)
    _config_path().write_text(json.dumps(config, indent=2), encoding="utf-8")
    if os.name != "nt":
        _config_path().chmod(0o600)
    print(f"Drive sync directory configured: {target}")
    print("Encrypted cloud copies still require FITNESS_MANAGER_BACKUP_PASSPHRASE in the local environment.")
    return 0


def cmd_restore(args) -> int:
    target = restore_backup(Path(args.source), DB_PATH, os.environ.get("FITNESS_MANAGER_BACKUP_PASSPHRASE"))
    print(f"Database restored and verified: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fitness_manager", description="Local-first Fitness Manager data CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize the local SQLite database").set_defaults(func=cmd_init)
    sub.add_parser("report", help="Show a summary of local records").set_defaults(func=cmd_report)
    profile = sub.add_parser("profile", help="Show or set the private local profile")
    profile_sub = profile.add_subparsers(dest="action", required=True)
    profile_sub.add_parser("show", help="Show the local profile").set_defaults(func=cmd_profile)
    profile_set = profile_sub.add_parser("set", help="Set the local profile")
    profile_set.add_argument("--sex", choices=["male","female","other","not_specified"], required=True)
    profile_set.add_argument("--age", type=int, required=True)
    profile_set.add_argument("--height-cm", type=float, required=True)
    profile_set.add_argument("--goal", action="append", default=[])
    profile_set.set_defaults(func=cmd_profile)
    hist = sub.add_parser("history", help="Show recent records")
    hist.add_argument("--limit", type=int, default=20)
    hist.set_defaults(func=cmd_history)
    audit = sub.add_parser("audit", help="Show recent local audit events")
    audit.add_argument("--limit", type=int, default=50)
    audit.set_defaults(func=cmd_audit)

    weigh = sub.add_parser("weigh-in", help="Record body weight")
    weigh.add_argument("--weight", type=float, required=True)
    weigh.add_argument("--date", type=_date)
    weigh.add_argument("--source", default="user_reported")
    weigh.add_argument("--notes")
    weigh.set_defaults(func=cmd_weigh_in)

    measure = sub.add_parser("measure", help="Record a body measurement")
    measure.add_argument("--kind", choices=["waist","abdomen","hip","chest","arm_left","arm_right","thigh_left","thigh_right","other"], required=True)
    measure.add_argument("--value", type=float, required=True)
    measure.add_argument("--unit", choices=["cm","mm","in"], default="cm")
    measure.add_argument("--date", type=_date)
    measure.add_argument("--method")
    measure.add_argument("--source", default="user_reported")
    measure.add_argument("--notes")
    measure.set_defaults(func=cmd_measure)

    food = sub.add_parser("food", help="Record one food item")
    food.add_argument("--meal", required=True)
    food.add_argument("--food", required=True)
    food.add_argument("--quantity-g", type=float)
    food.add_argument("--kcal", type=float)
    food.add_argument("--protein-g", type=float)
    food.add_argument("--carbs-g", type=float)
    food.add_argument("--fat-g", type=float)
    food.add_argument("--preparation")
    food.add_argument("--date", type=_date)
    food.add_argument("--source", default="user_reported")
    food.add_argument("--notes")
    food.set_defaults(func=cmd_food)

    workout = sub.add_parser("workout", help="Record one exercise entry")
    workout.add_argument("--date", type=_date)
    workout.add_argument("--session", default="Unspecified")
    workout.add_argument("--session-id", type=int)
    workout.add_argument("--exercise", required=True)
    workout.add_argument("--sets", type=int, required=True)
    workout.add_argument("--reps", type=int, required=True)
    workout.add_argument("--load-kg", type=float)
    workout.add_argument("--rir", type=float)
    workout.add_argument("--substitution-for")
    workout.add_argument("--duration-min", type=float)
    workout.add_argument("--session-rpe", type=float)
    workout.add_argument("--session-notes")
    workout.add_argument("--notes")
    workout.set_defaults(func=cmd_workout)

    run = sub.add_parser("run", help="Record a run up to 15 km")
    run.add_argument("--date", type=_date)
    run.add_argument("--distance-km", type=float, required=True)
    run.add_argument("--duration-min", type=float, required=True)
    run.add_argument("--rpe", type=float)
    run.add_argument("--avg-hr", type=int)
    run.add_argument("--terrain")
    run.add_argument("--symptoms")
    run.add_argument("--notes")
    run.set_defaults(func=cmd_run)

    checkin = sub.add_parser("checkin", help="Record recovery and wellbeing")
    checkin.add_argument("--date", type=_date)
    checkin.add_argument("--sleep-hours", type=float)
    checkin.add_argument("--recovery", type=int)
    checkin.add_argument("--soreness", type=int)
    checkin.add_argument("--energy", type=int)
    checkin.add_argument("--symptoms")
    checkin.add_argument("--notes")
    checkin.set_defaults(func=cmd_checkin)

    decision = sub.add_parser("decision", help="Record a proposed or approved plan decision")
    decision.add_argument("--date", type=_date)
    decision.add_argument("--domain", choices=["training","nutrition","running","general"], required=True)
    decision.add_argument("--current-plan")
    decision.add_argument("--proposed-plan", required=True)
    decision.add_argument("--evidence", required=True)
    decision.add_argument("--rationale", required=True)
    decision.add_argument("--uncertainty")
    decision.add_argument("--approval-status", choices=["proposed","approved","rejected","implemented","reverted"], default="proposed")
    decision.add_argument("--review-date")
    decision.set_defaults(func=cmd_decision)

    sub.add_parser("backup", help="Create and verify a local backup; optionally encrypt a Drive-sync copy").set_defaults(func=cmd_backup)
    restore = sub.add_parser("restore", help="Restore a verified backup")
    restore.add_argument("--from", dest="source", required=True)
    restore.set_defaults(func=cmd_restore)
    drive = sub.add_parser("configure-drive", help="Configure an existing local Google Drive sync folder")
    drive.add_argument("--path", required=True)
    drive.set_defaults(func=cmd_configure_drive)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:  # CLI boundary: concise, non-secret error message.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
