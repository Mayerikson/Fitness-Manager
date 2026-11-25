import tempfile
import unittest
from pathlib import Path

from scripts.audit_release import audit


class ReleaseAuditTests(unittest.TestCase):
    def test_python_cache_directory_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("scripts/fitness_manager.py scripts/audit_release.py tests", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "fitness_manager.py").write_text("# cli", encoding="utf-8")
            (root / "scripts" / "audit_release.py").write_text("# audit", encoding="utf-8")
            (root / "tests").mkdir()
            cache = root / "pkg" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "module.cpython-313.pyc").write_bytes(b"cache")
            issues = audit(root)
            self.assertTrue(any("Python cache directory" in issue for issue in issues))

    def test_clean_minimal_tree_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("scripts/fitness_manager.py scripts/audit_release.py tests", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "fitness_manager.py").write_text("# cli", encoding="utf-8")
            (root / "scripts" / "audit_release.py").write_text("# audit", encoding="utf-8")
            (root / "tests").mkdir()
            self.assertEqual(audit(root), [])


if __name__ == "__main__":
    unittest.main()
