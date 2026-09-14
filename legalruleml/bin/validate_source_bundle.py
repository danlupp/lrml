#!/usr/bin/env python3
"""Validate immutable decision text and the quote spans in a voice ledger.

Usage: python3 legalruleml/bin/validate_source_bundle.py MANIFEST VOICE_LEDGER [PROV]

Offsets are zero-based, half-open Unicode code-point offsets in the normalized
text.  The files use the schema documented in
``wiki/mapping/source-manifest.md``.
"""

from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable

PROV = "http://www.w3.org/ns/prov#"
XML = "http://www.w3.org/XML/1998/namespace"
POLICY = "unicode-nfc-lf-v1"


def normalize_source(text: str, policy: str) -> str:
    """Apply the sole versioned source normalization policy."""
    if policy != POLICY:
        raise ValueError(f"unsupported normalizationPolicy {policy!r}")
    # Decode has already happened.  A leading BOM is transport metadata, not
    # document content; line endings are made platform independent before NFC.
    return unicodedata.normalize(
        "NFC", text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    )


def _object(path: Path, report: Callable[[str], None]) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report(f"{path.name}: cannot read JSON: {exc}")
        return None
    if not isinstance(value, dict):
        report(f"{path.name}: root must be an object")
        return None
    return value


def validate_source_bundle(
    manifest_path: Path,
    ledger_path: Path,
    prov_path: Path | None,
    report: Callable[[str], None],
) -> None:
    """Report every manifest, offset, quote, and PROV consistency error."""
    manifest = _object(manifest_path, report)
    ledger = _object(ledger_path, report)
    if manifest is None or ledger is None:
        return

    if manifest.get("schemaVersion") != "1.0":
        report("source manifest: schemaVersion must be '1.0'")
    if not isinstance(manifest.get("decisionId"), str) or not manifest["decisionId"]:
        report("source manifest: decisionId must be a non-empty string")
    policy = manifest.get("normalizationPolicy")
    if not isinstance(policy, str):
        report("source manifest: normalizationPolicy must be a string")
        return
    source_name = manifest.get("sourceFile")
    if not isinstance(source_name, str) or not source_name:
        report("source manifest: sourceFile must be a non-empty string")
        return
    source_path = (manifest_path.parent / source_name).resolve()
    try:
        source_path.relative_to(manifest_path.parent.resolve())
    except ValueError:
        report("source manifest: sourceFile must remain within the manifest directory")
        return
    try:
        raw = source_path.read_text(encoding="utf-8")
        normalized = normalize_source(raw, policy)
    except (OSError, UnicodeError, ValueError) as exc:
        report(f"source manifest: cannot load sourceFile {source_name!r}: {exc}")
        return

    recorded = manifest.get("normalizedText")
    if not isinstance(recorded, str):
        report("source manifest: normalizedText must be a string")
        return
    if normalized.encode("utf-8") != recorded.encode("utf-8"):
        report(
            "source manifest: normalizedText does not equal the normalized sourceFile"
        )
    expected_digest = hashlib.sha256(recorded.encode("utf-8")).hexdigest()
    if manifest.get("sha256") != expected_digest:
        report("source manifest: sha256 does not match normalizedText UTF-8 bytes")

    if ledger.get("sourceManifest") != manifest_path.name:
        report(f"voice ledger: sourceManifest must be {manifest_path.name!r}")
    if ledger.get("schemaVersion") != "1.0":
        report("voice ledger: schemaVersion must be '1.0'")
    statements = ledger.get("statements")
    if not isinstance(statements, dict):
        report("voice ledger: statements must be an object")
        return

    spans: list[tuple[int, int, str, str]] = []
    quote_text: dict[str, str] = {}
    for statement_id, statement in statements.items():
        if not isinstance(statement, dict):
            report(f"voice ledger: statement {statement_id!r} must be an object")
            continue
        values = statement.get("quote_spans")
        if not isinstance(values, list) or not values:
            report(
                f"voice ledger: statement {statement_id!r} must have non-empty quote_spans"
            )
            continue
        for index, span in enumerate(values):
            label = f"voice ledger: {statement_id}.quote_spans[{index}]"
            if not isinstance(span, dict):
                report(f"{label} must be an object")
                continue
            quote_id, start, end, text = (
                span.get(k) for k in ("quote_id", "start", "end", "text")
            )
            if span.get("normalizationPolicy") != policy:
                report(
                    f"{label}.normalizationPolicy must equal the source manifest policy"
                )
            if not isinstance(quote_id, str) or not quote_id:
                report(f"{label}.quote_id must be a non-empty string")
                continue
            if quote_id in quote_text:
                report(f"{label}: duplicate quote_id {quote_id!r}")
            if (
                not isinstance(start, int)
                or isinstance(start, bool)
                or not isinstance(end, int)
                or isinstance(end, bool)
            ):
                report(f"{label}: start and end must be integers")
                continue
            if start < 0 or end <= start:
                report(f"{label}: invalid half-open range [{start}, {end})")
                continue
            if end > len(recorded):
                report(
                    f"{label}: range [{start}, {end}) exceeds source length {len(recorded)}"
                )
                continue
            if not isinstance(text, str):
                report(f"{label}.text must be a string")
                continue
            extracted = recorded[start:end]
            if extracted.encode("utf-8") != text.encode("utf-8"):
                report(f"{label}.text does not equal normalizedText[{start}:{end}]")
            spans.append((start, end, label, quote_id))
            quote_text[quote_id] = text

    spans.sort()
    for previous, current in zip(spans, spans[1:]):
        if current[0] < previous[1]:
            report(f"voice ledger: overlapping spans {previous[2]} and {current[2]}")

    if prov_path is None:
        return
    try:
        root = ET.parse(prov_path).getroot()
    except (OSError, ET.ParseError) as exc:
        report(f"{prov_path.name}: cannot read PROV XML: {exc}")
        return
    prov_values: dict[str, str] = {}
    for entity in root.iter(f"{{{PROV}}}Entity"):
        quote_id = entity.get(f"{{{XML}}}id")
        value = entity.find(f"{{{PROV}}}value")
        if quote_id and value is not None:
            if quote_id in prov_values:
                report(f"PROV: duplicate <prov:Entity xml:id={quote_id!r}>")
            prov_values[quote_id] = "".join(value.itertext())
    for quote_id, text in quote_text.items():
        if quote_id not in prov_values:
            report(f"PROV: no <prov:Entity xml:id={quote_id!r}> for validated quote")
        elif prov_values[quote_id].encode("utf-8") != text.encode("utf-8"):
            report(
                f"PROV: <prov:value> for {quote_id!r} does not equal validated quote"
            )
    for quote_id in prov_values.keys() - quote_text.keys():
        report(f"PROV: entity {quote_id!r} has no corresponding validated quote span")


def main() -> int:
    if len(sys.argv) not in (3, 4):
        print(__doc__.strip().splitlines()[2])
        return 2
    failures: list[str] = []
    validate_source_bundle(
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        Path(sys.argv[3]) if len(sys.argv) == 4 else None,
        failures.append,
    )
    for failure in failures:
        print(f"ERROR {failure}")
    if failures:
        print(f"FAIL  source bundle: {len(failures)} error(s)")
        return 1
    print("OK    source bundle valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
