import json, os, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'fitness_manager.py'

class FitnessManagerCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.db = self.base / 'fm.sqlite'
        self.backups = self.base / 'backups'
        self.drive = self.base / 'drive'
        home = self.base / 'home'
        profile_dir = home / '.fitness-manager'
        profile_dir.mkdir(parents=True)
        profile = {"profile_version":1,"last_confirmed_date":"2025-01-10","sex":"male","age_years":29,"height_cm":172,"baseline_weight_kg":73.4,"baseline_waist_cm":84,"waist_method":"synthetic test fixture","goals":["fat loss"],"running_distance_ceiling_km":15}
        (profile_dir / 'profile.json').write_text(json.dumps(profile), encoding='utf-8')
        self.env = dict(os.environ, HOME=str(home), FITNESS_MANAGER_DB=str(self.db), FITNESS_MANAGER_BACKUP_DIR=str(self.backups), FITNESS_MANAGER_BACKUP_PASSPHRASE='test-passphrase-strong-2026')
        subprocess.run([sys.executable, str(SCRIPT), 'init'], env=self.env, check=True, capture_output=True, text=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], env=self.env, check=True, capture_output=True, text=True)

    def test_baseline_seeded_once(self):
        con = sqlite3.connect(self.db)
        self.assertEqual(con.execute('select weight_kg from weigh_ins').fetchone()[0], 73.4)
        self.assertEqual(con.execute("select value from measurements where kind='waist'").fetchone()[0], 84.0)
        con.close()
        self.run_cli('init')
        con = sqlite3.connect(self.db)
        self.assertEqual(con.execute('select count(*) from weigh_ins').fetchone()[0], 1)
        con.close()

    def test_run_pace_calculation_and_audit(self):
        self.run_cli('run', '--distance-km', '5', '--duration-min', '30')
        con = sqlite3.connect(self.db)
        self.assertAlmostEqual(con.execute('select pace_min_per_km from runs').fetchone()[0], 6.0)
        self.assertEqual(con.execute("select count(*) from audit_log where table_name='runs' and action='INSERT'").fetchone()[0], 1)
        con.close()

    def test_food_values_can_remain_unknown(self):
        self.run_cli('meal', '--meal', 'lunch', '--food', 'rice')
        con = sqlite3.connect(self.db)
        row = con.execute('select kcal,protein_g from meals').fetchone()
        self.assertEqual(row, (None, None))
        con.close()

    def test_backup_drive_copy_manifest_and_restore(self):
        self.run_cli('weigh-in', '--weight', '72.9', '--date', '2025-01-11')
        out = self.run_cli('backup', '--backup-dir', str(self.backups), '--drive-dir', str(self.drive))
        backups = list(self.backups.glob('fitness_manager_*.sqlite'))
        self.assertGreaterEqual(len(backups), 1)
        backup = max(backups, key=lambda p: p.stat().st_mtime)
        self.assertTrue(backup.with_suffix('.json').exists())
        encrypted = self.drive / (backup.name + '.enc')
        self.assertTrue(encrypted.exists())
        self.assertTrue(encrypted.with_name(encrypted.name + '.json').exists())
        self.assertFalse((self.drive / backup.name).exists())
        manifest = json.loads(backup.with_suffix('.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['integrity_check'], 'ok')
        self.run_cli('weigh-in', '--weight', '72.2', '--date', '2025-01-12')
        con = sqlite3.connect(self.db)
        self.assertEqual(con.execute('select count(*) from weigh_ins').fetchone()[0], 3)
        con.close()
        self.run_cli('restore', '--from', str(backup), '--backup-dir', str(self.backups))
        con = sqlite3.connect(self.db)
        vals = [r[0] for r in con.execute('select weight_kg from weigh_ins order by id')]
        self.assertEqual(vals, [73.4, 72.9])
        con.close()
        self.assertTrue(list((self.backups / 'pre_restore').glob('pre_restore_*.sqlite')))

    def test_configure_drive_folder_and_auto_copy(self):
        self.run_cli('configure-drive', '--path', str(self.drive))
        self.run_cli('backup', '--backup-dir', str(self.backups))
        copies = list(self.drive.glob('fitness_manager_*.sqlite.enc'))
        self.assertEqual(len(copies), 1)
        self.assertTrue(copies[0].with_name(copies[0].name + '.json').exists())

    def test_drive_copy_blocked_without_passphrase(self):
        env = dict(self.env)
        env.pop('FITNESS_MANAGER_BACKUP_PASSPHRASE', None)
        proc = subprocess.run([sys.executable, str(SCRIPT), '--db', str(self.db), 'backup', '--backup-dir', str(self.backups), '--drive-dir', str(self.drive)], env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn('BLOQUEADA', proc.stdout)
        self.assertEqual(list(self.drive.glob('*.sqlite*')), [])
        self.assertGreaterEqual(len(list(self.backups.glob('*.sqlite'))), 1)

    def test_encrypted_backup_rejects_wrong_passphrase(self):
        self.run_cli('backup', '--backup-dir', str(self.backups), '--drive-dir', str(self.drive))
        encrypted = next(self.drive.glob('*.sqlite.enc'))
        env = dict(self.env, FITNESS_MANAGER_BACKUP_PASSPHRASE='wrong-password-123')
        proc = subprocess.run([sys.executable, str(SCRIPT), '--db', str(self.db), 'restore', '--from', str(encrypted)], env=env, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('autenticacao', proc.stderr.lower())

    def test_distributable_has_no_private_profile(self):
        self.assertFalse((ROOT / 'data' / 'profile.json').exists())
        self.assertTrue((ROOT / 'data' / 'profile.example.json').exists())

    def test_corrupt_backup_rejected(self):
        self.run_cli('backup', '--backup-dir', str(self.backups))
        backup = next(self.backups.glob('fitness_manager_*.sqlite'))
        backup.write_bytes(b'corrupt')
        proc = subprocess.run([sys.executable, str(SCRIPT), '--db', str(self.db), 'restore', '--from', str(backup)], env=self.env, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('SHA-256', proc.stderr)


    def test_release_audit_passes_and_preserves_module_convention(self):
        audit = ROOT / 'scripts' / 'audit_release.py'
        proc = subprocess.run([sys.executable, str(audit), str(ROOT)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((ROOT / 'governance' / 'MODULE.md').exists())
        self.assertTrue((ROOT / 'governance' / 'quality-gates' / 'MODULE.md').exists())
        self.assertTrue((ROOT / 'SKILL.md').exists())

    def test_release_audit_rejects_private_profile(self):
        private = ROOT / 'data' / 'profile.json'
        private.parent.mkdir(exist_ok=True)
        private.write_text('{"secret":"synthetic-test"}', encoding='utf-8')
        try:
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'audit_release.py'), str(ROOT)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('profile.json', proc.stdout)
        finally:
            private.unlink(missing_ok=True)

if __name__ == '__main__':
    unittest.main()
