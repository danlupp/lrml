# Voice-first annotation and evaluation

This page is the normative annotation guide and evaluation contract for the
versioned voice-first gold set.  It is deliberately evaluated **by decision**,
never by treating paragraphs as independent examples.  The first published
fixture is [`../../evaluation/gold/v1.0/`](../../evaluation/gold/v1.0/).

## Annotation unit and workflow

Two annotators independently mark a complete normalized decision, then a third
adjudicator resolves differences.  Annotators may see headings and surrounding
text but may not see model output.  Record the guide version, annotator IDs and
adjudication state in the release manifest.  A decision stays out of the test
partition until adjudicated.

The unit is one **independently retrievable material proposition**.  Include
facts alleged or found, legal interpretations, recommendations, operative
conclusions, and material procedural events.  Split coordinated prose when its
propositions differ in speaker, role, kind, or adoption.  Keep negation,
conditions, amounts, dates, taxpayer identity, and outcome within the span that
makes the proposition self-contained.  The same source characters may support
more than one proposition; represent these as separate statements rather than
forcing one label.

Use zero-based, half-open Unicode-code-point offsets into the decision's NFC/LF
text.  `text[start:end]` must equal `text_exact`.  Choose the smallest contiguous
span that contains the complete proposition, including a local reporting clause
when it is required to identify the speaker.  Use multiple spans only when the
evidence is genuinely discontinuous.  Do not manufacture ellipses or silently
correct the source.  Nested quotation marks remain part of the exact span.

## Required labels

Each statement has:

* `spans`: one or more exact source locators;
* `asserted_speaker`: stable IDs for substantive originators (joint speakers are
  retained rather than collapsed to “taxpayer”);
* `procedural_role`: `claimant`, `respondent`, `first_instance_decider`,
  `recommender`, `decider`, `dissenter`, `witness`, `quoted_authority`, or
  `document_narrator`;
* `narrator`: the voice presenting the words in this document, or `null` for a
  voice speaking directly.  In indirect speech, “Sekretariatet opplyser at
  skattekontoret mente …” has the office as speaker and secretariat as narrator;
* `adoption_status`: `adopted`, `rejected`, `recommended`, `not_adopted`,
  `contested`, `reported`, or `unclear`;
* `endorsed_by`: only a voice that expressly adopts the proposition; and
* `statement_kind`: `factual_allegation`, `factual_finding`,
  `legal_interpretation`, `recommendation`, `operative_conclusion`, or
  `procedural_history`.

Attribution follows the proposition through layers of speech.  For nested
`Sekretariatet skrev: «Kontoret uttalte: ‘A er skattepliktig’.»`, A's
substantive speaker is the office and the immediate decision narrator is the
secretariat.  The typography is evidence, not another speaker.  A quotation of
a court or statute uses `quoted_authority` only when the quoted authority itself
asserts the proposition; a party's interpretation of it stays with the party.

An innstilling is `recommended`, not adopted merely because it appears in a
vedtak.  “Nemnda slutter seg til sekretariatets begrunnelse” adds the board to
`endorsed_by` and changes the referenced secretariat propositions to `adopted`;
it does **not** replace their original speaker.  Adoption of a result alone does
not imply adoption of every reason.  A majority is the `decider`; a minority is
the `dissenter`, and neither is silently attributed to the full board.

## Intentional exclusions

Annotate every reviewed but non-material range in `excluded_spans`, with
`reason` equal to `heading`, `page_header_footer`, `signature`,
`administrative_metadata`, `table_decoration`, or `other_non_material`.
Exclusions are not negative statements and never enter retrieval scoring.  Do
not exclude substantive prose merely because it is repetitive or difficult.
The union of statement spans, excluded spans, and permitted whitespace/punctuation
gaps provides a coverage audit; it is not a requirement to label every character.

## Frozen releases and splits

A release directory is immutable after publication.  Corrections create a new
semantic version and a changelog entry.  `manifest.json` fixes source SHA-256,
guide/schema versions, licenses/provenance, feature tags, and decision-level
`train`, `development`, and `test` membership.  No decision, near duplicate, or
same-case procedural installment may cross partitions.  Synthetic fixtures in
v1.0 exercise the contract; a production benchmark must add licensed,
de-identified representative decisions and publish its sampling frame.

Coverage is stratified at decision level across ordinary decisions,
recommendation-only documents, express adoption, indirect speech, nested
quotations, multiple taxpayers, procedural history, and majority/minority
opinions.  Report both micro totals and a macro mean over decisions, plus each
feature slice.  Never randomly split paragraphs from one decision.

## Matching and metrics

Match predictions to gold statements within the same decision with a one-to-one
maximum-weight bipartite assignment.  Span sets are compared as unions of
character intervals.  Prefer exact span-set matches, then maximize character
intersection-over-union (IoU), with stable IDs as the final tie-break.  An
**exact** match requires identical interval boundaries; an **overlap** match
requires IoU at least `0.5`.  Unmatched predictions are false positives and
unmatched gold statements are false negatives.  Report precision, recall, and
F1 for both exact and overlap matching, micro and decision-macro, with bootstrap
95% confidence intervals sampled by decision.

On overlap-matched pairs report exact-set accuracy for `asserted_speaker`,
accuracy for procedural role, adoption status, and statement kind, plus narrator
exact-set accuracy.  **Quote exact-match rate** is the fraction of gold
statements whose matched prediction has exactly the same ordered span texts and
boundaries.  **Unsupported-statement rate** is predictions with no valid
round-tripping span, or whose span has zero overlap with any material gold
statement, divided by all predictions.  Empty-output decisions remain in every
denominator where applicable.

For every procedural role, retrieval precision is matched predictions labelled
with that role divided by all predictions labelled with it; recall is matched
gold statements recovered with that role divided by all gold statements with
it.  Publish numerators and denominators, and mark rather than suppress roles
with zero support.

Cost telemetry is joined by decision ID.  Report the percentage of decisions
with at least one expensive-model call (and, separately, percentage of sections
and statements escalated).  Decision cost includes initial extraction, repair,
adjudication, failed calls, and provider charges; zero-call decisions cost zero.
Report arithmetic mean and p50, p90, p95, and p99 in a named currency and price
table version.  Percentiles use nearest-rank over per-decision total costs.

## Release gates

Evaluate the locked test decisions once configuration is frozen on development.
Before any richer LegalRuleML formalization is assessed, the candidate must meet
all voice-filter and quote gates:

| Gate | Threshold |
| --- | ---: |
| overlap span micro precision / recall / F1 | each >= 0.90 |
| exact span micro F1 | >= 0.80 |
| speaker and procedural-role accuracy | each >= 0.92 |
| adoption-status accuracy | >= 0.90 |
| per-role retrieval | precision and recall >= 0.80 for every role with >= 10 gold examples |
| quote exact-match rate | >= 0.95 |
| unsupported-statement rate | <= 0.01 |

In addition, no required metric may regress by more than two percentage points
from the previous released system, and every feature slice must have overlap F1
of at least 0.80.  Escalation and cost are reported constraints, not quality
substitutes; a deployment may set its own budget ceiling in advance.  Failure of
any gate blocks formal-rule evaluation and prompts error analysis at the
decision—not paragraph—level.
