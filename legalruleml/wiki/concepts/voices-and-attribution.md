# Voices and attribution

A vedtak contains several speakers whose statements must remain distinguishable:
the taxpayer, the first-instance tax office, the secretariat, the deciding board,
and sometimes a dissenting member. LegalRuleML represents responsibility for an
expression through a Role. *(Core §4.3.2, §5.9)*

## Three independent relations

Do not collapse the different things loosely called “attribution”. The
repository voice ledger records three independent, document-level relations:

- **`asserted_by`** — the voice to which the proposition is substantively
  attributed, whether stated in its own words or relayed by another narrator;
- **`reported_by`** — the document voice narrating, quoting, or paraphrasing
  that proposition; and
- **`endorsed_by`** — a later voice that expressly adopts the proposition.

One proposition can therefore be asserted by the tax office, reported by the
secretariat, and endorsed by the board. None of those edges entails either of
the others. In particular, quotation or paraphrase does not make the narrator
responsible for the proposition, and document inclusion does not establish
endorsement. See the concrete JSON shape and evidence rules in the
[voice-first profile](../mapping/voice-first-profile.md).

## LegalRuleML core pattern

The OASIS relation is direct:

```text
Agent <- filledBy - Role - forExpression -> keyed expression
```

```xml
<lrml:Agents>
  <lrml:Agent key="agent-skattepliktig"/>
  <lrml:Agent key="agent-nemnda"/>
</lrml:Agents>
<lrml:Roles>
  <lrml:Role key="role-claimant" iri="https://example.org/roles#claimant">
    <lrml:filledBy keyref="#agent-skattepliktig"/>
    <lrml:forExpression keyref="#fs-paastand"/>
  </lrml:Role>
  <lrml:Role key="role-decider" iri="https://example.org/roles#decider">
    <lrml:filledBy keyref="#agent-nemnda"/>
    <lrml:forExpression keyref="#fs-konklusjon"/>
  </lrml:Role>
</lrml:Roles>
```

`forExpression` targets the keyed statement, rule, or atom for which the Actor
has substantive responsibility. It does not target a Context. Repeat
`forExpression` when one voice owns several expressions. Use another
substantive Role edge only when that other voice itself asserts the expression,
not merely because it reports or later endorses it.

LegalRuleML Core has no direct equivalent of this repository's narration and
endorsement edges. During projection, use `Role.forExpression` for
`asserted_by`; preserve `reported_by`, `endorsed_by`, and their evidence in the
voice ledger alongside the formal artifacts. Do not manufacture extra Roles to
make narration or endorsement look like direct assertion. A later voice's own
new proposition (“the board adopts the recommendation”) may independently be a
keyed expression with its own Role, but that does not change ownership of the
recommendation being adopted.

`Authority` is different: it records the institutional authority applicable to
statements through `Association.appliesAuthority`. It does not say who advanced
a particular claim.

## Argument inventory

Before writing XML, make a row for every material contribution:

| Actor | Procedural role | Expression | Status in document |
|---|---|---|---|
| skattepliktig | `claimant` | claim/fact/legal reading | alleged |
| skattekontor | `first-instance-decider` | original finding/result | earlier decision |
| sekretariat | `recommender` | assessment/recommendation | proposed |
| nemnd | `decider` | adopted reasoning/result | final |
| mindretall | `dissenter` | dissenting reading/result | dissent |

Recommended role IRI fragments are `claimant`, `first-instance-decider`,
`recommender`, `decider`, and `dissenter`. These names are this repository's
application profile, not a controlled OASIS vocabulary. Their stable identifiers,
Norwegian labels and recognition cues, search and operative semantics, direct
attribution requirement, and search-time parent grouping live in the versioned
[`v1.0` voice profile](../../application-profiles/voices/v1.0.json), rather than
in validator code. A document may stop at a recommendation or record only
dissent; do not invent a `decider` Role.

Actors are always document-local: give each person or institution a local
`Agent`/`Figure` key and connect it with `filledBy`. A project needing another
procedural role should copy or extend the versioned profile, supply all role
metadata, and validate with `--voice-profile FILE`. Merely using an unfamiliar
IRI does not opt out of checks: every Role still receives structural validation,
and `unknownRoleSeverity` in the selected profile makes an unknown identifier a
warning or an error.

The model-author Role is provenance about the generated XML, not a procedural
voice. Use `author` or `model-author`, and do not count it as support for the
vedtak's material statements.

## Adoption and rejection

Attribution says who is responsible for an expression. Adoption is a separate
relation. This repository represents an adjudicative selection with a Context:

```xml
<lrml:Context key="ctx-vedtak">
  <lrml:appliesAlternatives keyref="#alt-tolkninger"/>
  <lrml:inScope keyref="#cs-vedtatt-tolkning"/>
  <lrml:inScope keyref="#fs-konklusjon"/>
</lrml:Context>
```

OASIS defines `appliesAlternatives` and `inScope`; using this combination as the
named selection made by the decision is the repository profile. Absence from
`inScope` means only "not selected here". When the text expressly rejects a
claim, model that rejection or contrary finding as its own attributed statement.
Context selection captures the formal adjudicative result; it does not replace
the ledger's textual `endorsed_by` evidence, and endorsement alone does not
justify a Context selection when the document does not make one.

## Reading common vedtak formulations

- **“Skattepliktige anfører at …”** — the embedded proposition is
  `asserted_by` the taxpayer. The authorial voice of the passage is
  `reported_by`; anchor the reporting clause as `explicit_reporting_clause`.
- **The secretariat summarizes the tax office** — the tax office remains the
  asserting voice and the secretariat is the reporting voice. A heading and a
  clause such as “Skattekontoret la til grunn” may supply separate
  `section_heading` and `explicit_reporting_clause` evidence spans.
- **“Nemnda sluttet seg til sekretariatets innstilling”** — the recommendation
  remains asserted by the secretariat and is expressly `endorsed_by` the board;
  the board may also be the reporting voice for the recounted recommendation.
  The board is not retroactively its direct asserter.
- **Majority and minority opinions** — assign separate majority and minority
  voices. Attribute each proposition to the relevant voice using the opinion
  heading as evidence. Do not infer endorsement by the full board, and use
  `Alternatives` only for genuinely incompatible legal renderings.
- **Unattributed background narration** — use a stable document-narrator voice,
  supported by `document_structure`, or an `inferred` basis with lower
  confidence. Do not guess that the board or secretariat substantively asserted
  it merely from the document's institutional provenance.

## Choose the conflict construct

- Competing factual allegations remain separate attributed
  `FactualStatement`s. Do not put them in `Alternatives`, and do not rank them
  with `Override`.
- Mutually exclusive legal renderings may be grouped in `Alternatives`. The
  adjudication Context scopes the adopted rendering while preserving the other.
- Use `Override` only when the document actually states a superiority relation
  between defeasible Legal Rules, such as lex specialis. Its `over` and `under`
  endpoints are Prescriptive or Constitutive statements, not facts.
- Majority and dissent are voices first. Use `Alternatives` only when they emit
  genuinely alternative legal renderings; selection belongs in Context unless
  the text separately establishes rule priority.

## Repository profile and validation

The direct Role relation is part of LegalRuleML Core. The repository additionally
requires, when substantive procedural Roles are present:

- every material keyed statement has a substantive Role attribution;
- every declared Agent/Figure fills a Role;
- `Role.forExpression` does not point to Context;
- factual statements are not members of legal `Alternatives`;
- `Override` endpoints are Legal Rule statements.

Run:

```bash
python3 legalruleml/bin/validate_lrml.py --strict --relations --voices path/to/decision.lrml
```

`--voices` prints attribution and Context selection separately. Recognized
substantive Roles enable profile checks even without the flag; any unknown Role
also enables them so that it cannot silently become non-substantive. Select a
compatible versioned or extended profile with `--voice-profile FILE`.

## See also

- [metadata.md](metadata.md) - Agent, Role, Authority, and Jurisdiction.
- [context-associations.md](context-associations.md) - Context selection.
- [alternatives.md](alternatives.md) - competing legal renderings.
- [defeasibility.md](defeasibility.md) - genuine Legal Rule priority.
