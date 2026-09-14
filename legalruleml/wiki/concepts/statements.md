# Statements

All rules live inside a `<lrml:Statements>` block (a collection; metamodel
`StatementsBlock`). Each statement is a typed reification of a norm or fact.
*(spec §5.10, §5.11)*

```xml
<lrml:Statements key="stmts1">
  <lrml:ConstitutiveStatement key="cs1"> … </lrml:ConstitutiveStatement>
  <lrml:PrescriptiveStatement key="ps1"> … </lrml:PrescriptiveStatement>
  <lrml:FactualStatement key="fs1"> … </lrml:FactualStatement>
</lrml:Statements>
```

A `<lrml:Statements>` block may carry `@keyref` to reuse content and may be the
target of associations (so metadata attaches to many statements at once).

## The statement types *(spec §5.11)*

| Element | Purpose | Holds |
|---|---|---|
| `<lrml:ConstitutiveStatement>` | Defines a term / institutional fact; "counts-as" rules and definitions. | a `<ruleml:Rule>` — **no** deontic head |
| `<lrml:PrescriptiveStatement>` | A norm regulating behaviour: obligation/permission/prohibition/right. | a `<ruleml:Rule>` whose `then` contains a [deontic](deontic.md) operator |
| `<lrml:FactualStatement>` | Asserts a fact / state of affairs. | `<lrml:hasTemplate>` wrapping a **non-deontic** formula (`Atom`, `Neg`, `And`, …) |
| `<lrml:PenaltyStatement>` | Holds the penalty/sanction invoked on violation. | a deontic spec or a `<lrml:SuborderList>` of them |
| `<lrml:ReparationStatement>` | Links a prescriptive (primary) norm to its penalty (compensatory). | a `<lrml:Reparation>` with `appliesPenalty` + `toPrescriptiveStatement` keyrefs |
| `<lrml:OverrideStatement>` | States that one statement defeats another. | a `<lrml:Override>` template |

Each statement wraps its logical content through a `hasTemplate` edge. In
compact serialization that edge is skipped for every statement type **except
`FactualStatement`**, which keeps the explicit wrapper:

```xml
<lrml:ConstitutiveStatement key="cs-ferge">
  <ruleml:Rule key=":rule-ferge" closure="universal">
    <ruleml:if> … </ruleml:if>
    <ruleml:then> … </ruleml:then>
  </ruleml:Rule>
</lrml:ConstitutiveStatement>

<lrml:FactualStatement key="fs-terskel">
  <lrml:hasTemplate>
    <ruleml:Atom> … </ruleml:Atom>
  </lrml:hasTemplate>
</lrml:FactualStatement>
```

A FactualStatement's formula is constitutive-shaped (no deontic operators). To
state an *unconditional* deontic result — "Frodo innrømmes fradrag med kr 6 240"
— use a `PrescriptiveStatement` whose rule has an empty body:

```xml
<lrml:PrescriptiveStatement key="ps-konkl">
  <ruleml:Rule key=":r-konkl">
    <ruleml:if><ruleml:And/></ruleml:if>
    <ruleml:then><lrml:Right> … </lrml:Right></ruleml:then>
  </ruleml:Rule>
</lrml:PrescriptiveStatement>
```

## Constitutive vs Prescriptive — the key distinction *(spec §2.2, tutorial)*

- **Constitutive** rules *define* or *constitute* concepts ("X counts as Y",
  "a ferge is a vessel that …"). They carry no obligation; their head is a plain
  `<ruleml:Atom>`.
- **Prescriptive** rules *regulate* conduct and carry a deontic effect (you
  must / may / must not / have a right). Their head wraps a deontic operator.

> **Vedtak mapping:**
> - A **definition** the board relies on ("hva regnes som *ferge*?",
>   "hva er *rimeligste* reisemåte?") → **ConstitutiveStatement**.
> - The **entitlement conclusion** ("skattepliktige innrømmes fradrag") →
>   **PrescriptiveStatement** with a `<lrml:Right>`/`<lrml:Permission>` head
>   (Bearer = skattepliktige). See [deontic.md](deontic.md).
> - "Vilkåret om … er oppfylt" → **FactualStatement**.
> - "Mindretallet/flertallet legger til grunn …" competing readings →
>   wrap statements in [Alternatives](alternatives.md) and order them with an
>   **OverrideStatement** (see [defeasibility.md](defeasibility.md)).

## OverrideStatement & the Override template *(spec §5.11, §6)*

```xml
<lrml:OverrideStatement key="ov1">
  <lrml:Override over="#ps-flertall" under="#ps-mindretall"/>
</lrml:OverrideStatement>
```

`@over` wins, `@under` is defeated. Override encodes the superiority relation of
defeasible logic — see [defeasibility.md](defeasibility.md) for *lex specialis /
superior / posterior* and how this resolves dissent.

## Penalty & Reparation (for completeness) *(spec §5.11, §6.2)*

Tilleggsskatt (additional tax / penalty) cases use these: a
`<lrml:PrescriptiveStatement>` whose violation triggers a
`<lrml:ReparationStatement>` pointing at a `<lrml:PenaltyStatement>` that holds a
`<lrml:SuborderList>` of graded sanctions. See [deontic.md](deontic.md#violation-and-reparation).
The sample `vedtak_endring_av_ligning_og_ileggelse_av_tilleggsskatt…` is the
case to model with these.

## See also

- [ruleml-rules.md](ruleml-rules.md) — the `<ruleml:Rule>` body/head machinery.
- [deontic.md](deontic.md) · [defeasibility.md](defeasibility.md) ·
  [alternatives.md](alternatives.md)
