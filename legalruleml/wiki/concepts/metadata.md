# Metadata — agents, roles, authority, jurisdiction

Provenance and applicability metadata reify a rule (R6): *who* made it, in *what
role*, under *whose authority*, and in *which jurisdiction*. These live in the
metadata category of the top-level blocks. *(spec §5.9, §6.1)*

## The elements

| Block / element | Meaning |
|---|---|
| `<lrml:Agents>` / `<lrml:Agent>` | A person/organisation/system that plays a role (author, publisher, enacting body). |
| `<lrml:Figures>` / `<lrml:Figure>` | An abstract legal figure/persona that an Agent fills. |
| `<lrml:Roles>` / `<lrml:Role>` | The role an Agent plays (author, editor, bearer, …). |
| `<lrml:Authorities>` / `<lrml:Authority>` | The authority that enacts/decides the norm. |
| `<lrml:Jurisdictions>` / `<lrml:Jurisdiction>` | The jurisdiction (geographic/subject) in which it applies. |

```xml
<lrml:Authorities>
  <lrml:Authority key="auth-skatteklagenemnda"
       sameAs="https://www.skatteetaten.no/…/skatteklagenemnda"/>
</lrml:Authorities>
<lrml:Jurisdictions>
  <lrml:Jurisdiction key="jur-norge-skatt" sameAs="https://…/NO"/>
</lrml:Jurisdictions>
<lrml:Agents>
  <lrml:Agent key="agent-sekretariatet"/>
</lrml:Agents>
<lrml:Roles>
  <lrml:Role key="role-author" iri="https://example.org/roles#author">
    <lrml:filledBy keyref="#agent-sekretariatet"/>
    <lrml:forExpression keyref="#r-fradrag"/>
  </lrml:Role>
</lrml:Roles>
```

Wiring differs by element kind:

- **Authority / Jurisdiction** attach to statements via
  [`<lrml:Association>`](context-associations.md) edges `appliesAuthority`,
  `appliesJurisdiction`.
- **Agent / Role** do **not** have association edges (there is no
  `appliesAgent`/`appliesRole`). The `<lrml:Role>` itself carries the link:
  `<lrml:filledBy keyref>` names the Agent(s) filling it, and
  `<lrml:forExpression keyref>` directly names the expression
  (statement/rule/atom) the role is played for. It does not name a Context. A
  `<lrml:Figure>` similarly uses `hasFunction` + `hasActor`.

## Document creation metadata

The root `<lrml:LegalRuleML>` carries `@hasCreationDate` pointing to a
`<ruleml:Time>` (see [document-structure.md](document-structure.md) and
[temporal.md](temporal.md)). Authorship of the *model* (you, the agent) is a
`<lrml:Role>` = author on an `<lrml:Agent>`.

> **Vedtak mapping:**
> - `<lrml:Authority>` = **Skatteklagenemnda** (and/or *sekretariatet* who
>   prepares the innstilling). Pull names from the vedtak header / `config.json`.
> - `<lrml:Jurisdiction>` = **Norge / skatterett**.
> - `<lrml:Agent>` + `<lrml:Role>`(author, `filledBy` the agent,
>   `forExpression` the main rule) = the model's author (this pipeline).
> - Also represent procedural voices: skattepliktig=`claimant`,
>   skattekontor=`first-instance-decider`, sekretariat=`recommender`,
>   nemnd=`decider`, and mindretall=`dissenter`. Each Role points directly to
>   the expressions that voice advances. See
>   [voices-and-attribution.md](voices-and-attribution.md).
> - Bearer/AuxiliaryParty still identify parties inside deontic effects; they do
>   not replace voice attribution.

## See also

- [context-associations.md](context-associations.md) — how metadata attaches.
- [voices-and-attribution.md](voices-and-attribution.md) — procedural voices
  and direct responsibility for expressions.
- [temporal.md](temporal.md) — time metadata. · [sources-isomorphism.md](sources-isomorphism.md)
