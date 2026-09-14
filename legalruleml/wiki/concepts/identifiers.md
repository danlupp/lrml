# Identifiers, keys & CURIEs

LegalRuleML stitches a document together with a key/reference system and uses
CURIEs to keep IRIs short. *(spec §5.6, §5.12, §3.8)*

## Keys and references *(spec §5.12)*

- `@key` — a **document-unique** identifier on a Node element. On **LegalRuleML**
  elements it is an NCName (`ps-fradrag`). On **RuleML** elements it must be a
  CURIE or absolute IRI — in practice an empty-prefix CURIE like `:r-fradrag`;
  the leading colon is stripped for the uniqueness check and for `#keyref`
  matching. *(spec §7)* A plain `key="r-fradrag"` on a RuleML element is
  **invalid** against the XSD.
- `@keyref` — references another element's `@key`. Written `#thekey` (a local
  reference). Lets you point to a node defined elsewhere instead of nesting it.
- The `@key`/`@keyref` graph must be **acyclic** *(spec §5.12)*.
- `@keyref` enables the **distributed / split syntax**: define a node once, refer
  to it from many places (the basis of the N:M Association mechanism).
- `LegalReference`/`Reference` take **no `@key`**; their `@refersTo` attribute
  *is* their internal id (see [sources-isomorphism.md](sources-isomorphism.md)).
- A key is also how a fragment *below* statement level becomes referenceable:
  `<ruleml:Atom key=":a-bom-noedvendig">` is schema-valid and lets an
  `<lrml:Association>` tie that single vilkår to the ledd it comes from
  ([hjemmel-anchoring.md](hjemmel-anchoring.md)). `<lrml:Association>` may
  carry a `@key` too — hjemmel associations do.

```xml
<lrml:LegalReference refersTo="ref-1" refID="FSFIN § 6-44-4"/>
…
<lrml:appliesSource keyref="#ref-1"/>   <!-- resolves to refersTo="ref-1" -->
```

## IRI-bearing attributes *(spec §5.6)*

- `@iri` — the IRI denoting the element's meaning (e.g. an ontology term on a
  `<ruleml:Rel>`).
- `@sameAs` — asserts identity with an external IRI (Linked-Data `owl:sameAs`).
- `@type` — the metamodel/ontology type of the element.
- `@refersTo` — on `LegalReference`/`Reference` only: the reference's internal
  id (an NCName, **not** an IRI/CURIE).

All IRIs (direct or via CURIE expansion) must satisfy RFC 3987 *(spec §7)*.

## CURIEs and Prefix *(spec §3.8, §5.6)*

A **CURIE** is a compact IRI `prefix:local` expanded using `<lrml:Prefix>`
declarations at the top of the document. The attributes are `@pre` (the prefix
name — non-empty, no colon) and `@refID` (the IRI it maps to):

```xml
<lrml:Prefix pre="fsfin" refID="https://lovdata.no/forskrift/1999-11-19-1158/"/>
…
<ruleml:Rel iri="fsfin:§6-44-4"/>
```

- The **empty prefix** (`:overstigerTerskelbeloep`, `:r-fradrag`) cannot be
  declared with `<lrml:Prefix>` — it is bound by the **default `xmlns`** on the
  root element (point it at the domain-ontology namespace).
- Conformance must hold **both** before and after Prefix expansion *(spec §7)*.
- The **Basic Dialect** forbids CURIE abbreviation (use full IRIs there)
  *(spec §5.8)* — see [document-structure.md](document-structure.md#serializations).

## sameAs / mergerOf and identity

`@sameAs` links a local node to a canonical external IRI (e.g. a Lovdata URL or
a `rettsinformasjon` id). `mergerOf` (where present) declares a node as the
union of others. Use `@sameAs` to anchor your `<lrml:LegalSource>` to the
official online text. See [sources-isomorphism.md](sources-isomorphism.md).

> **Vedtak mapping conventions:**
> - Give every statement a readable `@key`: `ps-fradrag`, `cs-ferge-sekretariat`,
>   `fs-vilkaar-reisetid`, `ov-flertall`, `ctx-2022` — and RuleML keys the same
>   name with a leading colon (`:r-fradrag`).
> - `LegalReference@refersTo` = a readable internal id (`ref-fsfin-6-44-4`);
>   `@refID` = the citation alias from `rettsinformasjon.json`;
>   `LegalSource@sameAs` = the registered URN / Lovdata URL.
> - Declare a `fsfin:` / `sktl:` Prefix for the forskrift/lov you cite (omit in
>   Basic Dialect); bind the ontology terms via the default `xmlns`.
> - Run `python3 legalruleml/bin/validate_lrml.py <file>` — it checks key
>   uniqueness, reference resolution, and acyclicity along with the XSD.

## See also

- [document-structure.md](document-structure.md#conformance) — uniqueness/acyclicity rules.
- [sources-isomorphism.md](sources-isomorphism.md) · [context-associations.md](context-associations.md)
