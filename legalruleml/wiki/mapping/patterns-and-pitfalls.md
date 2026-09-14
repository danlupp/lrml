# Patterns & pitfalls

Reusable patterns distilled from the [playbook](vedtak-to-legalruleml.md) and the
[worked example](worked-example.md), plus mistakes to avoid.

## Patterns

### P1 — Vilkår list ⇒ conjunctive body
Every statutory condition becomes one `<ruleml:Atom>` in a single
`<ruleml:And>` inside `<ruleml:if>`. Keep one Atom per vilkår (do not merge two
vilkår into one Atom) so each can be paired with its own
[`FactualStatement`](../concepts/statements.md) and cited back to the text.

### P2 — Fact mirrors condition
For each "Vilkåret om X er oppfylt", emit a `FactualStatement` whose Atom uses
the **same relation** as the body Atom, but with the concrete `<ruleml:Ind>`
(the taxpayer) and `Data` (amounts) instead of `<ruleml:Var>`. Rule + facts
should entail the conclusion.

### P3 — Definition dispute ⇒ Constitutive + Alternatives + Context
A disagreement about what a term *means* (ferge, rimeligste, pendler) is two
[`ConstitutiveStatement`](../concepts/statements.md)s grouped in
[`Alternatives`](../concepts/alternatives.md), directly attributed to their
voices, with an adjudication [`Context`](../concepts/context-associations.md)
selecting the adopted reading.

### P4 — Dissens ⇒ direct voice attribution
Split decisions: attribute flertall and mindretall reasoning through `decider`
and `dissenter` Roles. Group only genuinely alternative legal renderings in
`Alternatives`; majority status alone does not establish `Override`.

### P5 — Year-dependent parameter ⇒ Context + TemporalCharacteristic
Do not bake one threshold into the rule as if timeless. Select the version for
the case's inntektsår via a `Context` + [`TemporalCharacteristic`](../concepts/temporal.md),
sourcing the value from `rettsinformasjon.json` `versjoner`/`parametre`.

### P6 — Always tie a rule to its hjemmel — one hjemmel per Association
Every rule statement gets a [`LegalReference`](../concepts/sources-isomorphism.md)
and an [`Association`](../concepts/context-associations.md). An untraceable rule
defeats the purpose (isomorphism, R4). Make the tie *precise*: pinpoint the
citation as deep as the text goes (§ → ledd → bokstav), key the Association, and
give it **exactly one** provision. When a single vilkår rests on another
provision, key that `<ruleml:Atom>` and anchor it there
([hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)).

### P7 — Entitlement vs duty vs definition
- "innrømmes fradrag" / "har krav på" → [`Right`/`Permission`](../concepts/deontic.md).
- "plikter" / "skal" → `Obligation`. "kan ikke" → `Prohibition`.
- "regnes som" / "anses som" (a definition) → `ConstitutiveStatement` (no deontic head).

### P8 — State the operative conclusion explicitly
The vedtak's result (granted kr 7 800 for 2022; denied kr 9 200 for 2023) must be
*readable from the model*, not just inferable from rule + facts. Emit an explicit
statement per inntektsår — the grant as an **empty-body `PrescriptiveStatement`**
(`<ruleml:if><ruleml:And/></ruleml:if>`) with a [`Right`](../concepts/deontic.md)
head carrying beløp **and** år (a deontic head cannot live in a
`FactualStatement`), each denial as its own `FactualStatement` with `Neg`.

### P9 — Year-dependent parameter must be a real term
The threshold that distinguishes the year versions must be an actual
`<ruleml:Data>`/`<ruleml:Var>` term in the rule and facts (e.g.
`:overstigerTerskelbeloep(skattepliktig, beløp, terskel)`), so the `Context`'s
choice of 3 300 vs 5 000 changes what the rule computes. A value that exists only
in a comment makes `tc-2022`/`tc-2023` cosmetic.

### P10 — Connect a definitional dispute to its concrete effect
A [P3](#p3--definition-dispute--constitutive--alternatives--context) dispute is
incomplete until a `FactualStatement` applies the adopted definition to the
concrete reise and a statement records that the sub-claim was denied. Don't leave
the Context selection resolving a definition in the abstract.

### P11 — Anchor quotes with PROV in the sidecar, never in the `.lrml`
Capture each fragment's justifying passage as a `<prov:Entity>` in the
`<name>.prov.xml` sidecar — verbatim text in `<prov:value>`, a
`<prov:wasQuotedFrom>` edge to its
[`LegalSource`](../concepts/sources-isomorphism.md#vedtak-quotes) key — and link
fragment→quote with a `<prov:wasDerivedFrom prov:generatedEntity="…lrml#<key>"
prov:usedEntity="#quote-…"/>` record. Statutory-rule text is quoted from the
provision source; a finding is quoted from the vedtak source. The sidecar keeps
the `.lrml` schema-conformant (the OASIS XSD rejects foreign markup), keeps the
quote layer out of the logic, and lets one quote be reused by several fragments.
(Supersedes both the inline `<lrml:Paraphrase>` convention and the earlier
embedded `<prov:Bundle>`.)

### P12 — Reconcile relations across voices before XML
Read every voice before naming predicates. The same truth condition and ordered
argument roles use one canonical relation IRI throughout the decision, and the
same referent reuses one `Ind` IRI. Put polarity in `Neg`, procedural status in
Role/Context, and time in terms/Context. When one formulation adds a legally
material qualifier, model the qualifier as another Atom over the same entity;
do not create a longer relation name that hides the shared premise. Record the
canonical vocabulary, source formulations, voices, usages, and quote evidence
in `<name>.relations.json`, then validate with `--relations`.

## Pitfalls

- **Deleting the losing argument.** A rejected legal reading stays as an
  Alternative; a rejected factual allegation stays as an attributed fact. The
  model captures *argumentation*, not just the outcome.
- **Skipping `<ruleml:if>`/`<ruleml:then>` in compact.** These edges are **not**
  skippable even in compact serialization
  ([document-structure.md](../concepts/document-structure.md#serializations)).
- **Duplicate or dangling keys.** Every `@key` must be document-unique and every
  `@keyref` must resolve; the key graph must be acyclic
  ([identifiers.md](../concepts/identifiers.md)).
- **Wrong serialization mix.** Don't embed RuleML's "relaxed" form; match the
  parent (compact-in-compact). CURIEs are disallowed in Basic Dialect.
- **Hard-coding the threshold for the wrong year.** kr 5 000 only applies from
  inntektsår 2023; using it for a 2022 case is a substantive error.
- **Modelling the conclusion as `Obligation`.** A tax *deduction* is a benefit
  (Right/Permission), not a duty on the taxpayer.
- **One mega-Atom for all vilkår.** Loses isomorphism and the per-vilkår facts.
- **Predicate names copied from prose.** Encoding a voice, negation, date, or
  incidental qualifier in the relation name creates false vocabulary splits.
  Reconcile truth conditions across the full decision; decompose material
  qualifiers into separate Atoms and preserve wording in relation-manifest
  evidence.
- **Forgetting Authority/Jurisdiction.** Reification (R6) wants provenance;
  always attach Skatteklagenemnda + Norge/skatt via an Association.
- **The lumped Association.** Several provisions and a dozen statements in one
  `<lrml:Association>` reads as *every* statement deriving from *every*
  provision — the XSD says each non-target entity pairs with every target — and
  that is what search and review consume. Split it one hjemmel per Association
  (see [P6](#p6--always-tie-a-rule-to-its-hjemmel--one-hjemmel-per-association)
  and [hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)).
- **Citing § when the text cites a ledd — or a ledd the text never cited.** Both
  break traceability: the first loses the pinpoint the vedtak gave you, the
  second invents a citation. Pinpoint exactly as deep as the text does.
- **Hanging a defining provision on the finding instead of the vilkår.** If
  § 6-44-1 andre ledd defines *nødvendig*, it belongs on the vilkår Atom in the
  rule (and on the finding), not on the finding alone — otherwise the rule still
  claims all its conditions come from § 6-44-4.
- **Confusing `Neg` and `Naf`.** Strong negation (`Neg`) asserts falsity;
  negation-as-failure (`Naf`) is "not provable". "ikke ferge i forskriftens
  forstand" is strong negation of membership, not a default.
- **Leaving the conclusion implicit.** Capturing rule + facts but not the
  operative result (granted/denied amount per year) loses the vedtak's outcome
  (see [P8](#p8--state-the-operative-conclusion-explicitly)).
- **Cosmetic threshold.** Two `Context`s for 3 300 vs 5 000 are pointless if the
  value isn't a real rule term (see [P9](#p9--year-dependent-parameter-must-be-a-real-term)).
- **Orphaned dispute.** An `Alternatives`/Context selection with no concrete fact or
  recorded denial under-models the sub-claim (see [P10](#p10--connect-a-definitional-dispute-to-its-concrete-effect)).
- **Using Override as a verdict edge.** `Override` ranks defeasible Legal Rules;
  it does not mean that one factual allegation, recommendation, or majority
  voice won. Use direct Role attribution and adjudication Context selection.
- **Dangling provenance nodes.** A declared `Agent` with no `Role` filling it via
  `filledBy` is dead metadata; every material statement also needs direct
  substantive `forExpression` attribution. Keep
  sekretariatet (innstiller) distinct from Skatteklagenemnda (vedtar) when both
  appear.
- **Broken quote anchors.** A sidecar `wasDerivedFrom` whose `generatedEntity`
  names no `@key` in the `.lrml` or whose `usedEntity` names no
  `<prov:Entity xml:id>`, or a `wasQuotedFrom` that names no declared
  `<lrml:LegalSource>`, breaks text isomorphism — `validate_lrml.py` checks all
  three (see [P11](#p11--anchor-quotes-with-prov-in-the-sidecar-never-in-the-lrml)).
- **Schema-invalid idioms that look plausible.** The XSD rejects:
  `<lrml:Prefix name=… value=…>` (use `pre`/`refID`), `@key` on a
  `LegalReference` (use `@refersTo`), bare RuleML keys (`key="t-2022"` → 
  `key=":t-2022"`), `xs:gYear` inside `<ruleml:Time>` (use `xs:date`),
  `<lrml:hasTime>` (use `atTime`), `appliesTemporal`/`appliesRole`/`appliesAgent`
  (don't exist), `<lrml:Alternative>` (use `hasAlternative`),
  `<lrml:Bearer>` wrapping its term (use a `ruleml:slot`), a bare Atom in a
  `FactualStatement` (wrap in `hasTemplate`), any PROV markup in the `.lrml`
  (sidecar). When in doubt, run the validator.

## See also

- [vedtak-to-legalruleml.md](vedtak-to-legalruleml.md) ·
  [worked-example.md](worked-example.md) ·
  [../reference/element-cheatsheet.md](../reference/element-cheatsheet.md)
