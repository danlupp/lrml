# Index

Catalog of every page in the LegalRuleML wiki. Start here.

## Start

- [AGENTS.md](AGENTS.md) — schema, conventions, workflows, and the adopted
  modelling stance for vedtak → LegalRuleML.
- [log.md](log.md) — chronological record of ingests, queries, and lint passes.

## Concepts — the LegalRuleML language

- [concepts/overview.md](concepts/overview.md) — what LegalRuleML is, the
  principles, and the big picture of how a document is shaped.
- [concepts/document-structure.md](concepts/document-structure.md) — the
  `<lrml:LegalRuleML>` root, prescribed element order, serializations
  (normalized / compact / basic), and conformance.
- [concepts/statements.md](concepts/statements.md) — Constitutive, Prescriptive,
  Factual, Penalty, Reparation, and Override statements; the `Statements` block.
- [concepts/ruleml-rules.md](concepts/ruleml-rules.md) — `<ruleml:Rule>`, `if`/`then`,
  `Atom`, `Rel`, `Var`, `Ind`, `Data`, `Expr`/`Fun`, `slot`, `And`/`Or`/`Neg`.
- [concepts/deontic.md](concepts/deontic.md) — Obligation, Permission, Prohibition,
  Right; Bearer/AuxiliaryParty; SuborderList; Violation.
- [concepts/defeasibility.md](concepts/defeasibility.md) — strict/defeasible/defeater
  strength, `<lrml:Override>`, superiority relation, conflict resolution.
- [concepts/sources-isomorphism.md](concepts/sources-isomorphism.md) — LegalSource,
  LegalReference, Source, Reference, Association; tying rules to hjemmel; anchoring
  source quotes with W3C PROV in the `.prov.xml` sidecar.
- [concepts/hjemmel-anchoring.md](concepts/hjemmel-anchoring.md) — making the
  rule↔text link *precise*: pinpoint sources (ledd/bokstav), one hjemmel per
  Association, keyed vilkår atoms, statutory wording in the sidecar, and what
  the validator enforces.
- [concepts/context-associations.md](concepts/context-associations.md) — `<lrml:Association>`
  and `<lrml:Context>`, the `applies*` edges, `inScope`/`toTarget`.
- [concepts/alternatives.md](concepts/alternatives.md) — `<lrml:Alternatives>` for
  competing interpretations; the four interpretation templates.
- [concepts/metadata.md](concepts/metadata.md) — Agent, Figure, Role, Authority,
  Jurisdiction (provenance and applicability).
- [concepts/voices-and-attribution.md](concepts/voices-and-attribution.md) —
  independent assertion, narration, and endorsement relations; direct
  Actor/Role/expression projection; adjudicative selection; and evidence bases.
- [concepts/temporal.md](concepts/temporal.md) — Time, TemporalCharacteristic,
  legal status (in force / efficacy / applicability), versioning over time.
- [concepts/identifiers.md](concepts/identifiers.md) — `@key`/`@keyref`/`@iri`/`@sameAs`,
  CURIEs, `<lrml:Prefix>`, distributed syntax, `mergerOf`.

## Mapping — vedtak → LegalRuleML

- [mapping/pipeline-design.md](mapping/pipeline-design.md) — bounded,
  section-scoped extraction with reversible normalization, exact-quote gates,
  selective adjudication, deterministic merging, and cost telemetry.
- [mapping/voice-first-profile.md](mapping/voice-first-profile.md) — lightweight
  keyed JSON extraction of material statements, exact quotes, three independent
  voice relations with evidence spans, procedural voices,
  and adoption status; separate from the `formal-rules` pipeline.
- [mapping/voice-first-annotation-and-evaluation.md](mapping/voice-first-annotation-and-evaluation.md)
  — normative span/voice annotation guide, versioned decision-level gold-set
  contract, metrics, cost reporting, and release gates.
- [mapping/source-manifest.md](mapping/source-manifest.md) — immutable normalized
  decision text, digests, canonical quote spans, and PROV equality.
- [mapping/vedtak-anatomy.md](mapping/vedtak-anatomy.md) — the structure of a
  Skatteklagenemnda vedtak and what each section contributes.
- [mapping/vedtak-to-legalruleml.md](mapping/vedtak-to-legalruleml.md) — the core
  step-by-step playbook (the most important page for the task).
- [mapping/worked-example.md](mapping/worked-example.md) — a full vedtak
  (`vedtak_frodo_ferge`) mapped to a complete compact LegalRuleML file.
- [mapping/patterns-and-pitfalls.md](mapping/patterns-and-pitfalls.md) — recurring
  modelling patterns and common mistakes to avoid.

## Reference

- [reference/element-cheatsheet.md](reference/element-cheatsheet.md) — quick
  syntax table of the elements you will actually emit.
- [reference/vocabulary.md](reference/vocabulary.md) — glossary of every Node
  element, edge element, and attribute, with one-line definitions.
