import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parents[1] / "bin"
sys.path.insert(0, str(BIN))

from validate_source_bundle import POLICY, validate_source_bundle  # noqa: E402


class SourceBundleTests(unittest.TestCase):
    def write_bundle(self, directory: Path, *, start=0, end=4, quote="Café"):
        (directory / "decision.txt").write_bytes(b"\xef\xbb\xbfCafe\xcc\x81\r\nrest")
        normalized = "Café\nrest"
        manifest = {
            "schemaVersion": "1.0",
            "decisionId": "decision",
            "sourceFile": "decision.txt",
            "normalizationPolicy": POLICY,
            "normalizedText": normalized,
            "sha256": hashlib.sha256(normalized.encode()).hexdigest(),
        }
        ledger = {
            "schemaVersion": "1.0",
            "sourceManifest": "decision.source.json",
            "statements": {
                "stmt-1": {
                    "statement_id": "stmt-1",
                    "quote_spans": [
                        {
                            "quote_id": "quote-1",
                            "start": start,
                            "end": end,
                            "text": quote,
                            "normalizationPolicy": POLICY,
                        }
                    ],
                }
            },
        }
        (directory / "decision.source.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (directory / "decision.voices.json").write_text(
            json.dumps(ledger), encoding="utf-8"
        )
        (directory / "decision.prov.xml").write_text(
            '<prov:Bundle xmlns:prov="http://www.w3.org/ns/prov#" '
            'xmlns:xml="http://www.w3.org/XML/1998/namespace">'
            '<prov:Entity xml:id="quote-1"><prov:value>Café</prov:value></prov:Entity>'
            "</prov:Bundle>",
            encoding="utf-8",
        )

    def validate(self, directory: Path):
        failures = []
        validate_source_bundle(
            directory / "decision.source.json",
            directory / "decision.voices.json",
            directory / "decision.prov.xml",
            failures.append,
        )
        return failures

    def test_valid_bundle_normalizes_bom_line_endings_and_nfc(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_bundle(directory)
            self.assertEqual(self.validate(directory), [])

    def test_rejects_out_of_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_bundle(directory, end=99)
            failures = self.validate(directory)
            self.assertTrue(any("exceeds source length" in item for item in failures))

    def test_rejects_prov_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_bundle(directory)
            prov = directory / "decision.prov.xml"
            prov.write_text(prov.read_text().replace("Café", "Cafe"), encoding="utf-8")
            failures = self.validate(directory)
            self.assertTrue(
                any("does not equal validated quote" in item for item in failures)
            )

    def test_rejects_overlapping_spans(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_bundle(directory)
            path = directory / "decision.voices.json"
            ledger = json.loads(path.read_text())
            ledger["statements"]["stmt-2"] = {
                "quote_spans": [
                    {
                        "quote_id": "quote-2",
                        "start": 1,
                        "end": 3,
                        "text": "af",
                        "normalizationPolicy": POLICY,
                    }
                ]
            }
            path.write_text(json.dumps(ledger))
            failures = self.validate(directory)
            self.assertTrue(any("overlapping spans" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
