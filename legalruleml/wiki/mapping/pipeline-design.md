# Bounded extraction pipeline

This page defines the production pipeline from a Norwegian *vedtak* to an
evidence-backed statement ledger and, optionally, LegalRuleML. The design
optimizes routine extraction for cost without allowing a model to invent text,
silently erase a procedural voice, or start an open-ended tool loop.

## Invariants and call budget

The orchestrator, not either model, owns control flow. Models receive text and
return data; they cannot call tools, fetch more context, recursively create
tasks, or decide to retry. For each detected section the hard budget is:

| Call | Maximum | Trigger |
| --- | ---: | --- |
| Low-cost extraction | 2 | One initial call and, only after validation failure, one repair call |
| Strong adjudication | 1 | At least one low-confidence or conflicting record survives deterministic validation |
| **Total** | **3** | The section is quarantined when this limit is exhausted |

No whole-document retry is permitted. A repair request contains only the
affected section, its validation errors, and the same output schema. A failed
adjudication is quarantined for human review; it never triggers another model
or tool call. Empty and oversized sections are also handled deterministically
(skip empty sections; split oversized sections at paragraph boundaries before
assigning each chunk its own budget).

Every accepted statement must have a speaker, a known procedural role, and at
least one exact, non-empty source span. Acceptance is therefore fail-closed:
unvalidated model output cannot enter the ledger or later compilation stages.

## 1. Reversible normalization

Decode the original UTF-8 bytes, remove at most one leading BOM, normalize line
endings to LF, and apply Unicode NFC, consistently with
[source-manifest.md](source-manifest.md). Retain both the immutable original
and normalized text and compute SHA-256 for each.

Normalization must also produce an **original-to-normalized offset map**. Store
it as ordered, gap-free segments with half-open ranges
`[original_start, original_end)` and `[normalized_start, normalized_end)` plus
the original and normalized substrings. Segments may be many-to-one (CRLF) or
many-to-many (Unicode composition); do not pretend every code point has a
one-to-one mapping. Include reverse indexes so either boundary can be mapped
back. When a boundary falls inside a non-bijective segment, return the entire
segment and an explicit ambiguity flag rather than guessing. Unit-test that
concatenating the segment substrings reconstructs both texts exactly.

All extraction spans use normalized Unicode-code-point offsets. The offset map
exists to reproduce and highlight the corresponding original material; it
does not replace the normalized source manifest as the canonical quote layer.

## 2. Sections and section-path priors

Detect headings with deterministic typography and numbering rules before any
model call. Preserve heading text and nesting, and assign every paragraph a
`section_path` from the document root to its most specific heading. Classify
paths into priors such as:

- `taxpayer_submissions` (*skattepliktiges anførsler*),
- `tax_office_decision` (*skattekontorets vedtak/vurdering*),
- `secretariat_assessment` (*sekretariatets vurdering/innstilling*),
- `board_decision` (*nemndas vedtak*),
- `majority`, and
- `minority`.

These are priors, not conclusions: they guide likely speaker and adoption
status but never fill a missing field or override explicit text. Retain the raw
heading, classifier rule/version, confidence, paragraph boundaries, and any
ambiguous candidate paths. A heading-classification ambiguity is eligible for
adjudication only when it affects a statement record.

## 3. Section-scoped structured extraction

Send exactly one section (or deterministic paragraph-bounded chunk) at a time
to the low-cost model. Require strict structured output with no free-text
envelope and reject unknown fields. At minimum each statement record contains:

```json
{
  "statement_id": "temporary-section-local-id",
  "statement_kind": "fact|argument|legal_interpretation|recommendation|decision",
  "speaker": "source-explicit actor label",
  "role": "claimant|first-instance-decider|recommender|decider|dissenter",
  "assertion": "searchable natural-language assertion",
  "adoption": "alleged|earlier-decision|recommended|adopted|rejected|dissent",
  "confidence": 0.0,
  "quote_spans": [{"start": 0, "end": 0, "text": "exact copied text"}]
}
```

Offsets are section-relative in the response and are converted to canonical
document-relative normalized offsets by the orchestrator. `quote_spans` must
contain copied, contiguous text—never paraphrases, repaired spelling,
synthetic ellipses, or Markdown decoration. Non-contiguous evidence requires
multiple spans. The prompt includes the allowed role and status vocabularies,
the section path and heading prior, the JSON Schema version, and the instruction
to return an empty record list when the section contains no material statement.

## 4. Exact-quote gate and local repair

Before semantic checks, verify for every span that `0 <= start < end <=
section_length` and that `section_text[start:end] == text` exactly. Then convert
the offsets to document coordinates and repeat equality against normalized
document text. Reject the entire affected record on any mismatch.

If the section has not used its one repair call, send that section—not the
document and not neighboring sections—back to the low-cost model with stable
error codes and the invalid record identifiers. Ask it to return a complete
replacement result for the section. Validate the replacement from scratch;
never splice an allegedly repaired quote into old output. Quarantine remaining
invalid records after attempt two.

## 5. Deterministic record validation

Run these checks without a model:

1. **Missing speaker:** reject a blank speaker; do not infer it from the prior.
2. **Unknown role:** reject values outside the controlled procedural-role map.
3. **Duplicate span:** within and across section results, flag identical
   document ranges; exact semantic duplicates proceed to deterministic merge,
   while competing analyses proceed to adjudication.
4. **Contradictory adoption flags:** flag incompatible statuses attached to the
   same speaker and semantic fingerprint, or to the same operative span.
5. **No evidence:** reject records without at least one quote span, including
   records whose spans were removed by quote validation.

Also validate the JSON Schema, enums, identifiers, confidence range, section
ownership, non-overlap rules, and source-manifest digest. Structural failures
are repairable only within the low-cost call budget. Records that are valid but
conflicting or below the configured confidence threshold are held for the next
stage and are not yet accepted.

## 6. Selective strong-model adjudication

Invoke the stronger model only for the held records, grouped by local conflict.
Supply the exact local paragraph, the immediately preceding and following
paragraphs when present, the raw and classified section path, all candidate
analyses, their evidence spans, and deterministic error/conflict codes. Do not
supply the entire vedtak unless those three paragraphs constitute it.

Strict output must select, amend, or reject each candidate and must return exact
evidence for every amended record. Run the quote gate and all deterministic
checks again. The adjudicator has one call per section and cannot request more
context or another call. High-confidence, non-conflicting records bypass it
entirely. An unresolved conflict or invalid adjudicator response is quarantined
for human review.

## 7. Deterministic merge

Merge only validated records. First group them by canonical source-span set
(sorted document-relative `(start, end, text)` tuples), then by a versioned
semantic fingerprint over normalized assertion, statement kind, speaker/role,
and adoption status. Normalize only documented superficial differences such as
Unicode NFC and whitespace; never erase negation, amounts, dates, actor
identity, role, or adoption status.

Exact fingerprints collapse deterministically to the lowest stable identifier
while retaining all extraction/adjudication provenance. Different fingerprints
on the same span remain distinct if compatible; if incompatible, they must have
been resolved or quarantined in stage 6. Sort final records by first source
offset and stable identifier so identical input produces byte-identical ledger
ordering.

## 8. Compile, do not re-extract

Treat the accepted ledger as the only input to output compilation. Always emit
the W3C PROV quote sidecar described in
[sources-isomorphism.md](../concepts/sources-isomorphism.md#vedtak-quotes): one
`prov:Entity` per exact span, `prov:value` equal to the normalized substring,
and derivations from generated fragments to evidence. Preserve a link to the
source manifest and offset-map artifact.

When the caller requests LegalRuleML, compile the **minimal** compact document
needed to express the accepted ledger: source/reference metadata, procedural
Actor/Role attribution, statement nodes, associations, and only the contexts
needed for recorded adoption or dissent. Do not invent rules, vilkår, hjemmel,
temporal parameters, or conclusions absent from accepted records. LegalRuleML
and PROV must pass the project validators before atomic persistence; otherwise
quarantine the bundle without partial output. Follow the detailed compilation
rules in [vedtak-to-legalruleml.md](vedtak-to-legalruleml.md).

## Cost and audit ledger

Append one immutable event for every model call, validation pass, retry,
escalation, quarantine, merge, and compilation. At minimum record:

- run, document, normalized-source digest, section/chunk, and attempt IDs;
- model/provider identifier and tier, prompt-template version, JSON Schema
  version, section-classifier version, and semantic-fingerprint version;
- input, cached-input, output, reasoning (when reported), and total token usage;
- latency and provider-reported cost or the price-table version used to compute
  it;
- validation result plus stable failure codes (including quote mismatches,
  missing speaker, unknown role, duplicate span, contradictory adoption, and
  no evidence); and
- escalation reason, candidate IDs, adjudication outcome, and quarantine reason.

Record zero-call sections too, so cost analysis can distinguish deterministic
skips from missing telemetry. Redact credentials and provider request IDs that
are not approved for storage, but never omit model, prompt version, token
usage, validation failures, or escalation reason. Aggregate costs from this
ledger; model prose is never the source of billing or validation truth.

## End-to-end termination rule

For each section the state machine is finite:

`normalized → sectioned → extract-1 → [accept | extract-2] → [accept |
adjudicate-1 | quarantine] → [accept | quarantine] → merge → compile`.

Only the orchestrator advances states, every transition is logged, and no edge
returns to an earlier state. This prohibition on open-ended loops is a safety,
latency, and cost invariant—not merely a prompting preference.
