# Source manifests and quote locators

Every decision bundle has an immutable `<name>.source.json` manifest. It names
the source decision, records the exact normalized text used by extraction, and
commits to its UTF-8 bytes with SHA-256:

```json
{
  "schemaVersion": "1.0",
  "decisionId": "vedtak-2026-17",
  "sourceFile": "vedtak-2026-17.md",
  "normalizationPolicy": "unicode-nfc-lf-v1",
  "normalizedText": "Det følger …\n",
  "sha256": "<64 lowercase hexadecimal digits>"
}
```

`sourceFile` is relative to, and must remain within, the manifest directory.
The `unicode-nfc-lf-v1` policy decodes UTF-8, removes one leading Unicode BOM,
maps CRLF and CR line endings to LF, and applies Unicode NFC. The digest is
`sha256(normalizedText.encode("utf-8"))`. The source file is loaded and
normalized again during validation, so neither the file, captured text, nor
digest can change independently.

## Canonical quote locators

The sibling `<name>.voices.json` ledger is an envelope with `schemaVersion`, a
basename-only `sourceManifest` reference, and the profile's keyed `statements`:

```json
{
  "schemaVersion": "1.0",
  "sourceManifest": "vedtak-2026-17.source.json",
  "statements": {
    "stmt-0042": {
      "statement_id": "stmt-0042",
      "quote_spans": [
        {
          "quote_id": "quote-stmt-0042-a",
          "start": 12844,
          "end": 12916,
          "text": "Fergesambandet anses ikke som offentlig transport etter fradragsregelen.",
          "normalizationPolicy": "unicode-nfc-lf-v1"
        }
      ]
    }
  }
}
```

`start` is inclusive and `end` exclusive. They count Unicode code points from
the start of `normalizedText`; byte, page, and paragraph offsets are not
canonical. Each span must be non-empty, in range, and non-overlapping across
the ledger. Its `text` must equal `normalizedText[start:end]` byte-for-byte when
both are encoded as UTF-8. Page, paragraph, and section labels may be retained
beside a span solely as display metadata.

A non-contiguous excerpt is **multiple `quote_spans`**, each with its own text
and `quote_id`. Never manufacture a combined quote by inserting `[…]`, an
ellipsis, whitespace, or punctuation. Each `quote_id` names one
`<prov:Entity xml:id="…">`; that entity's `<prov:value>` must exactly equal the
validated span text.

Validate the source layer alone with:

```console
python3 legalruleml/bin/validate_source_bundle.py NAME.source.json NAME.voices.json NAME.prov.xml
```

`validate_lrml.py` automatically performs the same checks when either sibling
source artifact is present and requires the pair to be complete.

