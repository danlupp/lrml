# Defeasibility & conflict resolution

Legal reasoning is **defeasible**: conclusions hold *unless* defeated by an
exception or a stronger competing rule. LegalRuleML encodes this with rule
*strength* and the *superiority relation*. *(spec §2.2, §6, tutorial §2)*

## Rule strength

A rule's defeasibility is expressed with a `<lrml:hasStrength>` edge inside the
`<ruleml:Rule>` (before `if`), holding one of the strength nodes — or applied
externally via `<lrml:appliesStrength>` on an Association/Context:

```xml
<ruleml:Rule key=":r-hovedregel" closure="universal">
  <lrml:hasStrength><lrml:DefeasibleStrength/></lrml:hasStrength>
  <ruleml:if> … </ruleml:if>
  <ruleml:then> … </ruleml:then>
</ruleml:Rule>
```

| Strength node | Meaning |
|---|---|
| `<lrml:StrictStrength>` | Whenever the body holds, the head holds — no exceptions. |
| `<lrml:DefeasibleStrength>` | The head holds *unless* defeated by a stronger rule/exception. |
| `<lrml:Defeater>` | Cannot derive its head on its own; only *blocks* an opposite defeasible conclusion. |

Most statutory rules with statutory exceptions are **defeasible**. A pure
exception that only prevents an opposite conclusion is a **defeater**.

## Override — the superiority relation *(spec §5.11, §6)*

`<lrml:Override>` (inside an `<lrml:OverrideStatement>`) states that one rule is
**superior** to another; when both fire with conflicting heads, the superior one
wins.

```xml
<lrml:OverrideStatement key="ov-spesialis">
  <lrml:Override over="#ps-spesial" under="#ps-hovedregel"/>
</lrml:OverrideStatement>
```

`@over` defeats `@under`. Override can itself be scoped to a [Context](context-associations.md)
and tied to a temporal status, so superiority can be jurisdiction- or
time-specific.

## Legal precedence principles

The standard meta-rules used to *justify* an Override:

- **Lex specialis** — the more specific rule overrides the general one.
- **Lex superior** — the higher-ranked source overrides the lower (lov > forskrift).
- **Lex posterior** — the later rule overrides the earlier (newer version wins).

Record which principle motivates an Override in a `<lrml:Comment>` or via
metadata, so the argumentation is traceable.

## Conflicting deontic effects

A `<lrml:Permission>` and a `<lrml:Prohibition>` on the same act conflict; a
`<lrml:Right>` may conflict with an `<lrml:Obligation>` on the counterparty.
Resolve with an `<lrml:Override>`, or express the exception as a separate
defeasible rule whose head is the `<ruleml:Neg>`/opposite deontic operator.

## Negation interplay

- `<ruleml:Neg>` — strong negation: asserts the literal is false.
- `<ruleml:Naf>` — negation as failure: holds when the positive cannot be proved
  (defaults / closed-world reasoning). Useful for "med mindre dokumentasjon
  foreligger" style defaults.

See [ruleml-rules.md](ruleml-rules.md#connectives).

## Mapping dissent and disputed readings

> **Vedtak mapping:**
> - Taxpayer's reading vs secretariat's reading of a vilkår, or
>   **flertall vs mindretall** in a split board: attribute each voice directly
>   to its statements. Group genuinely alternative legal renderings in
>   [`<lrml:Alternatives>`](alternatives.md), and record the decision's selection
>   in a Context. Majority status alone is not a defeasible superiority relation.
> - A statutory *unntak* (exception) to a hovedregel → a **defeasible** rule for
>   the hovedregel plus a more specific rule (lex specialis) joined by an
>   `<lrml:Override>`.
> - Competing factual allegations are facts, not rules: preserve their voice
>   attribution and the deciding body's contrary finding, but do not connect
>   them with `Override`.
> - The losing argument is **kept**, not deleted — its presence is the point of
>   modelling the argumentation (R3/R5, see [overview.md](overview.md)).

## See also

- [statements.md](statements.md#overridestatement--the-override-template)
- [alternatives.md](alternatives.md) · [deontic.md](deontic.md) ·
  [context-associations.md](context-associations.md) ·
  [voices-and-attribution.md](voices-and-attribution.md)
