# Voices and attribution

A vedtak contains several speakers whose statements must remain distinguishable:
the taxpayer, the first-instance tax office, the secretariat, the deciding board,
and sometimes a dissenting member. LegalRuleML represents responsibility for an
expression through a Role. *(Core §4.3.2, §5.9)*

## Core pattern

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
is responsible. It does not target a Context. Repeat `forExpression` when one
voice owns several expressions; repeat the edge from another Role when two
voices endorse the same expression.

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
application profile, not a controlled OASIS vocabulary. A document may stop at
a recommendation or record only dissent; do not invent a `decider` Role.

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
substantive Roles enable profile checks even without the flag.

## See also

- [metadata.md](metadata.md) - Agent, Role, Authority, and Jurisdiction.
- [context-associations.md](context-associations.md) - Context selection.
- [alternatives.md](alternatives.md) - competing legal renderings.
- [defeasibility.md](defeasibility.md) - genuine Legal Rule priority.
