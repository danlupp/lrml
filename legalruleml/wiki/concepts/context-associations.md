# Associations & Context

These two blocks attach metadata to statements **without** cluttering the rules
themselves — the heart of LegalRuleML's reification (R6). *(spec §5.14, §5.15, §6.1)*

## Association *(spec §5.14)*

`<lrml:Association>` is an N:M link between a set of statements and a set of
metadata (sources, agents, times, temporal characteristics, …). It lives in the
top-level `<lrml:Associations>` block.

```xml
<lrml:Associations>
  <lrml:Association>
    <lrml:appliesSource keyref="#ref-fsfin-6-44-4"/>
    <lrml:appliesAuthority keyref="#auth-skatteklagenemnda"/>
    <lrml:appliesJurisdiction keyref="#jur-norge"/>
    <lrml:appliesTemporalCharacteristic keyref="#tc-2022"/>
    <lrml:toTarget keyref="#ps-fradrag"/>
  </lrml:Association>
</lrml:Associations>
```

The `applies*` edges name *what* metadata is applied; `<lrml:toTarget>` names
*which* statement(s) it applies to. Both sides accept multiple edges, giving the
N:M relation. The `applies*` edges must come **before** the `toTarget` edges.

> **An Association is a cross-product.** The XSD documents it as *"a partial
> description of the extension of some relations where each non-target entity is
> **paired with every** target entity"*. Three sources and fourteen targets
> assert 42 links — including every rule↔provision pair you never intended.
> Hence the project rule: **one hjemmel per Association**, keyed, targeting only
> the fragments actually read out of that provision. Metadata that genuinely
> applies broadly (authority, jurisdiction) goes in its own source-free
> Association. Full rules: [hjemmel-anchoring.md](hjemmel-anchoring.md).

This is the **complete** set of `applies*` edges on an Association (the XSD
allows nothing else — in particular there is no `appliesTemporal`,
`appliesTime`, `appliesRole`, `appliesAgent` or `appliesLegalReference`):

- `<lrml:appliesSource>` — tie to hjemmel: resolves to a `LegalReference`
  (`@refersTo`) or `LegalSource` (`@key`) (→ [sources](sources-isomorphism.md)).
- `<lrml:appliesAuthority>` — the enacting/deciding authority (→ [metadata](metadata.md)).
- `<lrml:appliesJurisdiction>` — the jurisdiction (→ [metadata](metadata.md)).
- `<lrml:appliesTemporalCharacteristic>` / `<lrml:appliesTemporalCharacteristics>`
  — temporal scoping, one characteristic or a whole block (→ [temporal](temporal.md)).
- `<lrml:appliesModality>`, `<lrml:appliesStrength>` — modal/strength tagging.

(Agents and Roles are *not* attached via associations — a `<lrml:Role>` wires
itself to its agent and expression with `filledBy`/`forExpression`; see
[metadata.md](metadata.md).)

## Context *(spec §5.15)*

`<lrml:Context>` bundles a coherent set of associations/metadata under one key —
a named "interpretation environment" or *world*. A statement can then be read
*in a context*, and the same statement can have different properties in
different contexts (e.g. different inntektsår versions, or majority vs minority
interpretation).

```xml
<lrml:Context key="ctx-2022">
  <lrml:appliesTemporalCharacteristic keyref="#tc-inntektsaar-2022"/>
  <lrml:inScope keyref="#ps-fradrag"/>
</lrml:Context>
```

- A Context takes the same `applies*` edges as an Association, plus
  `<lrml:appliesAssociation>`/`<lrml:appliesAssociations>` to pull in whole
  association (blocks) by reference — then `<lrml:inScope>` **last**.
- `<lrml:inScope>` — the statements the context governs.
- A Context groups the metadata that holds *for that reading/version*, which is
  how alternatives and temporal versions are kept apart without duplicating the
  rule body.

> **Vedtak mapping:**
> - Use one **Association** per hjemmel — never several provisions in one — and
>   target only the statements and rule fragments read out of it
>   ([hjemmel-anchoring.md](hjemmel-anchoring.md)).
> - Use a **Context** per inntektsår/version when parameters change (terskelbeløp
>   3 300 for ≤2022 vs 5 000 from 2023), pairing it with a
>   [`TemporalCharacteristic`](temporal.md).
> - Attribute each competing reading directly through its procedural Role. Use
>   an adjudication **Context** with `appliesAlternatives` and `inScope` to name
>   the legal rendering selected by the decision. This selection convention is
>   the repository profile; Context does not replace Role attribution
>   ([voices-and-attribution.md](voices-and-attribution.md)).

## See also

- [hjemmel-anchoring.md](hjemmel-anchoring.md) — one hjemmel per Association,
  pinpoint sources, fragment-level targets.
- [sources-isomorphism.md](sources-isomorphism.md) · [metadata.md](metadata.md) ·
  [temporal.md](temporal.md) · [alternatives.md](alternatives.md) ·
  [voices-and-attribution.md](voices-and-attribution.md)
