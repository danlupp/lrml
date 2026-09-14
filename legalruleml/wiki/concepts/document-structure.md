# Document structure, serializations & conformance

## The root element

Every LegalRuleML document has a single Document Node root,
`<lrml:LegalRuleML>` (metamodel type `lrmlmm:LegalRuleMLDocument`). *(spec §5.5.1)*

Optional root attributes *(spec §5.5.1.1)*:

- `@xml:base` — base IRI for resolving relative IRIs.
- `@hasCreationDate` — a *local reference* (`#…`) to a `<ruleml:Time>` (not a
  literal date; Dublin-Core-like semantics).
- `@xsi:schemaLocation` — schema location (only meaningful on the root).
- plus the common Node attributes `@key`, `@keyref`, `@type`.

```xml
<lrml:LegalRuleML
    xmlns:lrml="http://docs.oasis-open.org/legalruleml/ns/v1.0/"
    xmlns:ruleml="http://ruleml.org/spec"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <!-- top-level blocks in prescribed order -->
</lrml:LegalRuleML>
```

## Prescribed order of top-level elements *(spec §5.16)*

The order *between categories* is fixed; order *within* a category is free.
`Comment*` may appear anywhere. Relax-NG-style sketch:

```
Comment*
 & ( Prefix*,
     ( LegalReferences | LegalSources | References | Sources
       | Times | TemporalCharacteristics
       | Agents | Figures | Roles | Authorities | Jurisdictions )*,
     Associations*,
     ( Alternatives | Context | Statements )* )
```

Four categories, in order:

1. **Prefix** declarations (→ [identifiers.md](identifiers.md)).
2. **Metadata**: `LegalReferences`, `LegalSources`, `References`, `Sources`,
   `Times`, `TemporalCharacteristics`, `Agents`, `Figures`, `Roles`,
   `Authorities`, `Jurisdictions` (→ [sources-isomorphism.md](sources-isomorphism.md),
   [temporal.md](temporal.md), [metadata.md](metadata.md)).
3. **Associations** (→ [context-associations.md](context-associations.md)).
4. **Statement-related**: `Alternatives`, `Context`, `Statements`
   (→ [statements.md](statements.md), [alternatives.md](alternatives.md)).

## Serializations *(spec §5.7)*

Two **equivalent, normative** serializations plus a basic dialect:

- **Normalized** — fully striped; *no* edge tags skipped. Closest to the RDF
  abstract syntax. Maximally explicit, maximally verbose.
- **Compact** — every *skippable* edge tag is removed. Same information, less
  XML. Obtained from normalized via the `compactifier` XSLT (and back via the
  `normalizer` XSLT).
- **Basic dialect** — a sublanguage of compact that forbids CURIE abbreviation
  and the `<ruleml:content>` edge, so conformance is checkable by **XSD alone**.
  *(spec §5.8)*

What "skippable" means: in the `lrml` namespace, **Branch-type edges** are
skippable (collection edges, document edges, annotation edges, and `hasTemplate`
on Constitutive/Prescriptive/Override/Penalty/Reparation statements);
**Leaf** and **Leaf/Branch** edges are not. Two caveats the XSD enforces:
`<lrml:hasTemplate>` on a **`FactualStatement`** is *not* skipped (write it
explicitly), and `<lrml:hasAlternative>`/`<lrml:inScope>`/`applies*` edges are
never skipped. Skippable RuleML edges include
`<ruleml:arg>`, `<ruleml:op>`, `<ruleml:formula>`, `<ruleml:declare>`,
`<ruleml:strong>`, `<ruleml:weak>`, `<ruleml:left>`, `<ruleml:right>`,
`<ruleml:torso>`. *(spec §3.8, §5.5.2)*

> **Project default:** emit **compact**. Example — normalized vs compact for an
> Override statement:
>
> Normalized:
> ```xml
> <lrml:hasStatement>
>   <lrml:OverrideStatement>
>     <lrml:hasTemplate>
>       <lrml:Override over="#cs2" under="#cs1"/>
>     </lrml:hasTemplate>
>   </lrml:OverrideStatement>
> </lrml:hasStatement>
> ```
> Compact:
> ```xml
> <lrml:OverrideStatement>
>   <lrml:Override over="#cs2" under="#cs1"/>
> </lrml:OverrideStatement>
> ```

Note: embedded RuleML must match the parent's serialization (compact-in-compact,
normalized-in-normalized); RuleML's "relaxed" serialization is **not** allowed
inside LegalRuleML. *(spec §5.7.2)*. Inside `<ruleml:Rule>`/`<ruleml:Implies>`,
the `<ruleml:if>` and `<ruleml:then>` edges are **not** skippable. *(spec §5.19.6)*

## Conformance *(spec §7)* {#conformance}

A file conforms as a LegalRuleML-XML file if it is well-formed, its root is
`<lrml:LegalRuleML>`, and it validates against at least one schema:

- **Basic Dialect** → valid against `xsd-schema/basic/lrml-basic.xsd`.
- **Compact** → valid against `xsd-schema/compact/lrml-compact.xsd` **or**
  `relaxng/lrml-compact.rnc` (or both).
- **Normalized** → valid against `xsd-schema/normal/lrml-normal.xsd` **or**
  `relaxng/lrml-normal.rnc` (or both).

Additional constraints **not** enforced by either schema (you must respect them):

1. Conformance must hold both before and after Prefix mapping (CURIE expansion).
2. RuleML collection edges (those with `@index`) must have `@index` values
   consistent with sibling order.
3. IRIs (written directly or as CURIEs, after expansion) must conform to RFC 3987.
4. Every `@key` value (after stripping a leading colon on RuleML `@key`) must be
   **unique within the document**.
5. Triples for skippable edges must not be reified with `@rdf:id`.

> **Practical validation:** the compact XSD (plus `ruleml.xsd` and W3C
> `xml.xsd`) is vendored at `legalruleml/xsd-schema/`. Run
>
> ```bash
> python3 legalruleml/bin/validate_lrml.py samples/out/<name>.lrml
> ```
>
> which validates against the XSD **and** checks key uniqueness, `@keyref`
> resolution, `@key`/`@keyref` acyclicity *(spec §5.12)*, `if`/`then`
> presence, and the PROV sidecar links.

Note the schema has **no extension point for foreign namespaces**: PROV markup
(or any non-lrml/ruleml element or attribute) inside the `.lrml` makes it
non-conformant. Source quotes therefore live in the `.prov.xml` **sidecar**
([sources-isomorphism §vedtak-quotes](sources-isomorphism.md#vedtak-quotes)).

## See also

- [identifiers.md](identifiers.md) — `@key`/`@keyref`, CURIEs, distributed syntax.
- [overview.md](overview.md#node-vs-edge-elements-the-striped-syntax) — node/edge dichotomy.
