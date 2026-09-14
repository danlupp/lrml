# Log

Append-only. Newest entries at the bottom. One line per event, prefixed so the
log is greppable: `grep "^## \[" log.md | tail -10`.

## [2026-06-25] init | Wiki created from tutorial.pdf + OASIS spec

- Ingested `in/tutorial.pdf` (*LegalRuleML: Design Principles and Foundations*)
  and the OASIS Standard HTML spec v1.0 (all of §§1–8 + annexes).
- Reviewed vedtak sources in `samples/in/` (`vedtak_frodo_ferge`,
  `vedtak_syntetisk_uenighet`, configs, `rettsinformasjon.json`) to anchor the
  mapping on the real source documents.
- Created schema ([AGENTS.md](AGENTS.md)), [index.md](index.md), and 12 concept
  pages covering the full language surface.
- Created the mapping playbook ([mapping/vedtak-to-legalruleml.md](mapping/vedtak-to-legalruleml.md)),
  a worked example for `vedtak_frodo_ferge`, vedtak anatomy, and patterns/pitfalls.
- Created reference cheatsheet and full vocabulary glossary.
- Adopted the modelling stance recorded in [AGENTS.md](AGENTS.md) (compact
  serialization, isomorphism-first, vilkår = rule body, dissent = Alternatives +
  Override, version selection via Context/TemporalCharacteristic).

## [2026-06-25] feature | Embed verbatim vedtak quotes (text isomorphism)

- Added the convention of embedding each fragment's exact vedtak passage as an
  inline `<lrml:Paraphrase>` on its Expression node (`Rule`/`Atom`/`Override`),
  plus declaring the vedtak as a `<lrml:LegalSource>` tied to the statements via
  an `<lrml:Association>`. Confirmed against spec §3.4/§5.14 (Paraphrase = NL
  rendering on Expression nodes; Source/Reference only point, never embed).
- Documented in [concepts/sources-isomorphism.md](concepts/sources-isomorphism.md#vedtak-quotes),
  added Step 6b to the [playbook](mapping/vedtak-to-legalruleml.md), a stance
  point in [AGENTS.md](AGENTS.md), and a step in the generation skill.
- Applied to `samples/out/vedtak_frodo_mordor.lrml` (14 Paraphrase quotes).

## [2026-07-02] change | Source quotes now use W3C PROV, replacing `<lrml:Paraphrase>`

- Adopted the [W3C PROV](https://www.w3.org/TR/prov-overview/) vocabulary for
  text isomorphism: each quote is a reusable `<prov:Entity>` in a `<prov:Bundle>`
  (`<prov:value>` + `<prov:wasQuotedFrom>` edge to its `<lrml:LegalSource>`), and
  every Expression node (`Rule`/`Atom`/`Override`) references its anchor with a
  `prov:wasDerivedFrom` attribute. Keeps the quote layer out of the logic, lets a
  quote be reused/shared, and records the quote's own provenance (statutory text
  → provision source; a finding → vedtak source).
- Reason to move off `<lrml:Paraphrase>`: it inlines the quote inside the logic
  and cannot say *which* source the text was quoted from. PROV separates the two.
- Updated [concepts/sources-isomorphism.md §vedtak-quotes](concepts/sources-isomorphism.md#vedtak-quotes),
  the [playbook](mapping/vedtak-to-legalruleml.md) (Step 6b + decision table +
  Step 10 validation), [patterns-and-pitfalls.md](mapping/patterns-and-pitfalls.md)
  (P11 + broken-anchor pitfall), [AGENTS.md](AGENTS.md) (stance 9 + prov prefix),
  the [element cheatsheet](reference/element-cheatsheet.md), and the generation
  skill (`SKILL.md`).
- Canonical example: the hand-enriched
  [`samples/in/vedtak_frodo_mordor.lrml`](../../samples/in/vedtak_frodo_mordor.lrml);
  the `soksbie` tool already ingests this PROV shape.

## [2026-07-03] note | Historical vedtak may cite hjemler absent from rettsinformasjon.json

- When `rettsinformasjon.json` lacks aliases for older income-tax or treaty provisions cited in a vedtak, preserve isomorphism by creating `LegalReference` entries from the vedtak's verbatim citations with `refIDSystemName="vedtak-aliaser"`, while still anchoring quotes to declared `LegalSource` nodes.
- 2026-07-03: When a provided Skatteklagenemnda vedtak lacks a matching *.config.json, model cited mval/fmva/sktfvl provisions from the vedtak text with `vedtak-aliaser`, and note/fallback if Graphviz `dot` is unavailable after XSLT DOT generation.
- 2026-07-03: For mva transaction-cost vedtak, model § 8-1 as a positive `Right` only when the acquisition is registered/relevant/nær-og-naturlig and not linked to exempt turnover; model § 3-6(1)(e) share sales as a competing negative/prohibitive rule, with taxpayer/dissent classifications preserved as `Alternatives` and majority `Override`.
- 2026-07-03: Vedtak-to-LRML tasks should handle fetched Skatteklagenemnda markdown under samples/in/vedtak/ even when no matching *.config.json is present; record any inferred hjemler/config assumptions in the LRML comment.

## [2026-07-03] fix | Schema-conformance pass: wiki idioms corrected against the OASIS XSD; PROV moved to sidecar

- Validated `samples/out/*.lrml` against the official compact XSD and the spec's
  own `examples/compactified/*.lrml`; the wiki taught ~10 idioms the schema
  rejects. All pages corrected: `Prefix pre/refID` (not name/value; empty prefix
  → default xmlns); `LegalReference` has no `@key`, `@refersTo` *is* its internal
  NCName id; RuleML `@key`s must be CURIEs (`:t-2022`); `Data` in `Time` limited
  to dateTime/date/duration (no gYear); `TemporalCharacteristic` uses `atTime`
  (not hasTime) with `vocab#` status IRIs; the only Association/Context edges are
  appliesSource/TemporalCharacteristic(s)/Strength/Modality/Authority/Jurisdiction
  (+ appliesAssociation(s) on Context) — no appliesTemporal/Time/Role/Agent;
  Agents wire via `Role filledBy/forExpression`; `Alternatives` members are
  `hasAlternative` edges; Bearer/AuxiliaryParty are `ruleml:slot` keys, never
  wrappers; `FactualStatement` keeps an explicit `hasTemplate` and cannot hold a
  deontic (unconditional grants = empty-body PrescriptiveStatement); no
  `PrimaryDuty`/`CompensativeDuty` (SuborderList holds deontic specs directly);
  strength via `hasStrength` + `StrictStrength`/`DefeasibleStrength`/`Defeater`.
- **PROV quotes moved to a sidecar** `<name>.prov.xml` (embedded `prov:Bundle` /
  `prov:wasDerivedFrom` attributes made files XSD-invalid): quote entities +
  `wasDerivedFrom` records linking fragment keys to quotes. `.lrml` stays pure.
- Vendored the OASIS compact XSD (+ W3C xml.xsd, two import patches for offline
  use) at `legalruleml/xsd-schema/`; added `legalruleml/bin/validate_lrml.py`
  (XSD + key uniqueness/resolution/acyclicity + if/then + sidecar link checks)
  and made it the validation gate in the playbook, AGENTS.md stance 10, and the
  generation skill.
- Note: existing `samples/out/*.lrml` still use the old idioms and embedded PROV
  (they predate this pass and do not validate); `lrml_html.py` still reads the
  embedded-PROV shape and needs a follow-up to load sidecars.

## [2026-09-04] fix | Migrated all samples to schema-valid format; tools read the PROV sidecar

- Migrated every `samples/{in,out}/*.lrml` (20 files) to the schema-valid idioms
  above; each now validates with `legalruleml/bin/validate_lrml.py`. Quotes were
  extracted into `<name>.prov.xml` sidecars from **both** legacy shapes: the
  embedded `<prov:Bundle>` + `prov:wasDerivedFrom` attributes, and the older
  inline `<lrml:Paraphrase>` (rule text → provision `LegalSource`, findings →
  vedtak source, per the wiki convention). All 20 files have a sidecar; no
  `.lrml` contains PROV or Paraphrase any more.
- Isomorphism preserved: the old `LegalReference@refersTo` external id
  (`urn:rettskilde:…`/`lov:…`/`ri:…`) moved to a paired `LegalSource@sameAs`, and
  each Association citing the reference now also cites that source — so
  `søksbie`'s URN search still resolves.
- `lrml_html.py` and `søksbie` now load `<name>.prov.xml` (sidecar quotes feed
  node tooltips / statement search text); both keep the legacy embedded-PROV and
  Paraphrase paths for older inputs. Graph id handling now covers keyless
  `LegalReference` (`@refersTo`) and colon-stripped RuleML keys; the same two
  fixes were applied to `viz/lrml-to-dot.xsl`. Regenerated the committed
  `.lrml.html` / `.svg` / `.dot` artifacts. Full test suite + ruff + mypy clean.

## [2026-09-04] fix | Tilleggsskatt breach must be a FactualStatement, not a `<lrml:Violation>`

- Surfaced by the `vedtak-to-legalruleml-doc-feedback` skill on a dry run: a
  minimal tilleggsskatt file built by following the mapping guidance literally
  put the breach in a `<lrml:FactualStatement>` as `<lrml:Violation keyref=…/>`,
  which the XSD rejects — `Violation` is a member of `Deontic.Node.choice`
  (rule head/body), and a `FactualStatement`'s formula only admits
  `Atom`/`And`/`Or`/`Neg`/… . The canonical migrated
  `vedtak_endring…tilleggsskatt` sample confirms the intended pattern: it uses
  **no** `Violation` and asserts each breach as a domain-relation Atom
  (`:uriktigeEllerUfullstendigeOpplysninger`).
- Root cause = systematic doc gap: the tilleggsskatt *mapping* guidance said
  "model the breach as a `<lrml:Violation>`" (no container, no caveat), while the
  concept page already said `Violation` is a rule-body formula. Corrected the
  operational spots to say: assert the breach as an ordinary `FactualStatement`
  with a domain relation, and reserve `<lrml:Violation keyref>` for a rule that
  fires *on* the breach. Edited `mapping/vedtak-to-legalruleml.md` (Step 8 +
  decision table), `concepts/deontic.md` (Violation bullet + tilleggsskatt note),
  and the base skill step 8. Verified the corrected pattern validates.

## [2026-08-11] feature | Hjemmel anchoring — rules traceable to the paragraph, not the statute

- **Gap:** nothing tied a rule (or a single vilkår) to the *specific* provision
  it was read out of. Three defects: sources were minted per statute section
  (`§ 6-44-4`) though the URN register goes to `…:ledd:2:bokstav:b`; one
  `<lrml:Association>` lumped several provisions with a dozen statements, which
  the XSD defines as a **cross-product** ("each non-target entity is paired with
  every target entity") — `vedtak_frodo_ferge` asserted 3 × 13 rule↔hjemmel
  links, and `søksbie` materialized exactly that; and the statutory *wording*
  was nowhere, since a rule's PROV quote was quoted from the vedtak.
- **Added** `concepts/hjemmel-anchoring.md` as the normative page: pinpoint
  sources (never deeper than the text cites), one hjemmel per keyed Association,
  fragment-level anchoring via `@key` on an individual `<ruleml:Atom>`, and
  `quote-hjemmel-<stem>` sidecar entities carrying `wasQuotedFrom` to both the
  provision and the vedtak reproducing it. Verified against the vendored XSD
  that `@key` on `ruleml:Atom` and on `lrml:Association` is valid.
- **Validator:** `appliesSource` must name a source/reference (error); ≤1
  hjemmel per Association, every rule statement a direct target of one, every
  keyed fragment targeted (warnings; errors under `--strict`, which the skill
  now runs). `--hjemmel` prints the traceability table.
- **Samples:** retrofitted `vedtak_kort_FSFIN_6_44_4` (the vedtak cites
  *FSFIN § 6-44-1, 2 ledd* for nødvendighet and § 6-44-4 for the rest — the
  nødvendighet vilkår is now a keyed Atom anchored to the ledd) and
  `vedtak_frodo_ferge` (statement-level; its text cites no ledd, so none was
  invented). Registered the new pinpoint in `rettsreferanser.json`.
- **Consumers:** `søksbie` indexes a fragment-level link against its enclosing
  statement while keeping the fragment key (`vilkår=…` badge, TUI detail);
  `lrml_html.py` and `viz/lrml-to-dot.xsl` draw keyed Associations as single
  hubs and keyed vilkår atoms as nodes. Updated `sources-isomorphism.md`,
  `context-associations.md`, `identifiers.md`, the playbook, pitfalls,
  cheatsheet, worked example, index, and the base skill. Full suite green
  (53 tests, incl. new `tests/test_validate_lrml.py`).

## [2026-08-21] sample | Multi-year recommendation with a definition dispute

- Generated `vedtak_frodo_mordor` as `recommendation-only`: separate temporal
  contexts carry the 2022/2023 thresholds, while a recommendation Context
  selects the secretariat's legal reading and recommended outcomes. Competing
  definitions use `Alternatives` without `Override`; no decider is inferred
  from the document heading when the operative text only says `innstiller`.

## [2026-08-21] sample | BFU 2/03 velferdstiltak for ansatte

- Generated `samples/out/bfu/bfu_2_03_velferdstiltak_for_de_ansatte.lrml` as an operative BFU: innsender is claimant, Skattedirektoratet is decider, and the decision Context selects the Directorate's restrictive langhelg/feriereise reading. Added missing pinpoint references for skatteloven § 5-1 første ledd, § 5-15 annet ledd, and FSFIN § 5-15-6 første ledd to `samples/in/rettsreferanser.json`; strict/voice and hjemmel validation pass, and SVG was generated.

## [2026-08-27] feature | Document-local canonical relation manifests

- Promoted relation reconciliation from an existing-artifact-only review to a
  mandatory pre-emission inventory for every decision. The agent now builds one
  entity identity map and canonical relation vocabulary across all procedural
  voices, groups formulations by truth conditions, keeps polarity/status out of
  predicate names, and decomposes legally material qualifiers into separate
  Atoms over shared entities.
- Added the generated `<name>.relations.json` sidecar and opt-in validator gate
  `--relations`. The gate checks LRML hash freshness, exact IRI coverage,
  ordered argument signatures and concrete term kinds, statement usages,
  direct Role voices, and PROV-backed source formulations. New generation
  requires the gate; plain `--strict` remains compatible with legacy artifacts
  during migration. Conflict reasoning continues to use exact canonical LRML
  symbols and never performs heuristic alias merging.

## [2026-08-31] feature | Rettsregister legal-source identities

- Made Rettsrev/Rettsregister `resource_id` the preferred external identity for
  law and regulation `LegalSource@sameAs` values. The generator resolves a
  structured instrument plus section/article through the new `resolve-source`
  helper and never constructs a database ID from a legacy URN.
- Preserved the `rettsreferanser.json` URN as an explicit warning-backed
  fallback whenever Rettsrev is unavailable or does not resolve the citation.
  Rettsregister stops at section/article depth, while cited ledd/bokstav/punktum
  remain distinct local LegalReference/LegalSource and Association pinpoints.

## [2026-08-31] feature | Canonical SQLite model persistence

- Replaced category-scoped generated files as runtime state with one complete
  `legalruleml_model` row per Rettsrev decision in `build/legalruleml.sqlite`.
  Rettsrev identity is resolved from its schema-v2 SQLite database read-only.
- Generation now uses short-lived files below `build/` for semantic audit,
  strict LRML/PROV/relation/voice validation, SVG rendering, and conflict
  analysis. Only a complete validated LRML/PROV/relations/conflicts bundle is
  committed, and a failed run leaves the previous row unchanged.
- Workbench reads persisted models from SQLite. Søksbie materializes LRML and
  PROV rows into Postgres/pgvector and rebuilds when the model corpus revision
  changes; legacy filesystem bundles remain available for one-time import.

## [2026-09-14] feature | Voice-first statement profile

- Added a lightweight `voice-first` profile with one keyed JSON record per
  material statement, controlled statement kinds, exact source offsets, direct
  procedural attribution, adoption status, and natural-language searchable
  assertions.
- Kept the existing LegalRuleML generation workflow as the separate
  `formal-rules` profile. RuleML rules, relation manifests, hjemmel decomposition,
  temporal rule parameters, conflict reasoning, and SVG rendering are outside
  the required scope of `voice-first`.

## [2026-09-14] docs | Separate assertion, narration, and endorsement

- Extended the voice-first schema and attribution guidance with
  independent `asserted_by`, `reported_by`, and `endorsed_by` relations;
  repeatable attribution bases with exact evidence spans; common vedtak
  examples; and a projection rule that reserves `Role.forExpression` for
  substantive responsibility while retaining narration and endorsement in the
  voice ledger.
## [2026-09-14] feature | Immutable source manifests and validated quote spans

- Defined per-decision source manifests containing normalized input text, its
  SHA-256 digest, the source filename, and a versioned normalization policy.
- Replaced composite voice-ledger quotes with non-overlapping contiguous spans
  using canonical document-relative character offsets, and added source/PROV
  byte-equality validation.

## [2026-09-14] docs | Bounded section extraction pipeline

- Defined a finite, section-scoped extraction and adjudication pipeline with a
  reversible normalization offset map, strict structured records, exact-quote
  rejection, deterministic validation and merging, and fail-closed output.
- Capped each section at two low-cost calls and one strong-model adjudication;
  prohibited model tool loops and required per-call model, prompt, token,
  failure, escalation, and cost telemetry.
## [2026-09-14] docs | Voice-first gold annotation and evaluation contract

- Added the normative decision-level annotation guide, metric definitions,
  cost/escalation reporting, and release gates that precede formalization.
- Published synthetic gold release `v1.0.0`, covering ordinary and
  recommendation-only decisions, adoption, indirect and nested speech,
  multiple taxpayers, procedural history, and majority/minority opinions.
- Added an offline validator and regression tests for hashes, disjoint splits,
  controlled labels, and exact span round trips.
