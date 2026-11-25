import sqlite3
import tempfile
import unittest
from pathlib import Path

from fitness_manager.db import initialize, session
from fitness_manager.storage import create_backup, maybe_encrypt_for_drive, restore_backup, verify_backup


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "fitness_manager.sqlite"
        initialize(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_schema_initializes_and_integrity_is_ok(self):
        with session(self.db) as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            self.assertEqual(version, 2)
            self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_schema_v1_upgrade_adds_integration_tables(self):
        with session(self.db) as conn:
            conn.execute("INSERT INTO measurements(measured_at,kind,value,unit) VALUES('2025-01-01','weight',112,'kg')")
            conn.execute("PRAGMA user_version=1")
        initialize(self.db)
        with session(self.db) as conn:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 2)
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertIn("integration_events", tables)
            self.assertIn("integration_state", tables)
            self.assertEqual(conn.execute("SELECT value FROM measurements WHERE kind='weight'").fetchone()[0], 112)

    def test_measurement_insert_is_audited(self):
        with session(self.db) as conn:
            conn.execute(
                "INSERT INTO measurements(measured_at,kind,value,unit) VALUES('2025-01-10','weight',72.4,'kg')"
            )
            row = conn.execute("SELECT table_name,action,record_id FROM audit_log").fetchone()
            self.assertEqual(tuple(row), ("measurements", "INSERT", 1))

    def test_historical_measurements_are_append_only(self):
        with session(self.db) as conn:
            conn.execute(
                "INSERT INTO measurements(measured_at,kind,value,unit) VALUES('2025-01-10','waist',83,'cm')"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            with session(self.db) as conn:
                conn.execute("UPDATE measurements SET value=107 WHERE id=1")

    def test_audit_log_is_append_only(self):
        with session(self.db) as conn:
            conn.execute(
                "INSERT INTO measurements(measured_at,kind,value,unit) VALUES('2025-01-10','weight',72.4,'kg')"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            with session(self.db) as conn:
                conn.execute("DELETE FROM audit_log WHERE id=1")

    def test_run_distance_is_limited_to_15_km(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with session(self.db) as conn:
                conn.execute(
                    "INSERT INTO runs(performed_at,distance_km,duration_sec,pace_sec_per_km) VALUES('2025-01-10',16,6000,375)"
                )

    def test_backup_manifest_and_restore(self):
        with session(self.db) as conn:
            conn.execute(
                "INSERT INTO measurements(measured_at,kind,value,unit) VALUES('2025-01-10','weight',72.4,'kg')"
            )
        backup = create_backup(self.db, self.root / "backups")
        verify_backup(backup)
        with session(self.db) as conn:
            conn.execute(
                "INSERT INTO measurements(measured_at,kind,value,unit) VALUES('2025-01-11','weight',71.4,'kg')"
            )
        restore_backup(backup, self.db)
        with session(self.db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]
        self.assertEqual(count, 1)
        self.assertTrue((self.root / "pre-restore").exists())

    def test_encrypted_drive_backup_can_be_restored(self):
        try:
            import cryptography  # noqa: F401
        except ImportError:
            self.skipTest("optional cryptography dependency is not installed")
        with session(self.db) as conn:
            conn.execute(
                "INSERT INTO measurements(measured_at,kind,value,unit) VALUES('2025-01-10','weight',72.4,'kg')"
            )
        backup = create_backup(self.db, self.root / "backups")
        encrypted = maybe_encrypt_for_drive(backup, self.root / "drive", "synthetic-test-passphrase")
        target = self.root / "restored.sqlite"
        restore_backup(encrypted, target, "synthetic-test-passphrase")
        with session(target) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM measurements").fetchone()[0], 1)
        with self.assertRaises(Exception):
            restore_backup(encrypted, self.root / "wrong.sqlite", "incorrect-passphrase")

    def test_manifest_detects_tampering(self):
        backup = create_backup(self.db, self.root / "backups")
        with backup.open("ab") as stream:
            stream.write(b"tamper")
        with self.assertRaises(ValueError):
            verify_backup(backup)


if __name__ == "__main__":
    unittest.main()
