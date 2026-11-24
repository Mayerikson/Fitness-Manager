#!/usr/bin/env python3
"""Fitness Manager local-first database. Python standard library only; no network/API calls."""
import argparse
import csv
import hashlib
import json
import getpass
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME_DATA = Path.home() / '.fitness-manager'
CONFIG_PATH = HOME_DATA / 'config.json'

def load_config():
    try:
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8')) if CONFIG_PATH.exists() else {}
    except (OSError, json.JSONDecodeError):
        return {}

CONFIG = load_config()
DB_DEFAULT = Path(os.environ.get('FITNESS_MANAGER_DB', str(HOME_DATA / 'fitness_manager.sqlite')))
BACKUP_DEFAULT = Path(os.environ.get('FITNESS_MANAGER_BACKUP_DIR', str(HOME_DATA / 'backups')))
DRIVE_DEFAULT = (os.environ.get('FITNESS_MANAGER_DRIVE_BACKUP_DIR') or str(CONFIG.get('drive_backup_dir', ''))).strip()
SCHEMA_VERSION = 3
PROFILE_DEFAULT = Path(os.environ.get('FITNESS_MANAGER_PROFILE', str(HOME_DATA / 'profile.json'))).expanduser()
ENCRYPTION_MAGIC = b'FMENC1'



def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect(db):
    db = Path(db).expanduser()
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA busy_timeout=30000')
    return con


def table_exists(con, name):
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None


def install_audit_triggers(con, table):
    # Audit immutable event snapshots; do not recursively audit the audit table.
    for action in ('INSERT', 'UPDATE', 'DELETE'):
        trigger = f'audit_{table}_{action.lower()}'
        cols = get_columns(con, table)
        if action == 'INSERT':
            old_expr, new_expr = 'NULL', 'json_object(' + ','.join([f"'{c}', NEW.{c}" for c in cols]) + ')'
            row_id_expr = 'NEW.id' if 'id' in cols else 'NULL'
        elif action == 'DELETE':
            old_expr, new_expr = 'json_object(' + ','.join([f"'{c}', OLD.{c}" for c in cols]) + ')', 'NULL'
            row_id_expr = 'OLD.id' if 'id' in cols else 'NULL'
        else:
            old_expr = 'json_object(' + ','.join([f"'{c}', OLD.{c}" for c in cols]) + ')'
            new_expr = 'json_object(' + ','.join([f"'{c}', NEW.{c}" for c in cols]) + ')'
            row_id_expr = 'NEW.id' if 'id' in cols else 'NULL'
        con.execute(f'''CREATE TRIGGER IF NOT EXISTS {trigger} AFTER {action} ON {table}
            BEGIN INSERT INTO audit_log(event_at,table_name,action,row_id,old_data,new_data)
            VALUES(strftime('%Y-%m-%dT%H:%M:%fZ','now'),'{table}','{action}',
            {row_id_expr},{old_expr},{new_expr}); END;''')


def get_columns(con, table):
    return [r['name'] for r in con.execute(f'PRAGMA table_info({table})').fetchall()]


def init_db(con):
    con.executescript('''
    CREATE TABLE IF NOT EXISTS weigh_ins (
      id INTEGER PRIMARY KEY, date TEXT NOT NULL, weight_kg REAL NOT NULL CHECK(weight_kg > 0),
      conditions TEXT, source TEXT DEFAULT 'user-reported', created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS measurements (
      id INTEGER PRIMARY KEY, date TEXT NOT NULL, kind TEXT NOT NULL, value REAL NOT NULL CHECK(value > 0),
      unit TEXT NOT NULL, method TEXT, source TEXT DEFAULT 'user-measured', created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS meals (
      id INTEGER PRIMARY KEY, date TEXT NOT NULL, meal TEXT NOT NULL, food TEXT NOT NULL,
      grams REAL, kcal REAL, protein_g REAL, carbs_g REAL, fat_g REAL, fiber_g REAL,
      preparation TEXT, source TEXT, notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS workouts (
      id INTEGER PRIMARY KEY, date TEXT NOT NULL, session TEXT NOT NULL, exercise TEXT NOT NULL,
      sets INTEGER, reps TEXT, load_kg REAL, rir REAL, rpe REAL, pain TEXT, notes TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS runs (
      id INTEGER PRIMARY KEY, date TEXT NOT NULL, distance_km REAL NOT NULL CHECK(distance_km > 0),
      duration_min REAL NOT NULL CHECK(duration_min > 0), pace_min_per_km REAL,
      rpe REAL, avg_hr_bpm INTEGER, surface TEXT, symptoms TEXT, notes TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS decisions (
      id INTEGER PRIMARY KEY, date TEXT NOT NULL, area TEXT NOT NULL, previous_plan TEXT,
      proposed_change TEXT NOT NULL, evidence TEXT NOT NULL, rationale TEXT NOT NULL,
      approval_status TEXT NOT NULL DEFAULT 'pending', review_date TEXT, outcome TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS checkins (
      id INTEGER PRIMARY KEY, date TEXT NOT NULL, sleep_hours REAL, energy_1_10 REAL,
      soreness_1_10 REAL, stress_1_10 REAL, steps INTEGER, symptoms TEXT, notes TEXT,
      source TEXT DEFAULT 'user-reported', created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS profile (
      key TEXT PRIMARY KEY, value_json TEXT NOT NULL, source TEXT NOT NULL,
      effective_date TEXT NOT NULL, updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit_log (
      id INTEGER PRIMARY KEY, event_at TEXT NOT NULL, table_name TEXT NOT NULL,
      action TEXT NOT NULL, row_id INTEGER, old_data TEXT, new_data TEXT
    );
    CREATE TABLE IF NOT EXISTS backup_history (
      id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, local_path TEXT NOT NULL,
      sha256 TEXT NOT NULL, size_bytes INTEGER NOT NULL, drive_copy_path TEXT,
      status TEXT NOT NULL, notes TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_weigh_ins_date ON weigh_ins(date);
    CREATE INDEX IF NOT EXISTS idx_measurements_date_kind ON measurements(date,kind);
    CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date);
    CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);
    CREATE INDEX IF NOT EXISTS idx_runs_date ON runs(date);
    CREATE INDEX IF NOT EXISTS idx_decisions_date ON decisions(date);
    CREATE INDEX IF NOT EXISTS idx_checkins_date ON checkins(date);
    ''')
    version = con.execute('PRAGMA user_version').fetchone()[0]
    if version < 1:
        con.execute('PRAGMA user_version=1')
    # Import private profile exactly once, from the user's home directory, never from the distributable package.
    profile_path = PROFILE_DEFAULT
    profile_empty = con.execute('SELECT COUNT(*) FROM profile').fetchone()[0] == 0
    if profile_empty and profile_path.exists():
        profile = json.loads(profile_path.read_text(encoding='utf-8'))
        d = profile.get('last_confirmed_date', date.today().isoformat())
        if profile.get('baseline_weight_kg') and con.execute('SELECT COUNT(*) FROM weigh_ins').fetchone()[0] == 0:
            con.execute('INSERT INTO weigh_ins(date,weight_kg,conditions,source) VALUES(?,?,?,?)',
                        (d, profile['baseline_weight_kg'], 'Linha de base inicial; confirmar em nova pesagem', 'user-reported'))
        if profile.get('baseline_waist_cm') and con.execute("SELECT COUNT(*) FROM measurements WHERE kind='waist'").fetchone()[0] == 0:
            con.execute('INSERT INTO measurements(date,kind,value,unit,method,source) VALUES(?,?,?,?,?,?)',
                        (d, 'waist', profile['baseline_waist_cm'], 'cm', profile.get('waist_method',''), 'user-measured'))
        for key, value in profile.items():
            con.execute('INSERT OR IGNORE INTO profile(key,value_json,source,effective_date,updated_at) VALUES(?,?,?,?,?)',
                        (key, json.dumps(value, ensure_ascii=False), 'user-confirmed/private-profile-file', d, utc_now()))
    if version < 2:
        con.execute('PRAGMA user_version=2')
    if version < 3:
        con.execute('PRAGMA user_version=3')
    for table in ('weigh_ins','measurements','meals','workouts','runs','decisions','checkins','profile'):
        install_audit_triggers(con, table)
    con.commit()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_db(path):
    con = sqlite3.connect(f'file:{Path(path).resolve()}?mode=ro', uri=True)
    try:
        result = con.execute('PRAGMA integrity_check').fetchone()[0]
        if result != 'ok':
            raise RuntimeError(f'Falha de integridade SQLite: {result}')
        version = con.execute('PRAGMA user_version').fetchone()[0]
        if version < 1:
            raise RuntimeError('Arquivo não parece ser um banco Fitness Manager válido.')
        return version
    finally:
        con.close()


def copy_sqlite_consistent(source, destination):
    source = Path(source).expanduser().resolve()
    destination = Path(destination).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source == destination:
        raise ValueError('Origem e destino do backup não podem ser iguais.')
    with sqlite3.connect(str(source), timeout=30) as src:
        src.execute('PRAGMA busy_timeout=30000')
        with sqlite3.connect(str(destination), timeout=30) as dst:
            src.backup(dst)
            dst.execute('PRAGMA integrity_check')
    validate_db(destination)


def prune_backups(folder, keep=30):
    folder = Path(folder)
    candidates = list(folder.glob('fitness_manager_*.sqlite')) + list(folder.glob('fitness_manager_*.sqlite.enc'))
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    for old in candidates[keep:]:
        old.unlink(missing_ok=True)
        old.with_suffix('.json').unlink(missing_ok=True)
        old.with_name(old.name + '.json').unlink(missing_ok=True)


def _backup_passphrase(interactive=True):
    value = os.environ.get('FITNESS_MANAGER_BACKUP_PASSPHRASE', '')
    if value:
        return value
    if interactive and sys.stdin.isatty():
        value = getpass.getpass('Senha para criptografar backup do Google Drive: ')
        if value:
            return value
    return None


def _crypto():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
        return AESGCM, Scrypt
    except ImportError as exc:
        raise RuntimeError('Criptografia de backup requer o pacote gratuito cryptography. Instale com: python -m pip install cryptography') from exc


def encrypt_backup_file(source, destination, passphrase):
    if not passphrase or len(passphrase) < 12:
        raise ValueError('A senha de backup deve ter pelo menos 12 caracteres.')
    AESGCM, Scrypt = _crypto()
    salt = os.urandom(16)
    nonce = os.urandom(12)
    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    key = kdf.derive(passphrase.encode('utf-8'))
    plaintext = Path(source).read_bytes()
    aad = ENCRYPTION_MAGIC + salt + nonce
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(aad + ciphertext)
    try:
        target.chmod(0o600)
    except OSError:
        pass
    return 'AES-256-GCM + Scrypt (N=32768,r=8,p=1)'


def decrypt_backup_file(source, destination, passphrase):
    if not passphrase:
        raise ValueError('Backup criptografado exige FITNESS_MANAGER_BACKUP_PASSPHRASE ou senha interativa.')
    AESGCM, Scrypt = _crypto()
    raw = Path(source).read_bytes()
    if len(raw) < len(ENCRYPTION_MAGIC) + 16 + 12 + 16 or not raw.startswith(ENCRYPTION_MAGIC):
        raise RuntimeError('Formato de backup criptografado invalido.')
    offset = len(ENCRYPTION_MAGIC)
    salt = raw[offset:offset+16]
    nonce = raw[offset+16:offset+28]
    ciphertext = raw[offset+28:]
    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    key = kdf.derive(passphrase.encode('utf-8'))
    aad = ENCRYPTION_MAGIC + salt + nonce
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, aad)
    except Exception as exc:
        raise RuntimeError('Falha de autenticacao: senha incorreta ou backup adulterado.') from exc
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(plaintext)
    try:
        target.chmod(0o600)
    except OSError:
        pass
    return target


def make_backup(db, backup_dir=None, drive_dir=None, keep=30, reason='manual'):
    db = Path(db).expanduser().resolve()
    if not db.exists():
        raise FileNotFoundError(f'Banco nao encontrado: {db}. Execute init primeiro.')
    validate_db(db)
    backup_dir = Path(backup_dir or BACKUP_DEFAULT).expanduser()
    backup_dir.mkdir(parents=True, exist_ok=True)
    try:
        backup_dir.chmod(0o700)
    except OSError:
        pass
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    backup_path = backup_dir / f'fitness_manager_{stamp}.sqlite'
    copy_sqlite_consistent(db, backup_path)
    try:
        backup_path.chmod(0o600)
    except OSError:
        pass
    digest = sha256_file(backup_path)
    manifest = {
        'product': 'Fitness Manager Universal', 'schema_version': SCHEMA_VERSION,
        'created_at': utc_now(), 'reason': reason, 'database_file': backup_path.name,
        'sha256': digest, 'size_bytes': backup_path.stat().st_size,
        'integrity_check': 'ok', 'source_database': 'local-path-redacted'
    }
    manifest_path = backup_path.with_suffix('.json')
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    drive_copy = None
    cloud_status = 'not_configured'
    if drive_dir:
        passphrase = _backup_passphrase(interactive=True)
        if not passphrase:
            cloud_status = 'blocked_encryption_not_configured'
            print('Google Drive: copia remota BLOQUEADA. Configure FITNESS_MANAGER_BACKUP_PASSPHRASE; nenhum backup sem criptografia foi enviado.')
        else:
            target_dir = Path(drive_dir).expanduser()
            target_dir.mkdir(parents=True, exist_ok=True)
            target_db = target_dir / (backup_path.name + '.enc')
            algorithm = encrypt_backup_file(backup_path, target_db, passphrase)
            cloud_digest = sha256_file(target_db)
            cloud_manifest = {
                'product': 'Fitness Manager Universal', 'format': 'FMENC1',
                'created_at': utc_now(), 'encrypted_file': target_db.name,
                'sha256_ciphertext': cloud_digest, 'size_bytes': target_db.stat().st_size,
                'algorithm': algorithm, 'integrity': 'AES-GCM authenticated encryption'
            }
            target_manifest = target_db.with_name(target_db.name + '.json')
            target_manifest.write_text(json.dumps(cloud_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
            drive_copy = str(target_db.resolve())
            cloud_status = 'encrypted_copy_verified_locally'
            prune_backups(target_dir, keep)
            print(f'Copia criptografada criada na pasta sincronizada: {target_db}')
            print('A conclusao do upload remoto depende do Google Drive para computador; este programa nao confirma a sincronizacao na nuvem.')
    con = connect(db)
    status = 'local_verified' if cloud_status in ('not_configured','blocked_encryption_not_configured') else cloud_status
    con.execute('INSERT INTO backup_history(created_at,local_path,sha256,size_bytes,drive_copy_path,status,notes) VALUES(?,?,?,?,?,?,?)',
                (utc_now(), str(backup_path.resolve()), digest, backup_path.stat().st_size, drive_copy,
                 status, reason + '; cloud_status=' + cloud_status))
    con.commit(); con.close()
    prune_backups(backup_dir, keep)
    print(f'Backup local verificado: {backup_path}')
    print(f'SHA-256 local: {digest}')
    return backup_path


def verify_backup(path, passphrase=None):
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError('Arquivo de backup nao encontrado.')
    if path.name.endswith('.sqlite.enc'):
        manifest_path = path.with_name(path.name + '.json')
        if not manifest_path.exists():
            raise RuntimeError('Manifesto do backup criptografado ausente.')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if sha256_file(path) != manifest.get('sha256_ciphertext'):
            raise RuntimeError('SHA-256 do backup criptografado nao confere.')
        passphrase = passphrase or _backup_passphrase(interactive=True)
        fd, temp_name = tempfile.mkstemp(prefix='fm-verify-', suffix='.sqlite')
        os.close(fd)
        temp = Path(temp_name)
        try:
            decrypt_backup_file(path, temp, passphrase)
            validate_db(temp)
        finally:
            temp.unlink(missing_ok=True)
        return True
    if path.suffix.lower() != '.sqlite':
        raise FileNotFoundError('Informe um backup .sqlite local ou .sqlite.enc criptografado.')
    manifest_path = path.with_suffix('.json')
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        actual = sha256_file(path)
        if actual != manifest.get('sha256'):
            raise RuntimeError('SHA-256 nao confere. O backup pode estar corrompido ou alterado.')
    validate_db(path)
    return True


def restore_backup(db, backup_path, backup_dir=None):
    db = Path(db).expanduser().resolve()
    backup_path = Path(backup_path).expanduser().resolve()
    temp_plain = None
    if backup_path.name.endswith('.sqlite.enc'):
        passphrase = _backup_passphrase(interactive=True)
        verify_backup(backup_path, passphrase=passphrase)
        fd, temp_name = tempfile.mkstemp(prefix='fm-restore-', suffix='.sqlite')
        os.close(fd)
        temp_plain = Path(temp_name)
        decrypt_backup_file(backup_path, temp_plain, passphrase)
        source_path = temp_plain
    else:
        verify_backup(backup_path)
        source_path = backup_path
    try:
        if db.exists():
            safety_dir = Path(backup_dir or BACKUP_DEFAULT).expanduser() / 'pre_restore'
            safety_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            safety_copy = safety_dir / f'pre_restore_{stamp}.sqlite'
            copy_sqlite_consistent(db, safety_copy)
            print(f'Banco atual preservado antes da restauracao: {safety_copy}')
        db.parent.mkdir(parents=True, exist_ok=True)
        staging = db.with_name(db.name + '.restore-tmp')
        staging.unlink(missing_ok=True)
        copy_sqlite_consistent(source_path, staging)
        os.replace(staging, db)
        validate_db(db)
        print(f'Restauracao concluida e validada: {db}')
        print('Reabra o agente para que ele consulte o historico restaurado.')
    finally:
        if temp_plain:
            temp_plain.unlink(missing_ok=True)

def configure_drive(path):
    path = Path(path).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    probe = path / '.fitness_manager_write_test'
    probe.write_text('ok', encoding='utf-8')
    probe.unlink()
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    cfg['drive_backup_dir'] = str(path)
    cfg['drive_configured_at'] = utc_now()
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Diretório de backup configurado: {path}')
    print(f'Configuração salva em: {CONFIG_PATH}')
    print('Importante: a copia para o Drive so ocorre criptografada. Configure FITNESS_MANAGER_BACKUP_PASSPHRASE no ambiente do usuario antes de ativar o backup agendado.')

def clear_drive_config():
    cfg = load_config()
    cfg.pop('drive_backup_dir', None)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Diretório de backup Google Drive removido da configuração. Backups locais continuam ativos.')

def auto_backup_if_due(db):
    db = Path(db).expanduser().resolve()
    if not db.exists():
        return
    con = sqlite3.connect(str(db))
    last = con.execute("SELECT MAX(created_at) FROM backup_history WHERE status IN ('verified','local_verified','encrypted_copy_verified_locally')").fetchone()[0] if table_exists(con, 'backup_history') else None
    con.close()
    due = True
    if last:
        try:
            due = datetime.fromisoformat(last.replace('Z','+00:00')) < datetime.now(timezone.utc) - timedelta(hours=24)
        except ValueError:
            due = True
    if due:
        drive = DRIVE_DEFAULT or None
        make_backup(db, drive_dir=drive, reason='automatic-daily-on-write')


def add_record(con, sql, values, label):
    con.execute(sql, values); con.commit()
    print(label)


def add_weighin(con, a):
    add_record(con, 'INSERT INTO weigh_ins(date,weight_kg,conditions,source) VALUES(?,?,?,?)',
               (a.date,a.weight,a.conditions,a.source), f'Pesagem registrada: {a.date} — {a.weight:.1f} kg')

def add_measure(con, a):
    add_record(con, 'INSERT INTO measurements(date,kind,value,unit,method,source) VALUES(?,?,?,?,?,?)',
               (a.date,a.kind,a.value,a.unit,a.method,a.source), f'Medida registrada: {a.kind} = {a.value:g} {a.unit} em {a.date}')

def add_meal(con, a):
    add_record(con, '''INSERT INTO meals(date,meal,food,grams,kcal,protein_g,carbs_g,fat_g,fiber_g,preparation,source,notes)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
        (a.date,a.meal,a.food,a.grams,a.kcal,a.protein,a.carbs,a.fat,a.fiber,a.preparation,a.source,a.notes),
        f'Alimento registrado: {a.food} ({a.date}). Valores não informados permanecem vazios.')

def add_workout(con, a):
    add_record(con, '''INSERT INTO workouts(date,session,exercise,sets,reps,load_kg,rir,rpe,pain,notes)
        VALUES(?,?,?,?,?,?,?,?,?,?)''',
        (a.date,a.session,a.exercise,a.sets,a.reps,a.load_kg,a.rir,a.rpe,a.pain,a.notes),
        f'Treino registrado: {a.session} — {a.exercise} ({a.date})')

def add_run(con, a):
    pace = a.duration / a.distance
    add_record(con, '''INSERT INTO runs(date,distance_km,duration_min,pace_min_per_km,rpe,avg_hr_bpm,surface,symptoms,notes)
        VALUES(?,?,?,?,?,?,?,?,?)''',
        (a.date,a.distance,a.duration,pace,a.rpe,a.avg_hr,a.surface,a.symptoms,a.notes),
        f'Corrida registrada: {a.distance:g} km em {a.duration:g} min — pace {int(pace)}:{round((pace-int(pace))*60):02d}/km')

def add_decision(con, a):
    add_record(con, '''INSERT INTO decisions(date,area,previous_plan,proposed_change,evidence,rationale,approval_status,review_date)
        VALUES(?,?,?,?,?,?,?,?)''',
        (a.date,a.area,a.previous,a.change,a.evidence,a.rationale,a.approval,a.review_date),
        f'Decisão registrada: {a.area} ({a.date}) — status: {a.approval}')

def add_checkin(con, a):
    add_record(con, '''INSERT INTO checkins(date,sleep_hours,energy_1_10,soreness_1_10,stress_1_10,steps,symptoms,notes,source)
        VALUES(?,?,?,?,?,?,?,?,?)''',
        (a.date,a.sleep,a.energy,a.soreness,a.stress,a.steps,a.symptoms,a.notes,'user-reported'),
        f'Check-in registrado: {a.date}')

def report(con):
    queries = [
      ('Pesagens', 'SELECT date,weight_kg FROM weigh_ins ORDER BY date DESC,id DESC LIMIT 10'),
      ('Medidas', "SELECT date,kind,value,unit,method FROM measurements ORDER BY date DESC,id DESC LIMIT 15"),
      ('Alimentação', 'SELECT date,meal,food,grams,kcal,protein_g FROM meals ORDER BY date DESC,id DESC LIMIT 20'),
      ('Treinos', 'SELECT date,session,exercise,sets,reps,load_kg FROM workouts ORDER BY date DESC,id DESC LIMIT 20'),
      ('Corridas', 'SELECT date,distance_km,duration_min,pace_min_per_km FROM runs ORDER BY date DESC,id DESC LIMIT 10'),
      ('Check-ins', 'SELECT date,sleep_hours,energy_1_10,soreness_1_10,steps FROM checkins ORDER BY date DESC,id DESC LIMIT 10')]
    print('\n=== FITNESS MANAGER — HISTÓRICO LOCAL ===')
    for title, sql in queries:
        print(f'\n{title}:')
        rows = con.execute(sql).fetchall()
        if not rows: print('  Sem registros.'); continue
        for r in rows:
            print('  ' + ' | '.join(f'{k}={r[k]}' for k in r.keys()))
    print('\nAuditoria: use o comando history para consultar alterações registradas.')

def show_history(con, limit=30):
    rows = con.execute('SELECT event_at,table_name,action,row_id,old_data,new_data FROM audit_log ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    print('\n=== AUDITORIA ===')
    for r in rows:
        print(f"{r['event_at']} | {r['table_name']} | {r['action']} | id={r['row_id']}")
        if r['new_data']: print('  novo: ' + r['new_data'][:600])

def export_csv(con, out):
    tables = ['weigh_ins','measurements','meals','workouts','runs','decisions','checkins','profile','audit_log']
    out = Path(out).expanduser(); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f); writer.writerow(['table','record_json'])
        for table in tables:
            for row in con.execute(f'SELECT * FROM {table} ORDER BY 1'):
                writer.writerow([table,json.dumps(dict(row),ensure_ascii=False)])
    print(f'Exportação concluída: {out}')


def main():
    p = argparse.ArgumentParser(description='Fitness Manager local-first database; sem API/rede.')
    p.add_argument('--db', default=str(DB_DEFAULT), help='Caminho do banco SQLite')
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init', help='Criar/verificar banco local')
    wi=sub.add_parser('weigh-in'); wi.add_argument('--weight',type=float,required=True); wi.add_argument('--date',default=date.today().isoformat()); wi.add_argument('--conditions',default=''); wi.add_argument('--source',default='user-reported')
    me=sub.add_parser('measure'); me.add_argument('--kind',required=True); me.add_argument('--value',type=float,required=True); me.add_argument('--unit',default='cm'); me.add_argument('--method',default=''); me.add_argument('--date',default=date.today().isoformat()); me.add_argument('--source',default='user-measured')
    fo=sub.add_parser('meal'); fo.add_argument('--date',default=date.today().isoformat()); fo.add_argument('--meal',required=True); fo.add_argument('--food',required=True); fo.add_argument('--grams',type=float); fo.add_argument('--kcal',type=float); fo.add_argument('--protein',type=float); fo.add_argument('--carbs',type=float); fo.add_argument('--fat',type=float); fo.add_argument('--fiber',type=float); fo.add_argument('--preparation',default=''); fo.add_argument('--source',default=''); fo.add_argument('--notes',default='')
    wo=sub.add_parser('workout'); wo.add_argument('--date',default=date.today().isoformat()); wo.add_argument('--session',required=True); wo.add_argument('--exercise',required=True); wo.add_argument('--sets',type=int); wo.add_argument('--reps',default=''); wo.add_argument('--load-kg',type=float); wo.add_argument('--rir',type=float); wo.add_argument('--rpe',type=float); wo.add_argument('--pain',default=''); wo.add_argument('--notes',default='')
    ru=sub.add_parser('run'); ru.add_argument('--date',default=date.today().isoformat()); ru.add_argument('--distance-km',dest='distance',type=float,required=True); ru.add_argument('--duration-min',dest='duration',type=float,required=True); ru.add_argument('--rpe',type=float); ru.add_argument('--avg-hr',type=int); ru.add_argument('--surface',default=''); ru.add_argument('--symptoms',default=''); ru.add_argument('--notes',default='')
    de=sub.add_parser('decision'); de.add_argument('--date',default=date.today().isoformat()); de.add_argument('--area',required=True); de.add_argument('--previous',default=''); de.add_argument('--change',required=True); de.add_argument('--evidence',required=True); de.add_argument('--rationale',required=True); de.add_argument('--approval',choices=['pending','approved','rejected'],default='pending'); de.add_argument('--review-date',default='')
    ci=sub.add_parser('checkin'); ci.add_argument('--date',default=date.today().isoformat()); ci.add_argument('--sleep',type=float); ci.add_argument('--energy',type=float); ci.add_argument('--soreness',type=float); ci.add_argument('--stress',type=float); ci.add_argument('--steps',type=int); ci.add_argument('--symptoms',default=''); ci.add_argument('--notes',default='')
    sub.add_parser('report', help='Mostrar resumo do histórico')
    hi=sub.add_parser('history'); hi.add_argument('--limit',type=int,default=30)
    ba=sub.add_parser('backup', help='Criar backup consistente e verificar SHA-256'); ba.add_argument('--backup-dir',default=str(BACKUP_DEFAULT)); ba.add_argument('--drive-dir',default=DRIVE_DEFAULT); ba.add_argument('--keep',type=int,default=30)
    re=sub.add_parser('restore', help='Restaurar backup verificado; preserva cópia pré-restauração'); re.add_argument('--from',dest='backup',required=True); re.add_argument('--backup-dir',default=str(BACKUP_DEFAULT))
    ex=sub.add_parser('export',help='Exportar histórico para CSV'); ex.add_argument('--out',default=str(ROOT/'data'/'fitness_export.csv'))
    cd=sub.add_parser('configure-drive',help='Configurar pasta local sincronizada pelo Google Drive'); cd.add_argument('--path',required=True)
    sub.add_parser('clear-drive',help='Desativar cópia para Google Drive; mantém backups locais')
    a=p.parse_args()
    if a.cmd == 'restore':
        restore_backup(a.db, a.backup, a.backup_dir); return
    if a.cmd == 'configure-drive':
        configure_drive(a.path); return
    if a.cmd == 'clear-drive':
        clear_drive_config(); return
    con=connect(a.db); init_db(con)
    try:
        if a.cmd=='init': print(f'Banco pronto: {a.db}')
        elif a.cmd=='weigh-in': add_weighin(con,a)
        elif a.cmd=='measure': add_measure(con,a)
        elif a.cmd=='meal': add_meal(con,a)
        elif a.cmd=='workout': add_workout(con,a)
        elif a.cmd=='run': add_run(con,a)
        elif a.cmd=='decision': add_decision(con,a)
        elif a.cmd=='checkin': add_checkin(con,a)
        elif a.cmd=='report': report(con)
        elif a.cmd=='history': show_history(con,a.limit)
        elif a.cmd=='backup': make_backup(a.db,a.backup_dir,a.drive_dir,a.keep,'manual')
        elif a.cmd=='export': export_csv(con,a.out)
    finally:
        con.close()
    if a.cmd in {'weigh-in','measure','meal','workout','run','decision','checkin'}:
        auto_backup_if_due(a.db)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        sys.exit(1)
