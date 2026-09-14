#!/usr/bin/env python3
"""Validate a versioned voice-first gold release without external packages."""

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

ROLES = {"claimant", "respondent", "first_instance_decider", "recommender",
         "decider", "dissenter", "witness", "quoted_authority", "document_narrator"}
STATUSES = {"adopted", "rejected", "recommended", "not_adopted", "contested", "reported", "unclear"}
KINDS = {"factual_allegation", "factual_finding", "legal_interpretation",
         "recommendation", "operative_conclusion", "procedural_history"}
REASONS = {"heading", "page_header_footer", "signature", "administrative_metadata",
           "table_decoration", "other_non_material"}


def validate(root: Path) -> list[str]:
    errors = []
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest: {exc}"]
    ids = [item.get("decision_id") for item in manifest.get("decisions", [])]
    if len(ids) != len(set(ids)):
        errors.append("manifest: duplicate decision_id")
    split_ids = [item for values in manifest.get("splits", {}).values() for item in values]
    if len(split_ids) != len(set(split_ids)) or set(split_ids) != set(ids):
        errors.append("manifest: splits must be disjoint and cover every decision")

    for item in manifest.get("decisions", []):
        did = item.get("decision_id", "<missing>")
        try:
            raw = (root / item["source"]).read_bytes()
            text = raw.decode("utf-8")
            ann = json.loads((root / item["annotations"]).read_text(encoding="utf-8"))
        except (KeyError, OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{did}: cannot load files: {exc}")
            continue
        if text != unicodedata.normalize("NFC", text) or "\r" in text:
            errors.append(f"{did}: source is not NFC/LF normalized")
        if hashlib.sha256(raw).hexdigest() != item.get("sha256"):
            errors.append(f"{did}: source SHA-256 mismatch")
        if ann.get("decision_id") != did:
            errors.append(f"{did}: annotation decision_id mismatch")
        statement_ids = set()
        for statement in ann.get("statements", []):
            sid = statement.get("statement_id", "<missing>")
            if sid in statement_ids:
                errors.append(f"{did}/{sid}: duplicate statement ID")
            statement_ids.add(sid)
            if not statement.get("asserted_speaker"):
                errors.append(f"{did}/{sid}: asserted_speaker must be non-empty")
            if statement.get("procedural_role") not in ROLES:
                errors.append(f"{did}/{sid}: unknown procedural_role")
            if statement.get("adoption_status") not in STATUSES:
                errors.append(f"{did}/{sid}: unknown adoption_status")
            if statement.get("statement_kind") not in KINDS:
                errors.append(f"{did}/{sid}: unknown statement_kind")
            _check_spans(text, statement.get("spans"), f"{did}/{sid}", errors)
        for excluded in ann.get("excluded_spans", []):
            xid = excluded.get("exclusion_id", "<missing>")
            if excluded.get("reason") not in REASONS:
                errors.append(f"{did}/{xid}: unknown exclusion reason")
            _check_spans(text, [excluded], f"{did}/{xid}", errors)
    return errors


def _check_spans(text, spans, label, errors):
    if not spans:
        errors.append(f"{label}: at least one span is required")
        return
    for span in spans:
        start, end = span.get("start"), span.get("end")
        exact = span.get("text_exact")
        if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(text):
            errors.append(f"{label}: invalid half-open span")
        elif text[start:end] != exact:
            errors.append(f"{label}: span does not round-trip")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release", type=Path)
    args = parser.parse_args()
    errors = validate(args.release)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print(f"valid voice gold release: {args.release}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
