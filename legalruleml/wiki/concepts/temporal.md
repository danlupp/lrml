# Temporal management

Legal rules change over time, and they reason about time. LegalRuleML separates
several temporal dimensions and lets a rule's parameters be version-selected.
*(spec §5.9.x, §6.3, tutorial §3)*

## Time instants and the metadata block

`<ruleml:Time>` represents an instant (via a contained `<ruleml:Data>`). Times
live in `<lrml:Times>` in the metadata category and are referenced by `@keyref`
/ `@hasCreationDate`. Two schema constraints to respect:

- the `@key` is a **RuleML** key → must be a CURIE (`:t-2022`), not a bare name;
- the `Data` only accepts `xs:dateTime`, `xs:date` or `xs:duration` — **not**
  `xs:gYear`. Represent an inntektsår by its January 1.

```xml
<lrml:Times>
  <ruleml:Time key=":t-2022">
    <ruleml:Data xsi:type="xs:date">2022-01-01</ruleml:Data>
  </ruleml:Time>
</lrml:Times>
```

## TemporalCharacteristics *(spec §6.3)*

`<lrml:TemporalCharacteristics>` / `<lrml:TemporalCharacteristic>` describe *how*
a statement relates to time. A single norm typically has several legal
"timelines":

- **In force / enforceability** — when the norm is part of the legal system.
- **Efficacy** — when the norm produces effects.
- **Applicability** — when the norm applies to facts (e.g. to a given
  inntektsår).

Each characteristic ties a `<ruleml:Time>` to a *status* (`forStatus`) and
optionally a *status development* (`hasStatusDevelopment`: the norm
starts/ends having that status). The child order is fixed:
`forStatus? hasStatusDevelopment? atTime?` — the time edge is **`atTime`**
(there is no `hasTime` element). Status and development IRIs come from the
LegalRuleML vocabulary `http://docs.oasis-open.org/legalruleml/ns/v1.0/vocab#`:
`Applicable`, `Efficacious`, `InForce`; `Starts`, `Ends`.

```xml
<lrml:TemporalCharacteristics>
  <lrml:TemporalCharacteristic key="tc-fsfin-2022">
    <lrml:forStatus iri="http://docs.oasis-open.org/legalruleml/ns/v1.0/vocab#Applicable"/>
    <lrml:atTime keyref="#t-2022"/>
  </lrml:TemporalCharacteristic>
</lrml:TemporalCharacteristics>
```

Wire it to a statement via
[`appliesTemporalCharacteristic`](context-associations.md) on an Association,
or scope it inside a [Context](context-associations.md).

## Versioning a rule's parameters

When a threshold or value changes between years, do **not** edit the rule body;
instead keep one rule and select the parameter version via a
[Context](context-associations.md) + `TemporalCharacteristic`, or model two
alternative statements distinguished by their temporal characteristic.

> **Vedtak mapping:**
> - The **inntektsår** of the case (e.g. 2022) → a `<ruleml:Time key=":t-2022">`
>   (`xs:date` 2022-01-01) and a `TemporalCharacteristic` with
>   `forStatus` = `vocab#Applicable`; tie it to every rule via an Association
>   (`appliesTemporalCharacteristic`) or a `Context`.
> - A **parameter that changed by year** — e.g. *bunnbeløp/terskelbeløp* kr 3 300
>   (income years ≤ 2022) vs kr 5 000 (from 2023) — is version-selected by the
>   case's inntektsår Context, so the right threshold Atom is the one in scope.
> - The vedtak's **decision date** → root `@hasCreationDate` → a `<ruleml:Time>`.

## See also

- [context-associations.md](context-associations.md) — Context/Association scoping.
- [metadata.md](metadata.md) · [document-structure.md](document-structure.md)
