# Alternatives — competing interpretations

`<lrml:Alternatives>` groups two or more **mutually competing** modellings of the
same legal material, so the document can carry several readings at once
(requirement R5). *(spec §5.12, §6, tutorial §2)*

```xml
<lrml:Alternatives key="alt-ferge">
  <lrml:hasAlternative keyref="#cs-ferge-sekretariat"/>
  <lrml:hasAlternative keyref="#cs-ferge-skattepliktig"/>
</lrml:Alternatives>
```

The members are `<lrml:hasAlternative>` **edges** (there is no
`<lrml:Alternative>` element), each referencing — or containing — one legal
statement/context. The alternatives are *not* simultaneously asserted as true:
they are candidate legal renderings. This repository records the adjudicative
selection with a [Context](context-associations.md) carrying
`appliesAlternatives` and `inScope`. An [`<lrml:Override>`](defeasibility.md) is
appropriate only when the legal rules also stand in an actual defeasible
superiority relation.

## The interpretation templates *(spec §6, tutorial)*

LegalRuleML recognizes recurring ways a text can be interpreted; an Alternatives
block typically captures one of:

- **Different definitions** of a term (what counts as *ferge* / *rimeligste*).
- **Different scopings** of a rule (broad vs narrow application).
- **Conflicting deontic effects** (permission vs prohibition).
- **Version differences** over time (handled jointly with [temporal](temporal.md)).

## Mapping disputes in a vedtak

> **Vedtak mapping:**
> 1. Identify whether the dispute concerns a legal rendering or merely competing
>    factual allegations. Keep factual allegations as separately attributed
>    `FactualStatement`s outside `Alternatives`.
> 2. For competing legal renderings, model each side as its own statement (often a
>    [ConstitutiveStatement](statements.md) for definitional disputes, a
>    PrescriptiveStatement for conclusion disputes).
> 3. Group them in `<lrml:Alternatives>`.
> 4. Attribute each statement directly through the relevant procedural Role.
> 5. Use an adjudication [Context](context-associations.md) to scope the adopted
>    statement. Add an [`<lrml:OverrideStatement>`](defeasibility.md) only when
>    the document supplies a Legal Rule priority such as lex specialis.
>
> The rejected reading is preserved — capturing *both* sides of the
> argumentation is the purpose of the model. The `vedtak_syntetisk_uenighet`
> and `vedtak_frodo_ferge` (the robåt sub-issue) samples are the cases to model
> this way.

## See also

- [defeasibility.md](defeasibility.md) — Override for Legal Rule superiority.
- [context-associations.md](context-associations.md) — scoping each reading.
- [voices-and-attribution.md](voices-and-attribution.md) — attributing each reading.
- [statements.md](statements.md) — the statement types being compared.
