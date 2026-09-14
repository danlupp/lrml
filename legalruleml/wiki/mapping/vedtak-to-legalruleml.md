# Playbook: vedtak → LegalRuleML

The core procedure. Input: a `vedtak_*.md` plus its `*.config.json` and
`rettsinformasjon.json`. Output: one compact LegalRuleML file (`<name>.lrml`),
a PROV quote sidecar (`<name>.prov.xml`), and a document-local canonical
relation manifest (`<name>.relations.json`). Follow the steps in order; each
cites the concept page with the details. See
[worked-example.md](worked-example.md) for a complete run.

## Step 0 — Read the inputs

- The vedtak text (`vedtak_*.md`) — understand the dispute and the outcome.
- The `*.config.json` — `rettsgrunnlag`/`tonto` used, and `instansiering_hint`
  (rettssubjekt = skattepliktige, pliktsubjekt = skattemyndigheten).
- `rettsinformasjon.json` — for each cited provision get `hjemmel_id`, `aliaser`,
  and the relevant `versjon`/`parametre` for the case's inntektsår.

See [vedtak-anatomy.md](vedtak-anatomy.md) for section-by-section orientation.

Before emitting XML, build an **argument inventory** with one row per material
contribution: Actor, procedural Role, keyed expression, and document status
(alleged / earlier decision / recommended / adopted / dissent). Keep the
skattyter, skattekontor, sekretariat, nemnd, and any minority separate even when
they endorse the same expression. This inventory controls the direct Role links
in step 3 and prevents the final voice from erasing earlier arguments
([voices-and-attribution.md](../concepts/voices-and-attribution.md)).

Before naming any relation, build two more linked inventories across the whole
decision:

- An **entity identity map**: the same person, transaction, event, object,
  amount, or period reuses one `Ind` IRI or typed `Data` value across voices.
- A **relation vocabulary**: one row per truth condition with canonical
  Norwegian IRI, meaning, arity, ordered argument roles/kinds, all source
  formulations and voices, and planned expression/quote evidence.

Reconcile by truth conditions, not by spelling. Put negation in `ruleml:Neg`
and voice/status in Role/Context. A legally material qualifier becomes a
separate Atom sharing the same entity variable; an incidental qualifier stays
in source evidence. Do not concatenate either into a new predicate name. Keep
nearby concepts separate only when the decision supports a material distinction,
and record that boundary.

## Step 1 — Scaffold the document

Open `<lrml:LegalRuleML>` with namespaces, set `@hasCreationDate` to the vedtak
date, and lay out the top-level blocks in the required order
([document-structure.md](../concepts/document-structure.md#prescribed-order-of-top-level-elements)):
`Prefix*` → metadata → `Associations` → `Alternatives`/`Context`/`Statements`.

## Step 2 — Reference layer (isomorphism)

For every cited **pinpoint** — the deepest level the vedtak actually cites:
paragraf → del → ledd → bokstav → punktum — create a
[`<lrml:LegalReference>`](../concepts/sources-isomorphism.md) and
`<lrml:LegalSource>`. "Etter FSFIN § 6-44-4 …" gives `…:del:4`; "FSFIN
§ 6-44-1, 2 ledd" gives `…:del:1:ledd:2` with key stem `-l2`. Never guess a
deeper level than the text gives ([hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)).

- `@refID` = an alias from `rettsinformasjon.json` (e.g. `"FSFIN § 6-44-4"`).
- `@refIDSystemName` = the alias system (`rettsinformasjon-aliaser`).
- `@refersTo` = the reference's own internal id (an NCName like
  `ref-fsfin-6-44-4`) — this is what `keyref="#…"` edges resolve to; a
  LegalReference takes **no** `@key`.
- Resolve each law/regulation with `vedtak-legalruleml resolve-source`, using the
  registered URN from `rettsreferanser.json` as `--legacy-id` and passing
  `--register samples/in/rettsreferanser.json` to persist verified mappings.
- `LegalSource@sameAs` = the exact returned `selected_id`: normally a
  Rettsregister section/article ID; the unchanged registered URN when Rettsrev
  is unavailable or unresolved. Report every fallback and never derive a
  Rettsregister ID from the URN.
- Rettsregister stops at section/article depth. Keep a cited ledd/bokstav as a
  distinct local source and Association even when it shares `@sameAs` with
  another pinpoint in that section.
- Also declare the **vedtak itself** as a LegalSource — the quote sidecar (step
  6b) quotes findings from it.

## Step 3 — Provenance & jurisdiction metadata

Create [`<lrml:Authority>`](../concepts/metadata.md) (Skatteklagenemnda /
sekretariatet) and `<lrml:Jurisdiction>` (Norge / skatt). Then realize the
argument inventory as [`Agent` + `Role`](../concepts/voices-and-attribution.md):
the Role carries `filledBy` (→ Actor) and one or more direct `forExpression`
edges (→ keyed statements/rules/atoms). Use the profile role fragments
`claimant`, `first-instance-decider`, `recommender`, `decider`, and `dissenter`.
Do not route a Role through Context, and do not invent a final decider in a
recommendation-only document. A separate `author`/`model-author` Role records
authorship of the XML and is not a procedural voice. There is no
`appliesAgent`/`appliesRole` Association edge.

## Step 4 — Temporal scoping & version selection

Create a `<ruleml:Time key=":t-<år>">` for the inntektsår (`xs:date`, its
January 1 — `xs:gYear` is not allowed) and a
[`<lrml:TemporalCharacteristic>`](../concepts/temporal.md) with
`forStatus` = `vocab#Applicable` and `atTime`. If a parameter is
year-dependent (terskelbeløp 3 300 ≤2022 vs 5 000 from 2023), pick the version
matching the case's inntektsår and use that value in the rule; wrap it in a
[`<lrml:Context>`](../concepts/context-associations.md) keyed to the year
(edge: `appliesTemporalCharacteristic`).

Make the parameter **load-bearing**, not decorative: the threshold must appear as
an actual term (a `<ruleml:Data>` argument of the vilkår relation, or a
`<ruleml:Var>` bound by the `Context`), so the 3 300 vs 5 000 versions actually
change what the rule computes. A threshold that lives only in an XML comment
means `tc-2022`/`tc-2023` do no work (pitfall below).

## Step 5 — Build the rule (vilkår = body, consequence = head)

In a [`<lrml:PrescriptiveStatement>`](../concepts/statements.md) put a
[`<ruleml:Rule>`](../concepts/ruleml-rules.md):

- `<ruleml:if>` = `<ruleml:And>` of one `<ruleml:Atom>` **per vilkår**.
- `<ruleml:then>` = the legal consequence. For an entitlement, a
  [`<lrml:Right>`/`<lrml:Permission>`](../concepts/deontic.md) with a
  `<ruleml:slot><lrml:Bearer/>…</ruleml:slot>` naming the skattepliktige.

If the board *defines* a term (what counts as *ferge*, *rimeligste*), make that a
separate [`<lrml:ConstitutiveStatement>`](../concepts/statements.md).

Give a vilkår Atom its own `@key` (`:a-<regel>-<vilkår>`) when its hjemmel
differs from the rule's — the classic case being a term the rule uses but
another provision defines ("nødvendig" in FSFIN § 6-44-1 andre ledd). Step 9
then hangs that provision on the Atom rather than on the whole rule
([hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)). Do not key vilkår
that share the rule's hjemmel.

## Step 6 — Facts (one per satisfied vilkår)

For each *"Vilkåret om X er … oppfylt"*, emit a
[`<lrml:FactualStatement>`](../concepts/statements.md) asserting the
corresponding Atom for this taxpayer (`<ruleml:Ind>` for the person, `Data` for
amounts) — wrapped in an explicit `<lrml:hasTemplate>` (not skippable on facts).
Carry both the concrete cost **and** the year's threshold so the
comparison is machine-checkable. For a vilkår the vedtak finds **not** met, assert
the Atom under `<ruleml:Neg>` (strong negation), e.g. dokumentasjon ikke oppfylt.
Together with the rule, these entail the conclusion.

## Step 6b — Anchor the source quotes with PROV (sidecar file)

For every modelled fragment, capture the **exact passage** it formalizes as a
`<prov:Entity>` in the sidecar file `<name>.prov.xml` (root: `<prov:Bundle>`,
`xmlns:prov="http://www.w3.org/ns/prov#"`) — verbatim text in `<prov:value>`
and a `<prov:wasQuotedFrom>` edge to the LegalSource key it came from
(statutory text → the provision source; a finding → the vedtak source). Link
each fragment to its quote with a
`<prov:wasDerivedFrom prov:generatedEntity="<name>.lrml#<key>"
prov:usedEntity="#quote-<key>"/>` record in the same sidecar. The `.lrml`
itself must contain **no PROV markup** (it would break XSD conformance); tie
the statements block to the vedtak `<lrml:LegalSource>` via an
`<lrml:Association>`. See
[sources-isomorphism §vedtak-quotes](../concepts/sources-isomorphism.md#vedtak-quotes).
Use verbatim text where a single sentence maps; a modeller paraphrase only where
none fits (e.g. for the `<lrml:Override>`).

Capture the **statutory wording** too, not just the vedtak's findings: one
`<prov:Entity xml:id="quote-hjemmel-<source-stem>">` per cited provision, quoted
from the provision source **and** from the vedtak that reproduces it, derived
onto the rule (or onto the keyed vilkår Atom whose ledd it states). A rule
normally ends up with two derivation links: the law, and the passage applying it
([hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)).

## Step 6c — Emit the relation manifest

Write `<name>.relations.json` after the LRML and PROV content is final. It is a
document-local review artifact, not a corpus ontology or a runtime alias table:

```json
{
  "schemaVersion": "1.0",
  "source": "name.lrml",
  "sourceSha256": "<sha256-of-final-lrml-bytes>",
  "relations": [{
    "iri": ":kanTrekkesFra",
    "meaning": "Utgiften kan trekkes fra inntekten",
    "arity": 2,
    "arguments": [
      {"role": "utgift", "kind": "individual"},
      {"role": "inntekt", "kind": "individual"}
    ],
    "usages": ["cs-lesemaate-a", "cs-lesemaate-b"],
    "voices": ["claimant", "recommender"],
    "sourceForms": [{
      "text": "utgiften kommer til fradrag",
      "voice": "claimant",
      "expression": "cs-lesemaate-a",
      "quote": "quote-cs-lesemaate-a"
    }]
  }]
}
```

Use statement keys in `usages`, substantive Role names in `voices`, and one or
more source forms backed by PROV derivations. `arguments.kind` is `individual`
or `data`; a RuleML `Var` may stand in either slot, while concrete `Ind`/`Data`
terms must match it. Add `datatype` for data slots when one datatype is required.
An optional `distinction` explains why a near-synonymous relation remains
separate.

## Step 7 — Disputes, exceptions & dissent

First classify the disagreement; the constructs are not interchangeable:

1. **Competing facts:** keep each allegation as a directly attributed
  `FactualStatement`. Add the deciding body's contrary finding or explicit
  rejection as another statement. Do not use `Alternatives` or `Override`.
2. **Competing legal renderings:** model each reading as its own Prescriptive or
  Constitutive statement, attribute each through its Role, and group the
  mutually exclusive renderings in
  [`<lrml:Alternatives>`](../concepts/alternatives.md). Record the decision in
  a Context with `appliesAlternatives` and `inScope` pointing to the adopted
  reading and operative conclusion.
3. **Actual defeasible rule priority:** add an
  [`<lrml:OverrideStatement>`](../concepts/defeasibility.md) only when one Legal
  Rule defeats another (lex specialis/superior/posterior). Its endpoints must
  be Prescriptive/Constitutive statements, never facts.
4. **Dissent:** attribute majority and minority directly. Use Alternatives only
  for genuinely alternative legal renderings; majority status alone does not
  create an Override.

Keep every material losing argument. A definitional fight must also include the
concrete application and operative result; selection in the abstract
under-models the reasoning.

## Step 8b — State the operative conclusion explicitly

The konklusjon must be *readable from the model*, not merely inferable. For each
inntektsår emit an explicit statement of the result: the granted amount as a
`PrescriptiveStatement` with an **empty body**
(`<ruleml:if><ruleml:And/></ruleml:if>`) and a
[`<lrml:Right>`](../concepts/deontic.md) head carrying the beløp and the år
(kr 7 800 / 2022) — a deontic operator may not sit in a `FactualStatement` —
and each denial as its own `FactualStatement` with a `<ruleml:Neg>` Atom
(kr 9 200 / 2023; the Bruinen sub-claim). Without this, the file captures the
rule and facts but loses the vedtak's actual outcome.

## Step 8 — Penalty / tilleggsskatt (only if present)

If the vedtak imposes tilleggsskatt: model the breached duty as an
[`<lrml:Obligation>`](../concepts/deontic.md); assert the breach as an ordinary
`<lrml:FactualStatement>` with a domain-relation Atom
(e.g. `:harGittUriktigeOpplysninger`) — **not** as a `<lrml:Violation>`, which is
a rule-body formula the schema forbids inside a fact; and model the sanction as a
[`<lrml:PenaltyStatement>`](../concepts/statements.md) linked by a
`<lrml:ReparationStatement>`, grading ordinary vs skjerpet via a
`<lrml:SuborderList>`. (Use `<lrml:Violation keyref="#ps-plikt"/>` only as a
premise in a rule that fires *on* the breach.)

## Step 9 — Associations (hjemmel anchoring)

In `<lrml:Associations>`, tie each statement to its hjemmel, authority,
jurisdiction, and temporal characteristic via
[`<lrml:Association>`](../concepts/context-associations.md) `applies*` +
`<lrml:toTarget>` edges (the only `applies*` edges are Source /
TemporalCharacteristic(s) / Strength / Modality / Authority / Jurisdiction).

Write **one hjemmel per Association**, keyed `assoc-<source-stem>`, carrying at
most one `LegalSource` + its `LegalReference`, and targeting only the fragments
read out of that provision — a rule, a keyed vilkår Atom, the findings applying
it. An Association pairs every source with every target, so a lumped one asserts
rule↔provision links the vedtak never made. Metadata that applies broadly
(authority, jurisdiction, the vedtak as source of the whole `Statements` block)
goes in its own source-free Association
([hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)).

Any declared `<lrml:Agent>` must fill a Role, and every material statement must
be reached by a substantive Role's direct `forExpression`. Distinguish
sekretariatet (innstiller) from Skatteklagenemnda (vedtar) when both appear.

## Step 10 — Validate

Run the project validator against the vendored OASIS schema:

```bash
python3 legalruleml/bin/validate_lrml.py --strict --relations --voices <temporary>/<artifact>.lrml
```

It checks XSD conformance (`legalruleml/xsd-schema/compact/lrml-compact.xsd`),
key uniqueness, `@keyref`/`@over`/`@under` resolution, key-graph acyclicity,
`if`/`then` presence, that no PROV leaked into the `.lrml`, and — when
`<name>.prov.xml` exists — that every `prov:wasDerivedFrom` link resolves on
both ends and every `prov:wasQuotedFrom` names a declared `<lrml:LegalSource>`.
`--strict` additionally makes the hjemmel-anchoring findings errors: a lumped
Association, an unanchored rule statement, an unused fragment key. The voice
profile also checks direct attribution, unused Actors, factual Alternatives,
and non-rule Override endpoints. `--voices` prints Actor/Role/expression edges
separately from Context selections. **Fix every reported error before
finishing.** Then read the traceability table —

```bash
python3 legalruleml/bin/validate_lrml.py --hjemmel <temporary>/<artifact>.lrml
```

— and confirm each rule and vilkår is listed under the provision the vedtak
actually cites for it.

Then confirm by inspection what no schema can check: every contribution in the
argument inventory is present under the right voice; the operative result
(granted/denied amounts per year) is stated explicitly; every year-dependent
parameter is a real term (not a comment); each dispute links to a concrete fact
and denial. Then append a
[log.md](../log.md) entry.

## Quick decision table

| You see in the vedtak | Emit |
|---|---|
| A cited paragraph (FSFIN §…) | `LegalReference` (`@refersTo` internal id) + `LegalSource` (pinpoint URN) + a keyed one-hjemmel `Association` |
| A vilkår whose term another provision defines | `@key` on that `<ruleml:Atom>` + its own `Association` to that pinpoint |
| "fradrag gis dersom … og … og …" | `PrescriptiveStatement` → `Rule`, vilkår = `And` of `Atom`s in `if` |
| "innrømmes fradrag" / "har krav på" | `then` = `Right`/`Permission`, slot `Bearer` = skattepliktige |
| "Vilkåret om X er oppfylt" | `FactualStatement` (`hasTemplate` + Atom) for X |
| "Vilkåret om X er ikke oppfylt" | `FactualStatement` with `<ruleml:Neg>` |
| "hva regnes som *ferge*" (a definition) | `ConstitutiveStatement` |
| taxpayer's factual allegation | attributed `FactualStatement`; deciding finding/rejection as a separate attributed fact |
| taxpayer's rejected legal reading | attributed legal statement + `Alternatives`; adjudication Context selects the adopted reading |
| "innrømmes fradrag med kr N" | empty-body `PrescriptiveStatement` with `Right` head (amount + år) |
| "innrømmes ikke" | `FactualStatement` with `Neg` (amount + år) |
| flertall vs mindretall | direct `decider`/`dissenter` attribution; `Alternatives` only for alternative legal renderings |
| lex specialis/superior/posterior | `Override` between Prescriptive/Constitutive statements |
| year-dependent threshold | version-select via inntektsår `Context` + `TemporalCharacteristic` |
| tilleggsskatt | `Obligation` (duty) + `FactualStatement` (breach) + `PenaltyStatement`/`ReparationStatement` (sanction) |
| Skatteklagenemnda / sekretariatet | `Authority`; Norge/skatt → `Jurisdiction` |
| who claims/recommends/adopts/dissents | `Agent ← filledBy — Role — forExpression → statement/rule/atom` |
| the sentence that justifies a fragment | sidecar quote (`prov:Entity` + `wasQuotedFrom`) linked by a `wasDerivedFrom` record to the fragment's `@key` |

## See also

- [worked-example.md](worked-example.md) · [patterns-and-pitfalls.md](patterns-and-pitfalls.md)
- [../reference/element-cheatsheet.md](../reference/element-cheatsheet.md)
