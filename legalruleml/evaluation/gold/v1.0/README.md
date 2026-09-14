# Vedtak voice gold v1.0.0

This immutable, synthetic fixture release demonstrates the annotation and split
contract in the [normative guide](../../../wiki/mapping/voice-first-annotation-and-evaluation.md).
It is suitable for validator and scorer development, not for estimating
production accuracy: the latter requires a separately licensed, adjudicated,
representative sample of real decisions.

`manifest.json` pins decision-level splits, hashes, versions, provenance, and
feature coverage. Each normalized UTF-8 `.txt` has one sibling adjudicated
`.annotations.json`. Never move paragraphs between splits. Run:

```bash
python3 legalruleml/bin/validate_voice_gold.py legalruleml/evaluation/gold/v1.0
```

Corrections must be released in a new semantic-version directory; do not mutate
this directory after publication.
