# RuleML rules — the logical core

LegalRuleML reuses RuleML for the actual logic inside a statement. This page
covers the RuleML elements you will emit. *(spec §5.19, RuleML spec)*

## Rule / Implies

```xml
<ruleml:Rule key=":r1" closure="universal">
  <ruleml:if>  …body…  </ruleml:if>
  <ruleml:then> …head… </ruleml:then>
</ruleml:Rule>
```

- `<ruleml:Rule>` is the reusable, named rule wrapper used inside statements.
  `<ruleml:Implies>` is the bare implication; in LegalRuleML practice the
  statement (`ConstitutiveStatement`/`PrescriptiveStatement`) supplies identity,
  so a `Rule` (or `Implies`) sits directly inside.
- `@closure="universal"` universally quantifies the free variables.
- The `<ruleml:if>` / `<ruleml:then>` edges are **not skippable** even in compact
  serialization *(spec §5.19.6)*. `if` = body (antecedent), `then` = head
  (consequent).
- RuleML `@key` values **must** be CURIEs or absolute IRIs — in practice an
  empty-prefix CURIE (`:r1`); a bare `key="r1"` is schema-invalid. The colon is
  stripped for the uniqueness check and `#keyref` matching *(spec §7)*.

## Atoms, relations, terms

```xml
<ruleml:Atom>
  <ruleml:Rel iri=":oppfyllerReisetidskrav"/>
  <ruleml:Var>skattepliktig</ruleml:Var>
</ruleml:Atom>
```

- `<ruleml:Atom>` — an atomic formula: a relation applied to terms.
- `<ruleml:Rel>` — the predicate/relation symbol (use `@iri` to point at an
  ontology term).
- `<ruleml:Var>` — a logical variable (text = name). Quantified by the rule's
  `@closure`.
- `<ruleml:Ind>` — an individual constant (e.g. a person, a place). Use `@iri`
  for IRI-identified individuals.
- `<ruleml:Data>` — a datatype literal; `@xsi:type` gives the XSD type, e.g.
  `<ruleml:Data xsi:type="xs:decimal">3300</ruleml:Data>`.
- `<ruleml:Expr>` + `<ruleml:Fun>` — a functional term (function applied to
  args), e.g. a computed amount.
- `<ruleml:slot>` — a `key → value` role/argument pair for named (rather than
  positional) arguments: `<ruleml:slot><ruleml:Ind>beløp</ruleml:Ind><ruleml:Data …/></ruleml:slot>`.

## Connectives

- `<ruleml:And>` — conjunction (used for the **vilkår list** in a body).
- `<ruleml:Or>` — disjunction.
- `<ruleml:Neg>` — **strong/classical** negation (the negation of the literal).
- `<ruleml:Naf>` — negation as failure (weak negation) — used for the absence of
  proof; relevant for defeasible defaults.

```xml
<ruleml:if>
  <ruleml:And>
    <ruleml:Atom> … vilkår 1 … </ruleml:Atom>
    <ruleml:Atom> … vilkår 2 … </ruleml:Atom>
    <ruleml:Atom> … vilkår 3 … </ruleml:Atom>
    <ruleml:Atom> … vilkår 4 … </ruleml:Atom>
  </ruleml:And>
</ruleml:if>
```

## How a vedtak rule is shaped

The statutory **vilkår** become the conjunctive body; the **legal consequence**
becomes the head. For a prescriptive (entitlement) rule, the head is a
[deontic](deontic.md) operator wrapping an Atom:

```xml
<lrml:PrescriptiveStatement key="ps-fradrag">
  <ruleml:Rule key=":r-fradrag" closure="universal">
    <ruleml:if>
      <ruleml:And>
        <ruleml:Atom><ruleml:Rel iri=":overTerskelbeløp"/><ruleml:Var>x</ruleml:Var></ruleml:Atom>
        <ruleml:Atom><ruleml:Rel iri=":oppfyllerReisetidskrav"/><ruleml:Var>x</ruleml:Var></ruleml:Atom>
        <ruleml:Atom><ruleml:Rel iri=":harDokumentasjon"/><ruleml:Var>x</ruleml:Var></ruleml:Atom>
        <ruleml:Atom><ruleml:Rel iri=":rimeligsteBillett"/><ruleml:Var>x</ruleml:Var></ruleml:Atom>
      </ruleml:And>
    </ruleml:if>
    <ruleml:then>
      <lrml:Right>
        <ruleml:slot><lrml:Bearer iri=":skattepliktig-rolle"/><ruleml:Var>x</ruleml:Var></ruleml:slot>
        <ruleml:Atom><ruleml:Rel iri=":harReisefradrag"/><ruleml:Var>x</ruleml:Var></ruleml:Atom>
      </lrml:Right>
    </ruleml:then>
  </ruleml:Rule>
</lrml:PrescriptiveStatement>
```

## See also

- [statements.md](statements.md) — which statement type wraps the rule.
- [deontic.md](deontic.md) — the deontic head operators.
- [../mapping/vedtak-to-legalruleml.md](../mapping/vedtak-to-legalruleml.md) — the playbook.
