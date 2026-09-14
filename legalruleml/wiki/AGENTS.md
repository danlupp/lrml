# LegalRuleML Wiki — Schema & Conventions

This wiki is a persistent, interlinked knowledge base about **LegalRuleML Core
Specification v1.0 (OASIS Standard, 30 Aug 2021)**, curated for one concrete job:

> **Goal:** Help an LLM agent parse a *vedtak* from the Norwegian
> *Skatteklagenemnda* (Tax Appeals Board) and produce a **LegalRuleML** file
> that represents the **legal argumentation** used in that vedtak.

You (the agent) read this wiki; you also maintain it. Humans curate sources and
ask questions; you do the summarizing, cross-referencing, and bookkeeping.

## Sources (immutable — read, never edit)

- `../in/tutorial.pdf` — *LegalRuleML: Design Principles and Foundations*
  (Athan, Governatori, Palmirani, Paschke, Wyner). The tutorial/primer.
- OASIS spec (HTML, authoritative):
  https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/legalruleml-core-spec-v1.0-os.html
- OASIS landing page:
  https://www.oasis-open.org/standard/legalruleml-core-specification-version-1-0-oasis-standard/
- Official example fragments (`.lrml`):
  https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/examples/
- Schemas: Relax NG `…/os/relaxng/`, XSD `…/os/xsd-schema/`, RDFS metamodel `…/os/rdfs/`.
  The compact XSD is **vendored** at `../xsd-schema/` (see its README for the
  two local import patches) so validation runs offline via
  `../bin/validate_lrml.py`.

Canonical vedtak and BFU source material lives in Rettsrev SQLite and is supplied
to Workbench generation through the dedicated Rettsrev LRML API. Shared legal
registers and legacy decision fixtures remain under `../../samples/in/`.
Complete generated models are persisted in `../../build/legalruleml.sqlite`;
filesystem bundles are temporary validation inputs or legacy fixtures.

## Directory layout

```
wiki/
  AGENTS.md            ← this file (schema, conventions, workflow)
  index.md             ← catalog of every page (read this first)
  log.md               ← append-only chronological log
  concepts/            ← LegalRuleML language reference, one topic per page
  mapping/             ← vedtak → LegalRuleML playbook + worked examples
  reference/           ← cheatsheets, full vocabulary glossary
```

## Page conventions

- Markdown, with `[[wikilinks]]`-style relative links written as normal
  Markdown links so they work in plain editors and Obsidian alike.
- XML element names use backticks and namespace prefixes:
  `<lrml:PrescriptiveStatement>`, `<ruleml:Atom>`, `@keyref`.
- Namespace prefixes used throughout:
  - `lrml` → `http://docs.oasis-open.org/legalruleml/ns/v1.0/`
  - `lrmlmm` → `http://docs.oasis-open.org/legalruleml/ns/mm/v1.0/` (metamodel)
  - `ruleml` → `http://ruleml.org/spec`
  - `prov` → `http://www.w3.org/ns/prov#` (W3C PROV, used for source-quote anchors)
  - `xs` / `xsi` → XML Schema (+ instance)
- When a claim comes from the spec, cite the section number (e.g. *spec §4.2.3*);
  when from the tutorial, say *tutorial*. Keep examples in **compact
  serialization** unless a point specifically needs the normalized form.
- Norwegian legal terms are kept in Norwegian (vedtak, vilkår, hjemmel,
  rettsgrunnlag, anførsel, sekretariatet) with a gloss on first use per page.

## Workflows

### Ingest a new source (spec section, paper, example file)
1. Read it; note which existing pages it touches.
2. Update the relevant `concepts/` or `mapping/` page(s).
3. Update `index.md` if a page is added or its summary changes.
4. Append an entry to `log.md`.

### Answer "how do I model X from a vedtak?"
1. Start at [index.md](index.md), then [mapping/vedtak-to-legalruleml.md](mapping/vedtak-to-legalruleml.md).
2. Drill into the relevant `concepts/` page for the precise element/attribute.
3. If the answer is reusable, file it back as a new section/page and log it.

### Produce a LegalRuleML file for a vedtak
Follow the step-by-step pipeline in
[mapping/vedtak-to-legalruleml.md](mapping/vedtak-to-legalruleml.md), using
[mapping/worked-example.md](mapping/worked-example.md) as a template and
[reference/element-cheatsheet.md](reference/element-cheatsheet.md) for syntax.
Validate with `python3 legalruleml/bin/validate_lrml.py <file>.lrml` (vendored
OASIS XSD at `legalruleml/xsd-schema/` + keyref/sidecar checks); fix every
error before finishing.

### Lint
Periodically check for: contradictions between pages, stale claims, orphan
pages, concepts mentioned but lacking a page, and missing cross-references.
Record findings in `log.md`.

## Modelling stance (decisions adopted for this project)

These conventions keep generated files consistent. They are defaults, not law —
revisit when a vedtak needs something else, and log any change.

1. **Serialization:** emit **compact** serialization, valid against the
   vendored `legalruleml/xsd-schema/compact/lrml-compact.xsd`
   (see [concepts/document-structure.md](concepts/document-structure.md)).
2. **Isomorphism first:** every modelled rule is tied back to its hjemmel via
   `<lrml:LegalReference>`/`<lrml:LegalSource>` + `<lrml:Association>`
   (see [concepts/sources-isomorphism.md](concepts/sources-isomorphism.md)).
   Use the `aliaser` from `rettsinformasjon.json` as `@refID`; the reference's
   internal id goes in `@refersTo` (no `@key` on references).
3. **Vilkår = rule body:** each statutory condition (vilkår) becomes a
   `<ruleml:Atom>` inside an `<ruleml:And>` in `<ruleml:if>`; the legal
   consequence is the `<ruleml:then>` head.
4. **Entitlement modelling:** "skattepliktige innrømmes fradrag" is modelled as
   the head of a **PrescriptiveStatement** using a directed
   `<lrml:Permission>`/`<lrml:Right>` (Bearer = skattepliktige), unless the
   reasoning is purely definitional, in which case use a
   **ConstitutiveStatement** (see [concepts/statements.md](concepts/statements.md)).
5. **Facts:** "Vilkåret om X er oppfylt" becomes a `<lrml:FactualStatement>`.
6. **Voices, disputes & dissent:** attribute every material contribution directly
  through Actor/Role/Expression. Competing factual allegations remain facts;
  mutually exclusive legal renderings may become `<lrml:Alternatives>` with an
  adjudication Context selecting the adopted reading. `<lrml:Override>` is only
  for actual defeasible Legal Rule priority (see
  [concepts/voices-and-attribution.md](concepts/voices-and-attribution.md)).
7. **Time:** the inntektsår and the applicable rule version (e.g. terskelbeløp
   3 300 vs 5 000) are modelled with `<lrml:TemporalCharacteristic>` and version
   selection via `<lrml:Context>` (see [concepts/temporal.md](concepts/temporal.md)).
8. **Provenance:** Skatteklagenemnda/sekretariatet → `<lrml:Authority>`;
  Norway/skatt → `<lrml:Jurisdiction>`; procedural Actors and model author use
  separate `<lrml:Role>` nodes.
9. **Text isomorphism (quotes):** anchor the exact passage that each fragment
   formalizes as a `<prov:Entity>` in the **sidecar file** `<name>.prov.xml`
   (W3C PROV; root `<prov:Bundle>`): verbatim text in `<prov:value>`, a
   `<prov:wasQuotedFrom>` edge to the `<lrml:LegalSource>` key, and a
   `<prov:wasDerivedFrom>` record linking the fragment's `@key` to its quote.
   The `.lrml` contains no PROV markup (the OASIS XSD rejects it). Declare the
   vedtak as a `<lrml:LegalSource>` linked to the statements via an
   `<lrml:Association>`
   (see [concepts/sources-isomorphism.md](concepts/sources-isomorphism.md#vedtak-quotes)).
10. **Validation gate:** a generated `.lrml` is done only when
  `python3 legalruleml/bin/validate_lrml.py --strict --relations <file>`
  reports no errors. Before emission, reconcile one document-local relation
  vocabulary and entity identity map across all voices. Store the canonical
  signatures, usages, voices, and quote-backed source forms in the sibling
  `<name>.relations.json`; the reasoner consumes the canonical LRML symbols and
  never guesses aliases at runtime. Conflict analysis must also succeed before
  LRML, PROV, relations, and conflicts are atomically stored as one model row.
