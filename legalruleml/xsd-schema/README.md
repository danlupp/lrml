# Vendored LegalRuleML 1.0 XSD schemas

Official OASIS schemas for validating our `.lrml` output, vendored so the
generation skill can validate offline without fetching them each run.

- Source: <https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/xsd-schema/>
  (LegalRuleML Core Specification v1.0, OASIS Standard, 30 Aug 2021).
  Downloaded 2026-07-03.
- `xml.xsd` is the W3C schema for the `xml:` namespace, from
  <https://www.w3.org/2009/01/xml.xsd>.

We vendor the **compact** dialect only — the project emits compact serialization
(`legalruleml/wiki/concepts/document-structure.md`).

## Local patches (for offline, warning-free validation)

Relative to the upstream files:

1. `compact/lrml-compact.xsd`, `compact/ruleml.xsd`,
   `datatypes/SimpleWithAttributes.xsd`: the `xs:import` of the `xml:` namespace
   points at `../xml.xsd` instead of `http://www.w3.org/2009/01/xml.xsd`.
2. `datatypes/SimpleWithAttributes.xsd`: dropped the `schemaLocation` on the
   `http://www.w3.org/2001/XMLSchema-datatypes` import (that URL is a namespace
   name, not a fetchable schema; an import without location is valid and stops
   xmllint's network error).

No element/type definitions were changed.

## Usage

```bash
xmllint --nonet --noout \
  --schema legalruleml/xsd-schema/compact/lrml-compact.xsd \
  samples/out/<name>.lrml
```

Exit code 0 = valid. Or run the full project validator (schema + keyref +
PROV-sidecar checks):

```bash
python3 legalruleml/bin/validate_lrml.py samples/out/<name>.lrml
```
