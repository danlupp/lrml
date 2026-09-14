# Vocabulary glossary

One-line definitions of the LegalRuleML/RuleML elements and attributes used in
this wiki. Node elements are UpperCamelCase (classes); edge elements are
lowerCamelCase (properties). *(spec §3, §5)* See
[overview.md](../concepts/overview.md#node-vs-edge-elements-the-striped-syntax).

## Document & structure
- **`lrml:LegalRuleML`** — the document root (`LegalRuleMLDocument`). → [doc](../concepts/document-structure.md)
- **`lrml:Prefix`** — declares a CURIE prefix → IRI mapping. → [ids](../concepts/identifiers.md)
- **`lrml:Comment`** — free annotation, allowed anywhere.

## Statements (node) → [statements.md](../concepts/statements.md)
- **`lrml:Statements`** — collection holding all statements.
- **`lrml:ConstitutiveStatement`** — a definitional / "counts-as" rule (no deontic head).
- **`lrml:PrescriptiveStatement`** — a behaviour-regulating rule (deontic head).
- **`lrml:FactualStatement`** — asserts a fact/state of affairs.
- **`lrml:PenaltyStatement`** — holds a sanction (a `SuborderList`).
- **`lrml:ReparationStatement`** — links a breached primary norm to its penalty.
- **`lrml:OverrideStatement`** — states one Legal Rule defeats another.
- **`lrml:hasTemplate`** — (edge) wraps a statement's logical content (skipped in compact, **except** on `FactualStatement` where it stays explicit).

## Deontic (node) → [deontic.md](../concepts/deontic.md)
- **`lrml:Obligation`** / **`lrml:Permission`** / **`lrml:Prohibition`** / **`lrml:Right`** — the deontic operators.
- **`lrml:Bearer`** — (node, slot key) the party bearing the modality; first child of a `<ruleml:slot>`, party term second.
- **`lrml:AuxiliaryParty`** — (node, slot key) the counterparty/beneficiary.
- **`lrml:SuborderList`** — ordered list of deontic specs (position = primary → compensating).
- **`lrml:Violation`** / **`lrml:Compliance`** — (formula) the referenced prescriptive statement was breached / met.
- **`lrml:Reparation`** — connects a penalty to its prescriptive statement (`appliesPenalty` + `toPrescriptiveStatement`).

## Defeasibility & alternatives → [defeasibility.md](../concepts/defeasibility.md) · [alternatives.md](../concepts/alternatives.md)
- **`lrml:Override`** — defeasible Legal Rule superiority; `@over` beats `@under`.
- **`lrml:Alternatives`** — groups mutually exclusive legal renderings.
- **`lrml:hasAlternative`** — (edge) one candidate reading in an Alternatives set.
- **`lrml:hasStrength`** — (edge, inside a Rule) holds **`lrml:StrictStrength`** / **`lrml:DefeasibleStrength`** / **`lrml:Defeater`**.

## Sources & isomorphism → [sources-isomorphism.md](../concepts/sources-isomorphism.md)
- **`lrml:LegalSource(s)`** — a legal text resource (`@key` + `@sameAs` IRI).
- **`lrml:LegalReference(s)`** — a citation record; **no `@key`** — its internal id is `@refersTo` (an NCName).
- **`lrml:Source(s)`** / **`lrml:Reference(s)`** — generic (non-legal) source/citation.

## Associations & context → [context-associations.md](../concepts/context-associations.md)
- **`lrml:Associations`** / **`lrml:Association`** — N:M link metadata ↔ statements.
- **`lrml:Context`** — a named interpretation/version environment.
- **`lrml:toTarget`** — (edge) the statement(s) an association applies to.
- **`lrml:inScope`** — (edge) statements a Context governs (last children of the Context).
- **`lrml:appliesSource` / `appliesAuthority` / `appliesJurisdiction` / `appliesTemporalCharacteristic(s)` / `appliesModality` / `appliesStrength`** — (edges) what metadata is applied; on a Context also **`appliesAssociation(s)`**. This list is exhaustive — no `appliesTemporal`, `appliesTime`, `appliesRole` or `appliesAgent`.

## Metadata → [metadata.md](../concepts/metadata.md)
- **`lrml:Agent(s)`** — a person/org/system playing a role.
- **`lrml:Figure(s)`** — an abstract legal figure (`hasFunction`) filled by an Agent (`hasActor`).
- **`lrml:Role(s)`** — the role an Agent plays; wired with **`lrml:filledBy`** (→ Agent) and direct **`lrml:forExpression`** (→ statement/rule/atom, not Context).
- **`lrml:Authority(ies)`** — the enacting/deciding authority.
- **`lrml:Jurisdiction(s)`** — the jurisdiction of application.

## Temporal → [temporal.md](../concepts/temporal.md)
- **`ruleml:Time`** — an instant; CURIE `@key` (`:t-2022`), `Data` limited to `xs:dateTime|date|duration`.
- **`lrml:Times`** — collection of Time instants.
- **`lrml:TemporalCharacteristic(s)`** — relates a statement to time + a legal status.
- **`lrml:forStatus`** — (edge) the legal status (`vocab#InForce` / `#Efficacious` / `#Applicable`).
- **`lrml:hasStatusDevelopment`** — (edge) `vocab#Starts` / `#Ends` for that status.
- **`lrml:atTime`** — (edge) links a characteristic to a Time (there is no `hasTime` element).

## RuleML logic → [ruleml-rules.md](../concepts/ruleml-rules.md)
- **`ruleml:Rule`** / **`ruleml:Implies`** — a (named) rule / bare implication.
- **`ruleml:if`** / **`ruleml:then`** — body / head edges (never skippable).
- **`ruleml:And` / `Or` / `Neg` / `Naf`** — conjunction / disjunction / strong negation / negation-as-failure.
- **`ruleml:Atom`** — atomic formula (relation + terms).
- **`ruleml:Rel`** — predicate/relation symbol.
- **`ruleml:Var`** — logical variable. **`ruleml:Ind`** — individual constant.
- **`ruleml:Data`** — typed datatype literal (`@xsi:type`).
- **`ruleml:Expr`** / **`ruleml:Fun`** — functional term / function symbol.
- **`ruleml:slot`** — named (key→value) argument.

## Common attributes → [identifiers.md](../concepts/identifiers.md)
- **`@key`** — document-unique id (RuleML keys are CURIEs: `:r-x`). **`@keyref`** — reference to a `@key` (`#k`, colon-stripped).
- **`@iri`** — meaning IRI. **`@sameAs`** — external identity IRI. **`@type`** — metamodel/ontology type.
- **`@refersTo`** — a reference's internal NCName id. **`@refID`** / **`@refIDSystemName`** — citation id + its naming system (also `@pre`/`@refID` on `Prefix`).
- **`@closure`** — quantifier closure on a rule. **`@over`** / **`@under`** — stronger/weaker Legal Rule in an Override.
- **`@hasCreationDate`** — root creation Time reference. **`@xsi:type`** — XSD datatype of a `Data`.
- **`@index`** — order index on collection edges.

## See also
- [element-cheatsheet.md](element-cheatsheet.md) · [../index.md](../index.md)
