import importlib.util
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
SPEC = importlib.util.spec_from_file_location(
    "validate_lrml", ROOT / "bin" / "validate_lrml.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VoiceProfileTests(unittest.TestCase):
    def setUp(self):
        MODULE.errors.clear()
        MODULE.warnings.clear()

    def test_default_profile_contains_role_semantics(self):
        profile = MODULE.load_voice_profile(MODULE.DEFAULT_VOICE_PROFILE)
        claimant = profile["roles"]["claimant"]
        self.assertTrue(claimant["searchableVoice"])
        self.assertTrue(claimant["directExpressionAttributionRequired"])
        self.assertIn("skattepliktig", claimant["norwegianLabels"])
        self.assertFalse(MODULE.errors)

    def test_custom_profile_makes_additional_role_substantive(self):
        payload = json.loads(MODULE.DEFAULT_VOICE_PROFILE.read_text())
        payload["roles"].append(
            {
                "stableRoleIdentifier": "expert",
                "norwegianLabels": ["sakkyndig"],
                "textualCues": ["sakkyndig uttaler"],
                "searchableVoice": True,
                "mayMakeOperativeFindings": False,
                "directExpressionAttributionRequired": True,
                "parentRole": None,
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            profile = MODULE.load_voice_profile(path)
        role = ET.fromstring(
            f'<Role xmlns="{MODULE.LRML}" key="role-expert" '
            'iri="https://example.org/roles#expert" />'
        )
        parsed = MODULE.VoiceRole(role, profile["roles"])
        self.assertTrue(parsed.substantive)
        self.assertTrue(parsed.direct_expression_required)

    def test_unknown_role_uses_profile_severity(self):
        profile = MODULE.load_voice_profile(MODULE.DEFAULT_VOICE_PROFILE)
        root = ET.fromstring(
            f'<LegalRuleML xmlns="{MODULE.LRML}"><Role key="role-observer" '
            'iri="https://example.org/roles#observer" /></LegalRuleML>'
        )
        roles = MODULE.collect_voice_roles(root, profile)
        MODULE.check_voices(root, {}, roles, profile, strict=False)
        self.assertTrue(
            any(
                "unknown role identifier 'observer'" in item for item in MODULE.warnings
            )
        )

        MODULE.warnings.clear()
        profile["unknownRoleSeverity"] = "error"
        MODULE.check_voices(root, {}, roles, profile, strict=False)
        self.assertTrue(
            any("unknown role identifier 'observer'" in item for item in MODULE.errors)
        )


if __name__ == "__main__":
    unittest.main()
