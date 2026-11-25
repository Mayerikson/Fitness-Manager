import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fitness_manager.py"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = os.environ.copy()
        self.env["FITNESS_MANAGER_HOME"] = self.temp.name
        self.env.pop("FITNESS_MANAGER_DB", None)

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, msg=result.stdout + result.stderr)
        return result.stdout

    def test_init_weigh_in_measure_report(self):
        self.run_cli("init")
        self.run_cli("weigh-in", "--weight", "72.4", "--date", "2025-01-10")
        self.run_cli("measure", "--kind", "waist", "--value", "83", "--unit", "cm", "--date", "2025-01-10")
        output = self.run_cli("report")
        self.assertIn("72.4 kg", output)
        self.assertIn("83.0 cm", output)
        audit = self.run_cli("audit", "--limit", "10")
        self.assertIn("measurements", audit)

    def test_measure_without_date_uses_today(self):
        from datetime import date
        self.run_cli("init")
        self.run_cli("measure", "--kind", "waist", "--value", "83", "--unit", "cm")
        output = self.run_cli("report")
        self.assertIn(f"83.0 cm", output)
        conn = sqlite3.connect(Path(self.temp.name) / "fitness_manager.sqlite")
        try:
            row = conn.execute("SELECT measured_at FROM measurements WHERE kind='waist'").fetchone()
        finally:
            conn.close()
        self.assertEqual(row[0], date.today().isoformat())

    def test_run_and_food_logging(self):
        self.run_cli("init")
        output = self.run_cli("run", "--distance-km", "3", "--duration-min", "24", "--date", "2025-01-10")
        self.assertIn("8:00/km", output)
        self.run_cli("food", "--meal", "lunch", "--food", "rice", "--quantity-g", "150", "--date", "2025-01-10")

    def test_profile_is_stored_locally(self):
        self.run_cli("init")
        self.run_cli("profile", "set", "--sex", "male", "--age", "29", "--height-cm", "170", "--goal", "fat_loss", "--goal", "running_up_to_15_km")
        output = self.run_cli("profile", "show")
        self.assertIn('"height_cm": 170.0', output)
        self.assertIn("running_up_to_15_km", output)

    def test_run_over_15_km_is_rejected(self):
        self.run_cli("init")
        self.run_cli("run", "--distance-km", "16", "--duration-min", "100", expected=2)


if __name__ == "__main__":
    unittest.main()
