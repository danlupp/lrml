# Overview — what LegalRuleML is

LegalRuleML extends **RuleML** with formal features specific to legal norms,
guidelines, policies, and reasoning. It is an OASIS Standard (v1.0, 2021)
expressed with XML Schema and Relax NG, plus an RDFS metamodel. Its purpose is
to turn natural-language legal text into a **rich, machine-readable** form that
preserves the peculiarities of legal reasoning. *(spec §2.2, tutorial §1)*

For our project it is the **target language**: we read a vedtak (natural
language) and emit LegalRuleML that captures the legal argumentation.

## What it models *(spec §2.2)*

- **Defeasibility** of rules and defeasible logic (exceptions, conflicts).
- **Deontic operators**: obligations, permissions, prohibitions, rights.
- **Semantic management of negation.**
- **Temporal management** of rules and temporality in rules.
- **Classification of norms**: constitutive vs prescriptive.
- **Jurisdiction** of norms.
- **Isomorphism** between rules and the natural-language provisions.
- **Identification of parts** of norms (bearer, conditions, …).
- **Authorial tracking** (provenance) of rules.

## Core principles *(spec §2.3, tutorial §1)*

- **Multiple semantic annotations:** one legal rule may carry several
  interpretations, each in its own annotation block (→ [alternatives](alternatives.md)).
- **Tracking creators:** documents/fragments record their authors and publisher
  (→ [metadata](metadata.md)).
- **Linking rules and provisions:** an IRI-based N:M mechanism connects rules to
  textual provisions (→ [sources & isomorphism](sources-isomorphism.md)).
- **Temporal management:** rules and their parameters change over time
  (→ [temporal](temporal.md)).
- **Formal ontology reference:** LegalRuleML is ontology- and logic-neutral; it
  points to external ontologies via IRIs (`@iri`, `@type`).
- **Built on RuleML; mappable to RDF triples** for Linked Data.

## Functional requirements R1–R6 *(spec §4.1)*

- **R1** model different rule types (constitutive, prescriptive).
- **R2** represent normative effects (obligations, permissions, …, reparations).
- **R3** implement defeasibility (exceptions and conflict resolution).
- **R4** implement isomorphism (1:1 rules ↔ textual units).
- **R5** represent alternatives (competing interpretations).
- **R6** manage rule reification (rules are objects with jurisdiction,
  authority, temporal properties).

> For a tax-appeal vedtak, the workhorses are **R1** (the deduction rule and its
> definitions), **R4** (tie every rule to the hjemmel), **R5** (taxpayer vs
> secretariat readings, flertall vs mindretall), and **R3/R6** (which reading
> wins, and under which inntektsår/version).

## Anatomy of a document (orientation)

A LegalRuleML document is the `<lrml:LegalRuleML>` root holding four ordered
groups of top-level blocks *(spec §5.16)*:

1. **Prefix** declarations.
2. **Metadata** — sources/references, times, temporal characteristics, agents,
   figures, roles, authorities, jurisdictions.
3. **Associations** — link metadata to rules without redundancy.
4. **Statement-related** — `Alternatives`, `Context`, `Statements` (the rules).

See [document-structure.md](document-structure.md) for the exact ordering and
serialization rules. The rest of the `concepts/` pages each zoom into one block.

## Node vs edge elements (the striped syntax) *(spec §5.5)*

LegalRuleML XML alternates two kinds of elements:

- **Node elements** — UpperCamelCase (`<lrml:Obligation>`, `<lrml:Authority>`);
  correspond to **classes** in the metamodel.
- **Edge elements** — lowerCamelCase (`<lrml:hasStatement>`, `<lrml:appliesSource>`);
  correspond to **properties/relationships**.

In the **normalized** serialization Node and edge elements strictly alternate
(a "striped" tree, like RDF/XML). In the **compact** serialization the skippable
edge tags are removed for brevity. We emit compact; see
[document-structure.md](document-structure.md#serializations).

## See also

- [statements.md](statements.md) · [ruleml-rules.md](ruleml-rules.md) ·
  [deontic.md](deontic.md) · [defeasibility.md](defeasibility.md)
- Project glue: [../mapping/vedtak-to-legalruleml.md](../mapping/vedtak-to-legalruleml.md)
