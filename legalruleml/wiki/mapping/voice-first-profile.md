# Voice-first statement profile

The **`voice-first`** profile is a lightweight extraction profile for answering
three questions before attempting formalization: **who said what, in what
procedural capacity, and did the decision adopt it?** It preserves searchable
natural-language propositions and exact source spans. It does not produce
LegalRuleML.

Use this profile when statement-level attribution and retrieval are the desired
output, or as an optional precursor to the separate [`formal-rules`](#relationship-to-formal-rules)
profile. Do not infer that a statement is a rule merely because it discusses
law.

## Output shape

Emit one JSON object whose properties are statement IDs and whose values are
statement records. There is **one keyed record per material statement**. The
top-level key and the record's `statement_id` MUST be identical, and both MUST
be unique within the document output.

```json
{
  "stmt-0042": {
    "statement_id": "stmt-0042",
    "document_id": "vedtak-2026-17",
    "speaker_id": "sekretariatet",
    "procedural_role": "recommender",
    "statement_kind": "legal_interpretation",
    "assertion_text": "The ferry route is not public transport for purposes of the deduction rule.",
    "quote_exact": "Fergesambandet anses ikke som offentlig transport etter fradragsregelen.",
    "quote_start": 12844,
    "quote_end": 12916,
    "section_path": ["Sekretariatets vurderinger", "Rettslig vurdering"],
    "attribution_basis": "explicit_section_voice",
    "adoption_status": "recommended",
    "confidence": 0.97,
    "endorsed_by": ["skatteklagenemnda"]
  }
}
```

JSON strings use the source document's Unicode text. Offsets are zero-based
Unicode code-point offsets into the canonical document text; `quote_start` is
inclusive and `quote_end` is exclusive. Therefore
`document_text[quote_start:quote_end]` MUST equal `quote_exact`. Select the
smallest self-contained exact span that supports the assertion. Repeated or
overlapping spans are allowed when the source makes more than one material
statement in the same words.

## Record fields

| Field | Requirement | Meaning |
|---|---|---|
| `statement_id` | required string | Stable, document-local identifier; identical to the enclosing JSON key. |
| `document_id` | required string | Stable identity of the source decision or document. |
| `speaker_id` | required string | Stable identity of the person, body, party, majority, minority, or quoted authority responsible for the statement. Do not substitute the document author when the text names another voice. |
| `procedural_role` | required string | The speaker's capacity for this statement, for example `claimant`, `respondent`, `recommender`, `decider`, `dissenter`, `witness`, or `quoted_authority`. |
| `statement_kind` | required enum | The semantic class defined below. |
| `assertion_text` | required string | A faithful, stand-alone, searchable natural-language proposition. |
| `quote_exact` | required string | Verbatim source text supporting the proposition. |
| `quote_start` / `quote_end` | required non-negative integers | Inclusive start and exclusive end offsets for `quote_exact` in canonical document text. |
| `section_path` | required array of strings | Ordered heading path from the document root to the quote; use `[]` only when the source has no headings. |
| `attribution_basis` | required enum | Why `speaker_id` and `procedural_role` were assigned: `explicit_speaker`, `explicit_section_voice`, `quotation_or_citation`, `document_structure`, or `inferred`. Prefer the most direct basis. |
| `adoption_status` | required enum | `adopted`, `rejected`, `recommended`, `not_adopted`, `contested`, `reported`, or `unclear`. This describes treatment by the deciding voice, not truth. |
| `confidence` | required number | Extraction confidence from `0.0` to `1.0`, inclusive; it is not substantive confidence that the assertion is true. |
| `endorsed_by` | optional array of strings | Speaker IDs that expressly adopt or endorse this statement without becoming its original speaker. |
| `supersedes_statement_id` | optional string | ID of an earlier record in the same document whose proposition this statement expressly replaces or corrects. It is not a generic disagreement link. |

Unknown values are represented explicitly: use `unclear` for adoption, use
`inferred` plus a suitably reduced `confidence` for uncertain attribution, and
create a stable placeholder `speaker_id` rather than omitting a required field.
Do not use `endorsed_by` to erase the original voice.

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
3. Every exact quote round-trips against the canonical document text at the
   declared half-open offsets.
4. Assertions are faithful searchable propositions, not predicates, and retain
   material negation, quantities, dates, and qualifications.
5. The original speaker is preserved even when another voice endorses, rejects,
   or reports the statement.
6. Recommendations and operative conclusions remain distinct.

## See also

- [`vedtak-anatomy.md`](vedtak-anatomy.md) — likely voices and statement types
  by document section.
- [`../concepts/voices-and-attribution.md`](../concepts/voices-and-attribution.md)
  — the richer attribution model used by `formal-rules`.
- [`vedtak-to-legalruleml.md`](vedtak-to-legalruleml.md) — the `formal-rules`
  generation playbook.
