# Hjemmel anchoring — which rule comes from which paragraph

[sources-isomorphism.md](sources-isomorphism.md) introduces the reference layer
(`LegalReference` / `LegalSource` / `Association`). This page is the **normative
rule set** for using it so that every modelled fragment is traceable to the
*specific* piece of legal text it was read out of — not merely to "the statute
somewhere in this file".

A vedtak sentence like

> Det følger av **FSFIN § 6-44-1, 2 ledd** at med *nødvendig* menes at bruk av
> egen bil fører til minst to timer kortere reise- og ventetid …

must produce a model in which the corresponding fragment — here the
*nødvendighet* vilkår — points at `§ 6-44-1 andre ledd`, and **not** at the
`§ 6-44-4` that the surrounding rule comes from.

## The three defects this prevents

1. **Coarse granularity.** A `LegalSource` minted per *statute section*
   (`§ 6-44-4`) cannot express "second ledd", even though the URN scheme in
   `rettsreferanser.json` goes down to `…:ledd:2:bokstav:b`.
2. **Cross-product ambiguity.** The XSD defines an Association as *"each
   non-target entity is paired with **every** target entity"*. An Association
   carrying three sources and fourteen targets therefore asserts **42** links —
   it claims every statement derives from every provision. That is not
   imprecision, it is a false assertion, and it is what consumers read
   (`søksbie` materializes exactly that cross-product).
3. **No statutory text.** A rule's PROV quote is often the *vedtak's* sentence
   about the rule. The wording of the provision itself — the thing the rule
   formalizes — is then nowhere in the artifact.

## Layer 1 — Pinpoint sources

Mint one `LegalReference` + `LegalSource` pair per **pinpoint** actually
invoked, where a pinpoint is the deepest structural level the text cites:
paragraf → del → ledd → bokstav → punktum.

```xml
<lrml:LegalReferences>
  <lrml:LegalReference refersTo="ref-fsfin-6-44-4"
       refID="FSFIN § 6-44-4" refIDSystemName="rettsinformasjon-aliaser"/>
  <lrml:LegalReference refersTo="ref-fsfin-6-44-1-l2"
       refID="FSFIN § 6-44-1 andre ledd" refIDSystemName="rettsinformasjon-aliaser"/>
</lrml:LegalReferences>
<lrml:LegalSources>
  <lrml:LegalSource key="src-fsfin-6-44-4"
    sameAs="forskrift-1999-11-19-1158/section:6-44-4"/>
  <lrml:LegalSource key="src-fsfin-6-44-1-l2"
    sameAs="forskrift-1999-11-19-1158/section:6-44-1"/>
</lrml:LegalSources>
```

Rules:

- **Never invent a pinpoint.** Cite as deep as the vedtak cites, and no deeper.
  "Etter FSFIN § 6-44-4 gis fradrag …" yields `…:del:4`; guessing which *ledd*
  of § 6-44-4 each vilkår sits in would fabricate a citation. Pinpointing is a
  faithfulness requirement, not a completeness score.
- **One key stem per pinpoint**, used for both members of the pair:
  `ref-<stem>` / `src-<stem>`. Build the stem from the URN tail —
  `ledd:2` → `-l2`, `bokstav:b` → `-bb`, `punktum:1` → `-p1`
  (`ref-fsfin-6-44-1-l2`, `src-mval-8-3-l1-bg`).
- **`@sameAs` prefers the exact Rettsregister ID** returned by Rettsrev. Resolve
  the section/article with `vedtak-legalruleml resolve-source`; never construct
  the database ID. If Rettsrev is unavailable or unresolved, use the registered
  legacy URN and report the fallback. Rettsregister does not model ledd or
  bokstav as separate resources, so distinct local pinpoints may share the same
  section-level `@sameAs`; their local keys, references, Associations, and PROV
  links remain distinct.
- **The version dimension is not a pinpoint.** A provision's 2013 wording vs its
  2023 wording is expressed by `appliesTemporalCharacteristic` on the
  Association ([temporal.md](temporal.md)), not by a second source key — unless
  the register genuinely holds a distinct versioned URN, in which case that
  source belongs on the statement that *depends* on the version (typically the
  parameter `FactualStatement` carrying the terskelbeløp).

## Layer 2 — One hjemmel per Association

Because an Association is a cross-product, split the `Associations` block into
two kinds.

**Hjemmel associations** — carry **exactly one** hjemmel and target only the
fragments actually read out of it. Give each one a `@key` so it can be cited,
quoted and reviewed:

```xml
<lrml:Association key="assoc-fsfin-6-44-1-l2">
  <lrml:appliesSource keyref="#ref-fsfin-6-44-1-l2"/>   <!-- the citation -->
  <lrml:appliesSource keyref="#src-fsfin-6-44-1-l2"/>   <!-- its text -->
  <lrml:appliesTemporalCharacteristic keyref="#tc-2013"/>
  <lrml:toTarget keyref="#a-bom-noedvendig"/>
  <lrml:toTarget keyref="#fs-reisetid-2013"/>
</lrml:Association>
```

- At most **one `LegalSource`** and **one `LegalReference`** per Association,
  and they must be the pair for the *same* pinpoint. Two LegalSources on one
  Association is an ambiguous hjemmel — the validator reports it.
- Targets are the fragments derived from *that* pinpoint: a whole statement, or
  individual rule fragments (layer 3).
- Key convention: `assoc-<source-stem>`, plus a discriminator when one provision
  is applied in several years or by several authorities
  (`assoc-fsfin-6-44-4-2013`).

**Metadata associations** — authority, jurisdiction, temporal scoping that
apply broadly. They carry **no** `appliesSource` (except the one association
that names the vedtak itself as the source of the whole `Statements` block) and
may target many statements:

```xml
<lrml:Association key="assoc-vedtak">
  <lrml:appliesSource keyref="#src-vedtak-skn-2022-0117"/>
  <lrml:appliesAuthority keyref="#auth-skl"/>
  <lrml:appliesJurisdiction keyref="#jur-no-skatt"/>
  <lrml:toTarget keyref="#stmts"/>
</lrml:Association>
```

The vedtak-wide association does **not** count as hjemmel coverage for the
statements inside the block: coverage requires an Association that names the
statement (or one of its fragments) as a **direct** target.

## Layer 3 — Fragment-level anchoring (the vilkår)

When the vilkår of one rule come from different provisions — the ordinary case
for a rule whose terms are defined elsewhere — give the individual
`<ruleml:Atom>`s a `@key` and target *them*:

```xml
<lrml:PrescriptiveStatement key="ps-bomfradrag">
  <ruleml:Rule key=":r-bomfradrag" closure="universal">
    <ruleml:if>
      <ruleml:And>
        <ruleml:Atom key=":a-bom-terskel">…</ruleml:Atom>       <!-- § 6-44-4 -->
        <ruleml:Atom key=":a-bom-noedvendig">…</ruleml:Atom>    <!-- § 6-44-1 andre ledd -->
        <ruleml:Atom key=":a-bom-dok">…</ruleml:Atom>           <!-- § 6-44-4 -->
      </ruleml:And>
    </ruleml:if>
    <ruleml:then>…</ruleml:then>
  </ruleml:Rule>
</lrml:PrescriptiveStatement>
```

- A `@key` on a `ruleml:Atom` is **schema-valid** (verified against the vendored
  compact XSD) and needs no other change; like every RuleML key it is a CURIE
  (`:a-…`) and resolves colon-stripped (`keyref="#a-bom-noedvendig"`).
- Key convention: `:a-<rule-stem>-<vilkår>`.
- **Key a vilkår when it earns it** — when its hjemmel differs from the rule's,
  or when a quote is anchored to it. A rule whose vilkår all come from one
  pinpoint needs no atom keys; the statement-level link says everything.
- The head Atom follows the same rule: if the legal *consequence* is granted by
  a different provision than the conditions, key it too.
- This is the only construct that answers "*based on paragraph 3*, if bla then
  blub" precisely: `blub`'s Atom (or the whole rule) points at paragraph 3.

## Layer 4 — The statutory text in the sidecar

Layers 1–3 link a fragment to a provision *identifier*. The provision's
**wording** goes in the `.prov.xml` sidecar next to the vedtak quotes
([sources-isomorphism §vedtak-quotes](sources-isomorphism.md#vedtak-quotes)):

```xml
<prov:Entity xml:id="quote-hjemmel-fsfin-6-44-1-l2">
  <prov:value>Det følger av FSFIN § 6-44-1, 2 ledd at med nødvendig menes at bruk
    av egen bil fører til minst to timer kortere reise- og ventetid […]</prov:value>
  <prov:wasQuotedFrom prov:resource="#src-fsfin-6-44-1-l2"/>   <!-- the provision -->
  <prov:wasQuotedFrom prov:resource="#src-vedtak"/>            <!-- as reproduced in the vedtak -->
</prov:Entity>
<prov:wasDerivedFrom prov:generatedEntity="<name>.lrml#a-bom-noedvendig"
                     prov:usedEntity="#quote-hjemmel-fsfin-6-44-1-l2"/>
```

- Id convention `quote-hjemmel-<source-stem>` distinguishes statutory wording
  from the `quote-<fragment-key>` entities that hold vedtak findings.
- The vedtak usually *reproduces* the provision rather than the modeller reading
  Lovdata. Say so with **both** `wasQuotedFrom` edges — the provision first, the
  vedtak second. Never attribute wording to a provision source that the vedtak
  did not actually reproduce; if the vedtak only summarizes, quote the vedtak
  and leave the provision link to the Association layer.
- A rule statement therefore normally carries **two** derivation links: one to
  the statutory wording, one to the vedtak passage applying it. Both are
  `wasDerivedFrom` records; nothing else changes.

## What the validator enforces

`legalruleml/bin/validate_lrml.py` (see [A.3 of the spec](../../README.md#a3-conformance--validation)):

| Check | Severity |
|---|---|
| `appliesSource` resolves to a `LegalSource`/`LegalReference` (not a Time, Authority, …) | error |
| An Association carries at most one LegalSource and one LegalReference | warning · error under `--strict` |
| Every `PrescriptiveStatement`/`ConstitutiveStatement` is a **direct** target of a hjemmel Association (itself or one of its keyed fragments) | warning · error under `--strict` |
| A keyed rule fragment (`ruleml:Atom@key`) is targeted by some Association | warning · error under `--strict` |
| `wasQuotedFrom` / `wasDerivedFrom` resolve on both ends | error |

`python3 legalruleml/bin/validate_lrml.py --hjemmel <file>.lrml` prints the
traceability table (fragment → refID → URN → quote) for review.

## See also

- [sources-isomorphism.md](sources-isomorphism.md) — the reference vocabulary
  and the PROV sidecar.
- [context-associations.md](context-associations.md) — the Association /
  Context mechanism and the complete set of `applies*` edges.
- [identifiers.md](identifiers.md) — `@key` CURIEs and colon-stripped matching.
- [../mapping/worked-example.md](../mapping/worked-example.md) — a complete file
  using all four layers.
