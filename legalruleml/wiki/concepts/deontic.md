# Deontic operators

Deontic operators express normative effects and form the **head** of a
prescriptive rule. *(spec §5.13, §6)*

## The operators *(spec §5.13)*

| Element | Meaning | Typical vedtak phrasing |
|---|---|---|
| `<lrml:Obligation>` | It is obligatory that … (OBL) | "plikter å", "skal" |
| `<lrml:Permission>` | It is permitted that … (PER) | "kan", "har adgang til" |
| `<lrml:Prohibition>` | It is forbidden that … (FOR) | "kan ikke", "skal ikke" |
| `<lrml:Right>` | The bearer has a right to … | "innrømmes fradrag", "har krav på" |

These are **node** elements wrapping the affected formula. They may be
**directed** (carry a Bearer) or undirected. The content model is:
optional `<ruleml:slot>`s (the parties), then the formula:

```xml
<lrml:Obligation>
  <ruleml:slot>
    <lrml:Bearer iri=":pliktsubjekt-rolle"/>
    <ruleml:Var>x</ruleml:Var>
  </ruleml:slot>
  <ruleml:Atom> … the obliged state of affairs … </ruleml:Atom>
</lrml:Obligation>
```

## Parties *(spec §5.13)*

Party roles are **slot keys**: `<lrml:Bearer>`/`<lrml:AuxiliaryParty>` are
empty elements (optionally with `@iri`) placed as the *first* child of a
`<ruleml:slot>`, whose *second* child is the party term (`Var`/`Ind`). Writing
`<lrml:Bearer><ruleml:Var>x</ruleml:Var></lrml:Bearer>` (Bearer as a wrapper)
is invalid against the schema.

- `<lrml:Bearer>` — the party that bears the obligation/permission/right.
- `<lrml:AuxiliaryParty>` — the counterparty / beneficiary (e.g. the obligee);
  goes in its own additional `<ruleml:slot>`.

> **Vedtak mapping:** the entitlement conclusion "skattepliktige innrømmes
> fradrag" → `<lrml:Right>` (or `<lrml:Permission>`) with a Bearer slot for the
> skattepliktige. Use `<lrml:Obligation>` for duties (e.g. dokumentasjonsplikt,
> opplysningsplikt) and `<lrml:Prohibition>` for "kan ikke kreve fradrag".
> Deontic operators appear in a `PrescriptiveStatement`'s rule head (or body) —
> never inside a `FactualStatement`. An *unconditional* deontic conclusion is a
> rule with an empty body: `<ruleml:if><ruleml:And/></ruleml:if>`.

## Strength of the deontic effect

A deontic operator participates in defeasible reasoning; its rule may be strict,
defeasible, or a defeater (see [defeasibility.md](defeasibility.md)). Conflicts
between a Permission and a Prohibition on the same act are resolved by
[Override](defeasibility.md).

## Suborder list (graded / reparative chains) *(spec §6.2)*

`<lrml:SuborderList>` holds an **ordered** list of deontic specifications used
for compensatory/reparative obligations: if the primary one is violated, the
next item applies, and so on (contrary-to-duty structures). The members are the
deontic operators themselves — there are no wrapper elements for "primary" vs
"compensative" duty; position in the list carries that meaning:

```xml
<lrml:SuborderList>
  <lrml:Prohibition key="prohib-primary"> …slot + Atom… </lrml:Prohibition>
  <lrml:Obligation key="oblig-compensating"> …slot + Atom… </lrml:Obligation>
</lrml:SuborderList>
```

## Violation and reparation *(spec §6.2)* {#violation-and-reparation}

- `<lrml:Violation keyref="#ps-x"/>` is a deontic **formula** used inside a rule
  head/body (e.g. as a premise in `<ruleml:And>` in an `if`): it holds when the
  referenced prescriptive statement has been breached. It is **never** a
  standalone `<lrml:FactualStatement>` — the schema rejects a `Violation` in a
  fact's template. To *assert* that a breach occurred, use an ordinary
  `<lrml:FactualStatement>` with a domain relation (see the tilleggsskatt note
  below). (`<lrml:Compliance keyref>` is its positive counterpart.)
- A [`<lrml:PenaltyStatement>`](statements.md) holds the sanction; a
  `<lrml:ReparationStatement>` connects the breached primary norm to that
  penalty via `<lrml:Reparation>`:

```xml
<lrml:ReparationStatement key="reps-1">
  <lrml:Reparation key="rep-1">
    <lrml:appliesPenalty keyref="#pen-1"/>
    <lrml:toPrescriptiveStatement keyref="#ps-1"/>
  </lrml:Reparation>
</lrml:ReparationStatement>
```

> **Vedtak mapping (tilleggsskatt):** model the substantive duty
> (e.g. correct opplysningsplikt) as an `<lrml:Obligation>`; assert the **breach
> as an ordinary `<lrml:FactualStatement>`** with a domain-relation Atom
> (e.g. `:harGittUriktigeOpplysninger`) — *not* as a `<lrml:Violation>`, which is
> a rule-body formula, not a fact; the tilleggsskatt as a
> `<lrml:PenaltyStatement>` referenced by a `<lrml:ReparationStatement>`. Grade
> ordinary vs skjerpet tilleggsskatt via a `<lrml:SuborderList>`. Use
> `<lrml:Violation keyref="#ps-plikt"/>` only where a rule *fires on* the breach
> (as a premise in its body). See the `vedtak_endring…tilleggsskatt` sample,
> which asserts each breach as a domain-relation fact and uses no `Violation`.

## See also

- [statements.md](statements.md) · [defeasibility.md](defeasibility.md) ·
  [ruleml-rules.md](ruleml-rules.md)
