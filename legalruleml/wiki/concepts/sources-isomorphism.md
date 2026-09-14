# Sources & isomorphism — tying rules to the hjemmel

**Isomorphism** (requirement R4) means each formal rule maps back to the
textual provision it formalizes, so the model stays traceable to the law.
LegalRuleML provides a reference layer for this. *(spec §2.3, §5.9, §6.1)*

## The reference vocabulary *(spec §5.9)*

| Element | Role |
|---|---|
| `<lrml:LegalSources>` / `<lrml:LegalSource>` | A legal text resource (a statute, a paragraph) identified by IRI (`@key` + `@sameAs`). |
| `<lrml:LegalReferences>` / `<lrml:LegalReference>` | A reusable citation record: a non-IRI identifier (`@refID`) plus the system that disambiguates it (`@refIDSystemName`), with its own internal id in `@refersTo`. |
| `<lrml:Sources>` / `<lrml:Source>` | A generic (non-legal) source resource. |
| `<lrml:References>` / `<lrml:Reference>` | A citation record for a generic source. |

```xml
<lrml:LegalReferences>
  <lrml:LegalReference refersTo="ref-fsfin-6-44-4"
       refID="FSFIN § 6-44-4"
       refIDSystemName="rettsinformasjon-aliaser"/>
</lrml:LegalReferences>
<lrml:LegalSources>
  <lrml:LegalSource key="src-fsfin-6-44-4"
  sameAs="forskrift-1999-11-19-1158/section:6-44-4"/>
</lrml:LegalSources>
```

- `@refID` — the human/citation identifier of the provision ("FSFIN § 6-44-4").
- `@refIDSystemName` (and optional `@refIDSystemSource`) — the naming system the
  refID belongs to.
- `@refersTo` — the reference's **internal id** (an NCName; no `@key` is allowed
  on references). Association edges resolve to it: `keyref="#ref-fsfin-6-44-4"`
  matches `refersTo="ref-fsfin-6-44-4"`.
- `@sameAs` (on the LegalSource) — the canonical external identity of the text.
  Prefer the exact Rettsregister `resource_id` returned through Rettsrev. If the
  API is unavailable or does not resolve the citation, retain the normalized
  `urn:rettskilde:no:…` from `rettsreferanser.json` and report the fallback.
  Successful verified mappings are persisted on that URN entry as
  `rettsrevResourceId` and `rettsrevCanonicalRef`; fallback results never write
  those fields.

> **Project rule (isomorphism-first):** take the citation from
> `rettsinformasjon.json` — its `aliaser` give the `@refID`/`@refIDSystemName`.
> Mint a readable internal id for `@refersTo` (`ref-<hjemmel>`), and resolve the
> registered citation with `vedtak-legalruleml resolve-source`. Put the returned
> `selected_id` in `LegalSource@sameAs`. Rettsregister stops at section/article;
> keep cited ledd/bokstav/punktum in the local reference and fallback URN even
> when several pinpoints share one external section ID. The vedtak's
> `*.config.json` lists the `rettsgrunnlag` actually used; create one
> `<lrml:LegalReference>` per cited provision.

## Connecting reference → rule

The reference layer is connected to statements through an
[`<lrml:Association>`](context-associations.md), keeping the link explicit and
N:M (one provision ↔ many rules, one rule ↔ many provisions):

```xml
<lrml:Associations>
  <lrml:Association key="assoc-fsfin-6-44-4">
    <lrml:appliesSource keyref="#ref-fsfin-6-44-4"/>
    <lrml:appliesSource keyref="#src-fsfin-6-44-4"/>
    <lrml:toTarget keyref="#ps-fradrag"/>
  </lrml:Association>
</lrml:Associations>
```

This says: the rule `ps-fradrag` formalizes the provision referenced by
`ref-fsfin-6-44-4`. See [context-associations.md](context-associations.md) for
the full Association mechanism and the `applies*` edges.

> **The link is only as precise as you make it.** An Association pairs *every*
> source with *every* target, so one Association carrying several provisions
> and many statements claims that all of them derive from all of them. Which
> paragraph — down to the ledd — a given rule, vilkår or finding comes from is
> governed by **[hjemmel-anchoring.md](hjemmel-anchoring.md)**: pinpoint
> sources, one hjemmel per Association, keys on the individual
> `<ruleml:Atom>`s, and the statutory wording in the sidecar. Read that page
> before writing the `Associations` block.

## Why a separate layer (not just attributes)

Keeping references in their own block lets several rules share a reference, lets
a reference be reused across versions, and lets the rule↔text mapping carry its
own metadata (author, time) — the basis of LegalRuleML's authorial tracking and
temporal versioning. *(tutorial §3)*

## Source quotes with W3C PROV — the sidecar file {#vedtak-quotes}

Beyond linking rules to the *hjemmel*, we also want each modelled fragment to
carry the **exact passage** it formalizes — text-level isomorphism. LegalRuleML's
`<lrml:Source>`/`<lrml:LegalSource>` and `<lrml:Reference>` only *point* at
external text (e.g. Akoma Ntoso), and `<lrml:Paraphrase>` inlines a quote but
buries it inside the logic and cannot record *which* text it was quoted from.

We anchor quotes with the **W3C PROV vocabulary**
([PROV overview](https://www.w3.org/TR/prov-overview/)) in a **sidecar file**
`<name>.prov.xml` next to `<name>.lrml`. The OASIS XSD has no extension point
for foreign markup, so PROV inside the `.lrml` (as an embedded `<prov:Bundle>`
or `prov:wasDerivedFrom` attributes) makes the file schema-invalid — the
sidecar keeps the `.lrml` fully conformant while preserving the quote layer.

The sidecar holds two things:

1. **Quote entities** — one `<prov:Entity xml:id="quote-…">` per anchored
   passage: verbatim text in `<prov:value>`, plus `<prov:wasQuotedFrom>` edges
   naming the `<lrml:LegalSource>` (by key) the text came from.
2. **Derivation links** — one `<prov:wasDerivedFrom>` per anchored fragment,
   connecting the fragment's `@key` in the `.lrml` (`prov:generatedEntity`) to
   its quote (`prov:usedEntity`). The `.lrml` itself contains **no** PROV.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prov:Bundle xml:id="prov-text-anchors"
    xmlns:prov="http://www.w3.org/ns/prov#">

  <!-- the rule paraphrases the provision -->
  <prov:Entity xml:id="quote-r-fradrag">
    <prov:value>Etter FSFIN § 6-44-4 gis fradrag for kostnader til ferge og bom
      ved arbeidsreise dersom kostnadene overstiger terskelbeløpet […]</prov:value>
    <prov:wasQuotedFrom prov:resource="#src-fsfin-6-44-4"/>
  </prov:Entity>
  <!-- a finding is quoted from the vedtak itself -->
  <prov:Entity xml:id="quote-fs-terskel-2022">
    <prov:value>Dokumenterte fergekostnader for inntektsåret 2022 utgjør kr 7 800
      og overstiger terskelbeløpet på kr 3 300. Vilkåret om terskelbeløp er for
      inntektsåret 2022 oppfylt.</prov:value>
    <prov:wasQuotedFrom prov:resource="#src-vedtak-skn-2023-0042"/>
  </prov:Entity>

  <prov:wasDerivedFrom prov:generatedEntity="vedtak_x.lrml#r-fradrag"
                       prov:usedEntity="#quote-r-fradrag"/>
  <prov:wasDerivedFrom prov:generatedEntity="vedtak_x.lrml#fs-terskel-2022"
                       prov:usedEntity="#quote-fs-terskel-2022"/>
</prov:Bundle>
```

In the `.lrml`, declare each source once (the vedtak **and** the cited
provision), so the `prov:wasQuotedFrom` edges resolve, and tie the statements to
the vedtak source via an `<lrml:Association>`:

```xml
<lrml:LegalSources>
  <lrml:LegalSource key="src-fsfin-6-44-4" sameAs="urn:…:paragraf:6:del:44:del:4"/>
  <lrml:LegalSource key="src-vedtak-skn-2023-0042" sameAs="urn:skatteklagenemnda:SK-2023-0042"/>
</lrml:LegalSources>
…
<lrml:Association>
  <lrml:appliesSource keyref="#src-vedtak-skn-2023-0042"/>
  <lrml:toTarget keyref="#stmts"/>
</lrml:Association>
```

Conventions:
- **Verbatim** quote where one sentence maps to the fragment; use a modeller
  paraphrase only where no single sentence fits (e.g. for an `<lrml:Override>`,
  which states the superiority, not a vedtak sentence).
- **Statutory wording gets its own entity**, `quote-hjemmel-<source-stem>`,
  quoted from the provision source *and* (when the vedtak reproduces it) from
  the vedtak source. A rule then carries two derivation links: the law it
  formalizes, and the passage applying it
  ([hjemmel-anchoring.md §layer-4](hjemmel-anchoring.md)).
- Mark omissions with `[…]`. Keep Norwegian wording exactly as written.
- One `<prov:Entity>` per anchored fragment; name it `quote-<fragment-key>` so
  the derivation link is easy to read. A shared quote (e.g. a rule text
  paraphrasing two versions) may carry several `<prov:wasQuotedFrom>` edges.
- `prov:generatedEntity` names the fragment's `@key` (RuleML keys with the
  leading colon stripped: `:r-fradrag` → `…lrml#r-fradrag`). Anchor the
  **Expression** node (`Rule`/`Atom`) or the statement key when the fragment
  has no own key (an `Override` → the `OverrideStatement` key).
- Every `prov:usedEntity` must resolve to a `<prov:Entity xml:id>` in the
  sidecar; every `prov:wasQuotedFrom` `@prov:resource` and
  `prov:generatedEntity` must resolve to a key in the `.lrml` —
  `legalruleml/bin/validate_lrml.py` checks all three.
- If the vedtak is later marked up in Akoma Ntoso, add a fine-grained
  `<lrml:Reference>` (`@refID` = fragment locator) alongside the anchor for
  machine-resolvable pinpointing.

Worked example: see [worked-example.md §4](../mapping/worked-example.md#4-the-prov-sidecar-vedtak_frodo_fergeprovxml).

## See also

- [hjemmel-anchoring.md](hjemmel-anchoring.md) — the rules that make the link
  *precise*: pinpoints, one hjemmel per Association, fragment-level anchors.
- [context-associations.md](context-associations.md) — Association & Context.
- [identifiers.md](identifiers.md) — `@key`/`@keyref`/`@sameAs`, CURIEs.
- [metadata.md](metadata.md) — authority/jurisdiction that often co-travels.
