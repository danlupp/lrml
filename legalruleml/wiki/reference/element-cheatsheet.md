# Element cheatsheet

Quick syntax reference for the elements you actually emit when mapping a vedtak.
Compact serialization, verified against the vendored OASIS XSD
(`legalruleml/xsd-schema/compact/lrml-compact.xsd`). For meanings see the linked
concept pages.

## Skeleton

```xml
<lrml:LegalRuleML xmlns="https://example.org/ratatouille/onto#"
                  xmlns:lrml="http://docs.oasis-open.org/legalruleml/ns/v1.0/"
                  xmlns:ruleml="http://ruleml.org/spec"
                  xmlns:xsi="…/XMLSchema-instance" xmlns:xs="…/XMLSchema"
                  hasCreationDate="#t-vedtak">
  <lrml:Prefix pre="…" refID="…"/>
  <lrml:LegalReferences>…</lrml:LegalReferences>
  <lrml:LegalSources>…</lrml:LegalSources>
  <lrml:Authorities>…</lrml:Authorities>
  <lrml:Jurisdictions>…</lrml:Jurisdictions>
  <lrml:Agents>…</lrml:Agents>  <lrml:Roles>…</lrml:Roles>
  <lrml:Times>…</lrml:Times>
  <lrml:TemporalCharacteristics>…</lrml:TemporalCharacteristics>
  <lrml:Associations>…</lrml:Associations>
  <lrml:Context>…</lrml:Context>
  <lrml:Alternatives>…</lrml:Alternatives>
  <lrml:Statements>…</lrml:Statements>
</lrml:LegalRuleML>
```
Top-level order is fixed → [document-structure.md](../concepts/document-structure.md#prescribed-order-of-top-level-elements).
The **default `xmlns`** is the domain-ontology namespace — it is what bare-colon
CURIEs (`:overstigerTerskelbeloep`, `:r-fradrag`) resolve against. No PROV
markup in this file: quotes live in the `.prov.xml` sidecar (below).

## Prefixes → [identifiers.md](../concepts/identifiers.md)
```xml
<lrml:Prefix pre="fsfin" refID="https://lovdata.no/forskrift/1999-11-19-1158/"/>
```
Attributes are `@pre` (non-empty, no colon) and `@refID` (the IRI). An **empty**
prefix cannot be declared with `<lrml:Prefix>` — bind it via the default `xmlns`.

## Reference layer → [sources-isomorphism.md](../concepts/sources-isomorphism.md)
```xml
<lrml:LegalReference refersTo="ref-fsfin-6-44-4"
    refID="FSFIN § 6-44-4" refIDSystemName="rettsinformasjon-aliaser"/>
<lrml:LegalSource key="src-fsfin-6-44-4"
  sameAs="forskrift-1999-11-19-1158/section:6-44-4"/>
```
`LegalReference` takes **no `@key`**; `@refersTo` *is* its internal id (an
NCName — no colons/`#`), and `keyref="#ref-fsfin-6-44-4"` elsewhere resolves to
it. `@refID` holds the human citation. Resolve the registered legacy URN with
`vedtak-legalruleml resolve-source`; its exact Rettsregister `selected_id` goes
in `LegalSource@sameAs`. If Rettsrev is unavailable or unresolved, the unchanged
registered URN is the warning-backed fallback.

## Provenance → [metadata.md](../concepts/metadata.md)
```xml
<lrml:Authority key="auth-skl" sameAs="…"/>
<lrml:Jurisdiction key="jur-no-skatt" sameAs="…"/>
<lrml:Agent key="agent-modell"/>
<lrml:Role key="role-author" iri="https://example.org/roles#author">
  <lrml:filledBy keyref="#agent-modell"/>
  <lrml:forExpression keyref="#r-fradrag"/>
</lrml:Role>
```
Agents attach to expressions through the Role's `filledBy`/`forExpression`
edges; `forExpression` directly targets a statement/rule/atom, not Context.
Procedural voice Roles are separate from model authorship. There is **no**
`appliesAgent`/`appliesRole` association edge. See
[voices-and-attribution.md](../concepts/voices-and-attribution.md).

## Time → [temporal.md](../concepts/temporal.md)
```xml
<ruleml:Time key=":t-2022"><ruleml:Data xsi:type="xs:date">2022-01-01</ruleml:Data></ruleml:Time>
<lrml:TemporalCharacteristic key="tc-2022">
  <lrml:forStatus iri="http://docs.oasis-open.org/legalruleml/ns/v1.0/vocab#Applicable"/>
  <lrml:atTime keyref="#t-2022"/>
</lrml:TemporalCharacteristic>
```
RuleML `@key`s must be CURIEs (`:t-2022`) or absolute IRIs; `Data` inside `Time`
only accepts `xs:dateTime | xs:date | xs:duration` (an inntektsår = its
January 1). The edge is `atTime`, and status IRIs come from the
`…/ns/v1.0/vocab#` vocabulary (`Applicable`, `Efficacious`, `InForce`; status
development `Starts`/`Ends`).

## Association / Context → [context-associations.md](../concepts/context-associations.md)
```xml
<lrml:Association key="assoc-fsfin-6-44-4">
  <lrml:appliesSource keyref="#ref-fsfin-6-44-4"/>
  <lrml:appliesSource keyref="#src-fsfin-6-44-4"/>
  <lrml:appliesAuthority keyref="#auth-skl"/>
  <lrml:appliesJurisdiction keyref="#jur-no-skatt"/>
  <lrml:appliesTemporalCharacteristic keyref="#tc-2022"/>
  <lrml:toTarget keyref="#ps-fradrag"/>
</lrml:Association>
<lrml:Context key="ctx-2022">
  <lrml:appliesTemporalCharacteristic keyref="#tc-2022"/>
  <lrml:inScope keyref="#ps-fradrag"/>
</lrml:Context>
```
The full set of `applies*` edges: `appliesSource`,
`appliesTemporalCharacteristic(s)`, `appliesStrength`, `appliesModality`,
`appliesAuthority`, `appliesJurisdiction` (Context additionally:
`appliesAssociation(s)`). Nothing else exists.

## Hjemmel anchoring → [hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)
One hjemmel per Association; a vilkår with its own hjemmel gets its own key:
```xml
<lrml:LegalReference refersTo="ref-fsfin-6-44-1-l2"
    refID="FSFIN § 6-44-1 andre ledd" refIDSystemName="rettsinformasjon-aliaser"/>
<lrml:LegalSource key="src-fsfin-6-44-1-l2"
  sameAs="forskrift-1999-11-19-1158/section:6-44-1"/>
…
<lrml:Association key="assoc-fsfin-6-44-1-l2">
  <lrml:appliesSource keyref="#ref-fsfin-6-44-1-l2"/>
  <lrml:appliesSource keyref="#src-fsfin-6-44-1-l2"/>
  <lrml:toTarget keyref="#a-bom-noedvendig"/>     <!-- one vilkår -->
</lrml:Association>
…
<ruleml:Atom key=":a-bom-noedvendig">
  <ruleml:Rel iri=":oppfyllerReisetidsregelen"/><ruleml:Var>skattepliktig</ruleml:Var>
</ruleml:Atom>
```
Pinpoint only as deep as the text cites (`ledd:2` → key stem `-l2`,
`bokstav:b` → `-bb`). Check with
`python3 legalruleml/bin/validate_lrml.py --strict --hjemmel <f>.lrml`.

## Source quotes (PROV sidecar) → [sources-isomorphism.md](../concepts/sources-isomorphism.md#vedtak-quotes)
In `<name>.prov.xml` next to the `.lrml` — never inside it:
```xml
<prov:Bundle xml:id="prov-text-anchors" xmlns:prov="http://www.w3.org/ns/prov#">
  <prov:Entity xml:id="quote-fs-terskel">
    <prov:value>Dokumenterte fergekostnader … Vilkåret … er oppfylt.</prov:value>
    <prov:wasQuotedFrom prov:resource="#src-vedtak-sk-2022-0117"/>
  </prov:Entity>
  <prov:wasDerivedFrom prov:generatedEntity="<name>.lrml#fs-terskel"
                       prov:usedEntity="#quote-fs-terskel"/>
</prov:Bundle>
```
`wasQuotedFrom` resolves to a `LegalSource` **key** in the `.lrml`;
`wasDerivedFrom/@prov:generatedEntity` names the anchored fragment's `@key`
(colon-stripped). Statutory text → quoted from the provision source; a finding →
quoted from the vedtak source.

## Statements → [statements.md](../concepts/statements.md)
```xml
<lrml:PrescriptiveStatement key="ps-x"> <ruleml:Rule …>…</ruleml:Rule> </lrml:PrescriptiveStatement>
<lrml:ConstitutiveStatement key="cs-x"> <ruleml:Rule …>…</ruleml:Rule> </lrml:ConstitutiveStatement>
<lrml:FactualStatement key="fs-x">
  <lrml:hasTemplate> <ruleml:Atom>…</ruleml:Atom> </lrml:hasTemplate>
</lrml:FactualStatement>
<lrml:OverrideStatement key="ov-x"> <lrml:Override over="#cs-stronger" under="#cs-weaker"/> </lrml:OverrideStatement>
<lrml:PenaltyStatement key="pen-x"> <lrml:SuborderList>…</lrml:SuborderList> </lrml:PenaltyStatement>
<lrml:ReparationStatement key="reps-x">
  <lrml:Reparation key="rep-x">
    <lrml:appliesPenalty keyref="#pen-x"/>
    <lrml:toPrescriptiveStatement keyref="#ps-x"/>
  </lrml:Reparation>
</lrml:ReparationStatement>
```
`hasTemplate` is skippable in compact for every statement type **except
`FactualStatement`**, which keeps the explicit wrapper. A FactualStatement's
formula is non-deontic (Atom / Neg / And…); an unconditional deontic conclusion
is a PrescriptiveStatement with an empty body:
```xml
<lrml:PrescriptiveStatement key="ps-konkl">
  <ruleml:Rule key=":r-konkl">
    <ruleml:if><ruleml:And/></ruleml:if>
    <ruleml:then> <lrml:Right>…</lrml:Right> </ruleml:then>
  </ruleml:Rule>
</lrml:PrescriptiveStatement>
```

## Rule body/head → [ruleml-rules.md](../concepts/ruleml-rules.md)
```xml
<ruleml:Rule key=":r-x" closure="universal">
  <ruleml:if><ruleml:And>
    <ruleml:Atom><ruleml:Rel iri=":pred"/><ruleml:Var>x</ruleml:Var></ruleml:Atom>
  </ruleml:And></ruleml:if>
  <ruleml:then>…head…</ruleml:then>
</ruleml:Rule>
```
Terms: `<ruleml:Var>x</ruleml:Var>` · `<ruleml:Ind iri=":frodo"/>` ·
`<ruleml:Data xsi:type="xs:decimal">3300</ruleml:Data>` ·
`<ruleml:Rel iri=":pred"/>` · connectives `And`/`Or`/`Neg`/`Naf`.
`if`/`then` are **never** skippable. RuleML `@key`s are CURIEs (`:r-x`);
`keyref="#r-x"` matches with the empty-prefix colon stripped.

## Deontic head → [deontic.md](../concepts/deontic.md)
```xml
<lrml:Right>
  <ruleml:slot><lrml:Bearer iri=":skattepliktig-rolle"/><ruleml:Var>x</ruleml:Var></ruleml:slot>
  <ruleml:Atom>…</ruleml:Atom>
</lrml:Right>
```
`Bearer`/`AuxiliaryParty` are **slot keys**: empty elements (optionally with
`@iri`) whose party term is the slot's second child — never wrappers around the
term. Same shape for `Obligation`, `Permission`, `Prohibition`.

## Alternatives → [alternatives.md](../concepts/alternatives.md)
```xml
<lrml:Alternatives key="alt-x">
  <lrml:hasAlternative keyref="#cs-a"/><lrml:hasAlternative keyref="#cs-b"/>
</lrml:Alternatives>
```
(The edge is `hasAlternative`; there is no `<lrml:Alternative>` element.)
Members are alternative legal renderings, not competing factual allegations.
Use Context `appliesAlternatives` + `inScope` for adjudicative selection;
`Override` only for genuine defeasible Legal Rule priority.

## Common attributes → [identifiers.md](../concepts/identifiers.md)
`@key` (unique, colon-stripped for RuleML) · `@keyref="#k"` · `@iri` · `@sameAs` ·
`@refersTo` (LegalReference internal id) · `@refID` / `@refIDSystemName` ·
`@closure` · `@xsi:type` · `@over`/`@under` · `@hasCreationDate="#t"` ·
`@pre` (Prefix name).

## Validate

```bash
python3 legalruleml/bin/validate_lrml.py samples/out/<name>.lrml
```
Runs the vendored-XSD check plus keyref/acyclicity/if-then/sidecar checks.

## See also
- [vocabulary.md](vocabulary.md) — full glossary.
- [../mapping/worked-example.md](../mapping/worked-example.md) — a complete file.
