import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_voice_gold", ROOT / "bin" / "validate_voice_gold.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VoiceGoldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.release = Path(self.tmp.name) / "v1.0"
        shutil.copytree(ROOT / "evaluation" / "gold" / "v1.0", self.release)

    def tearDown(self):
        self.tmp.cleanup()

    def test_checked_in_release_is_valid(self):
        self.assertEqual(MODULE.validate(self.release), [])

    def test_detects_quote_offset_drift(self):
        path = self.release / "decisions" / "ordinary.annotations.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["statements"][0]["spans"][0]["start"] += 1
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("round-trip" in error for error in MODULE.validate(self.release)))

    def test_detects_split_leakage(self):
        path = self.release / "manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["splits"]["test"].append("ordinary")
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("splits" in error for error in MODULE.validate(self.release)))


if __name__ == "__main__":
    unittest.main()
