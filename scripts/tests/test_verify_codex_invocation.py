import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_codex_invocation import check_selftest


class TestCheckSelftest(unittest.TestCase):
    def test_license_optional(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "example-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: example-skill\ndescription: Example.\n---\n\nBody\n",
                encoding="utf-8",
            )
            (skill_dir / "LICENSE.txt").write_text("MIT\n", encoding="utf-8")
            result = check_selftest(skill_dir)
            self.assertEqual(result.status, "pass")


if __name__ == "__main__":
    unittest.main()
