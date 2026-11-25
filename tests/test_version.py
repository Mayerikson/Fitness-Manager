import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VersionTests(unittest.TestCase):
    def test_release_markers_are_aligned(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        init = (ROOT / "fitness_manager" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn(version, readme)
        self.assertIn(version, skill)
        self.assertIn(version, init)


if __name__ == "__main__":
    unittest.main()
