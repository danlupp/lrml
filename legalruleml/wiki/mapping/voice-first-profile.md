# Voice-first statement profile

The **`voice-first`** profile is a lightweight extraction profile for answering
questions before attempting formalization: **who is substantively responsible,
who narrates it, in what procedural capacity, and who later adopts it?** It
preserves searchable
natural-language propositions and exact source spans. It does not produce
LegalRuleML.

Use this profile when statement-level attribution and retrieval are the desired
output, or as an optional precursor to the separate [`formal-rules`](#relationship-to-formal-rules)
profile. Do not infer that a statement is a rule merely because it discusses
law.

For gold annotation, decision-level evaluation metrics, and the release gates
that must pass before formal-rule evaluation, follow the
[annotation and evaluation contract](voice-first-annotation-and-evaluation.md).

## Output shape

The ledger is stored as `<name>.voices.json` and MUST use the source-manifest
envelope and quote-span format defined in
[source manifests and quote locators](source-manifest.md). The abbreviated
statement map below illustrates statement fields; in a file it belongs under
the envelope's `statements` property.

Emit one JSON object whose properties are statement IDs and whose values are
statement records. There is **one keyed record per material statement**. The
top-level key and the record's `statement_id` MUST be identical, and both MUST
be unique within the document output.

```json
{
  "stmt-0042": {
    "statement_id": "stmt-0042",
    "document_id": "vedtak-2026-17",
    "asserted_by": ["sekretariatet"],
    "reported_by": [],
    "procedural_role": "recommender",
    "statement_kind": "legal_interpretation",
    "assertion_text": "The ferry route is not public transport for purposes of the deduction rule.",
    "quote_spans": [{
      "quote_id": "quote-stmt-0042-a",
      "start": 12844,
      "end": 12916,
      "text": "Fergesambandet anses ikke som offentlig transport etter fradragsregelen.",
      "normalizationPolicy": "unicode-nfc-lf-v1"
    }],
    "section_path": ["Sekretariatets vurderinger", "Rettslig vurdering"],
    "attribution_basis": [
      {
        "value": "section_heading",
        "relation": "asserted_by",
        "voice_id": "sekretariatet",
        "evidence_text": "Sekretariatets vurderinger",
        "evidence_start": 12602,
        "evidence_end": 12629
      },
      {
        "value": "document_structure",
        "relation": "asserted_by",
        "voice_id": "sekretariatet",
        "evidence_text": "Fergesambandet anses ikke som offentlig transport etter fradragsregelen.",
        "evidence_start": 12844,
        "evidence_end": 12916
      }
    ],
    "adoption_status": "recommended",
    "confidence": 0.97,
    "endorsed_by": []
  }
}
```

JSON strings use the manifest's immutable normalized Unicode text. Offsets are
document-relative, zero-based Unicode code-point offsets. Select the smallest
self-contained exact span that supports the assertion. Quote spans MUST NOT
overlap; records may refer to the same `quote_id` only through a separate
non-locator reference added by a consumer.

## Record fields

| Field | Requirement | Meaning |
|---|---|---|
| `statement_id` | required string | Stable, document-local identifier; identical to the enclosing JSON key. |
| `document_id` | required string | Stable identity of the source decision or document. |
| `asserted_by` | required non-empty array of strings | Voice(s) to which the proposition is substantively attributed. Use stable IDs for the person, body, party, majority, minority, or quoted authority. Joint assertions may have several voices. |
| `reported_by` | required array of strings | Document voice(s) that narrate, quote, or paraphrase another voice's proposition. Use `[]` when the source presents the assertion directly. Reporting does not transfer substantive responsibility. |
| `procedural_role` | required string | The asserting voice's capacity for this statement, for example `claimant`, `respondent`, `recommender`, `decider`, `dissenter`, `witness`, or `quoted_authority`. |
| `statement_kind` | required enum | The semantic class defined below. |
| `assertion_text` | required string | A faithful, stand-alone, searchable natural-language proposition. |
| `quote_spans` | required non-empty array | Contiguous verbatim source spans. Each records unique `quote_id`, `start`, `end`, `text`, and `normalizationPolicy`; see [the locator specification](source-manifest.md). |
| `section_path` | required array of strings | Ordered heading path from the document root to the quote; use `[]` only when the source has no headings. |
| `attribution_basis` | required non-empty array of objects | Independent reasons for the voice relations. Each object has `value`, `relation`, `voice_id`, `evidence_text`, `evidence_start`, and `evidence_end`; `relation` names one of the three voice fields and `voice_id` MUST occur in that field. The half-open evidence offsets use the same canonical text as the quote. Allowed values are `direct_quote`, `explicit_reporting_clause`, `section_heading`, `document_structure`, and `inferred`. |
| `adoption_status` | required enum | `adopted`, `rejected`, `recommended`, `not_adopted`, `contested`, `reported`, or `unclear`. This describes treatment by the deciding voice, not truth. |
| `confidence` | required number | Extraction confidence from `0.0` to `1.0`, inclusive; it is not substantive confidence that the assertion is true. |
| `endorsed_by` | required array of strings | Later voice(s) that expressly adopt this proposition without becoming its original asserting or reporting voice. Use `[]` when there is no express adoption. |
| `supersedes_statement_id` | optional string | ID of an earlier record in the same document whose proposition this statement expressly replaces or corrects. It is not a generic disagreement link. |

Unknown values are represented explicitly: use `unclear` for adoption, use an
`inferred` basis plus a suitably reduced `confidence` for uncertain attribution,
and create a stable placeholder voice ID rather than omitting `asserted_by`.
The three voice relations are independent: a voice may occur in more than one
when the text genuinely gives it more than one function, but reporting and
endorsement never implicitly add that voice to `asserted_by`.

Evidence spans need not equal a quote span. For example, the proposition may
occur beneath a heading, while the heading itself supplies one attribution
basis. Every evidence span MUST independently round-trip against the canonical
document text. Record all material bases rather than selecting only the
strongest one; an explicit reporting clause and a section heading can therefore
both support the same relation. `inferred` is a last resort and its evidence
should capture the contextual text that made the inference possible.
Use `direct_quote` when quotation marks or an equivalent block quotation
directly identify a voice's words; use `explicit_reporting_clause` for clauses
such as “anfører at”, “uttalte at”, and “sluttet seg til”; use
`section_heading` when a heading names the voice; and use `document_structure`
when authorship follows from the document's established section layout.

## Statement kinds

`statement_kind` has these values:

- **`factual_allegation`** — a party or other voice asserts a fact that the
  deciding body has not established in this statement.
- **`factual_finding`** — the deciding or fact-finding voice determines a fact.
- **`legal_interpretation`** — a proposition about the meaning, scope,
  applicability, or legal effect of a source or legal concept.
- **`recommendation`** — a proposed disposition or course of action, including
  a secretariat's innstilling, rather than the operative decision itself.
- **`operative_conclusion`** — the decision's disposition or other text that
  itself grants, denies, orders, annuls, remands, or otherwise resolves an
  issue.
- **`procedural_history`** — a material event in the matter's procedural
  sequence, such as an earlier decision, appeal, notice, or remand.

Split a passage into multiple records when it contains independently material
propositions with different kinds, speakers, roles, adoption states, or useful
retrieval targets. Do not split away qualifications that change the meaning of
the proposition.

## Writing `assertion_text`

`assertion_text` is **not a RuleML predicate**, identifier, or compressed label.
Write a grammatical proposition that remains faithful to `quote_exact`, names
the relevant subject and qualification, and can be found through ordinary
full-text or semantic search. Resolve pronouns only where the surrounding text
makes the referent clear; do not add facts or legal implications.

Prefer:

> The Appeals Board found that the taxpayer travelled 48 days in 2022.

Do not write:

> `travelDays(taxpayer, 48, 2022)`

Nor should `assertion_text` silently promote an allegation to a finding. Voice,
procedural role, kind, and adoption are separate dimensions and must all be
recorded.

## Attribution examples

These abbreviated records omit unchanged required fields and illustrative
offsets. Production records include exact, round-tripping quote and evidence
spans.

### Party submission: “Skattepliktige anfører at …”

For `Skattepliktige anfører at reisen var yrkesreise`, attribute the proposition
to the taxpayer and the reporting clause to the document voice:

```json
{
  "asserted_by": ["skattepliktige"],
  "reported_by": ["sekretariatet"],
  "endorsed_by": [],
  "attribution_basis": [
    {"value": "explicit_reporting_clause", "relation": "asserted_by", "voice_id": "skattepliktige", "evidence_text": "Skattepliktige anfører at", "evidence_start": 410, "evidence_end": 438},
    {"value": "document_structure", "relation": "reported_by", "voice_id": "sekretariatet", "evidence_text": "Sekretariatets fremstilling", "evidence_start": 350, "evidence_end": 376}
  ]
}
```

`reported_by` identifies whoever authored that passage (here, the secretariat),
not automatically the deciding board or the document as an abstract object.

### Secretariat summary of the tax office

Under a secretariat-authored section that paraphrases the tax office, use
`asserted_by: ["skattekontoret"]` and `reported_by: ["sekretariatet"]`.
Preserve both an `explicit_reporting_clause` span such as “Skattekontoret la til
grunn at” and a `section_heading` or `document_structure` span when both help
establish the narrator. Do not attribute the office's conclusion substantively
to the secretariat merely because the secretariat summarizes it.

### Express endorsement

For `Nemnda sluttet seg til sekretariatets innstilling`, the proposition in the
innstilling remains `asserted_by: ["sekretariatet"]`, can be
`reported_by: ["nemnda"]` when the board's text recounts it, and has
`endorsed_by: ["nemnda"]`. Anchor “sluttet seg til” as an
`explicit_reporting_clause` basis for the narration and express adoption. Do
not rewrite the earlier proposition as though the board originally asserted it.

### Majority and minority opinions

Give the majority and minority stable, distinct voice IDs. A proposition under
“Flertallet” may use `asserted_by: ["nemnd-flertall"]` with a `section_heading`
basis; a contrary proposition under “Mindretallet” uses
`asserted_by: ["nemnd-mindretall"]`. Neither voice reports or endorses the other
unless the text expressly does so. Membership in the final document alone is
not endorsement by the full board.

### Unattributed background narration

Background prose with no named source still needs an asserting voice. Use the
stable document-narrator placeholder (for example `vedtak-narrator`) in
`asserted_by`, leave `reported_by` and `endorsed_by` empty, and supply
`document_structure` or, if responsibility truly cannot be established,
`inferred` evidence with reduced confidence. Do not silently assign the
background proposition to the board, secretariat, or taxpayer.

## Relationship to `formal-rules`

The existing vedtak-to-LegalRuleML pipeline remains a separate profile named
**`formal-rules`**. It emits and validates LegalRuleML plus its provenance,
relation, and conflict artifacts. Choosing `voice-first` neither invokes nor
claims conformance with that pipeline.

The `voice-first` profile does **not require**:

- full RuleML rules or LegalRuleML XML;
- relation manifests or canonical predicate signatures;
- hjemmel decomposition or fragment-to-provision Associations;
- temporal rule parameters or version-selection Contexts;
- conflict reasoning or conflict artifacts; or
- DOT/SVG rendering.

These exclusions are scope boundaries, not prohibitions. A consumer may later
promote reviewed voice-first records into `formal-rules`, but it must then run
that profile's complete modelling and validation workflow rather than treating
the JSON records as formal rules.

## Review checks

1. Every material statement has exactly one keyed record; the same exact quote
   may support multiple independently material statement records.
2. Every top-level key equals its `statement_id`, and all referenced
   `supersedes_statement_id` values resolve.
3. Every exact quote and every attribution evidence span round-trips against the
   manifest's canonical document text at the declared half-open offsets; quote
   spans are non-overlapping and PROV values match their spans byte-for-byte.
4. Assertions are faithful searchable propositions, not predicates, and retain
   material negation, quantities, dates, and qualifications.
5. `asserted_by`, `reported_by`, and `endorsed_by` are evaluated independently;
   narration or endorsement never erases or silently changes substantive
   attribution.
6. Recommendations and operative conclusions remain distinct.

## See also

- [`vedtak-anatomy.md`](vedtak-anatomy.md) — likely voices and statement types
  by document section.
- [`../concepts/voices-and-attribution.md`](../concepts/voices-and-attribution.md)
  — the richer attribution model used by `formal-rules`.
- [`vedtak-to-legalruleml.md`](vedtak-to-legalruleml.md) — the `formal-rules`
  generation playbook.
