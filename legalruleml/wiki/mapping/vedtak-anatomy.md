# Anatomy of a Skatteklagenemnda vedtak

A *vedtak* (decision) from the **Skatteklagenemnda** (Norwegian Tax Appeals
Board) follows a stable structure. Knowing which section yields which
LegalRuleML construct is half the mapping job. The reference sample is
[`samples/in/frodo/vedtak_frodo_ferge.md`](../../../samples/in/frodo/vedtak_frodo_ferge.md).

## Sections and what they yield

| Vedtak section (Norwegian) | Contains | Maps to |
|---|---|---|
| **Header** ("Skatteklagenemndas vedtak i sak SK-…") | case id, the deciding body, date | `@hasCreationDate`, [`Authority`](../concepts/metadata.md), case `@key` |
| **Saksforholdet** (the facts) | who, what, the inntektsår, amounts | [`FactualStatement`](../concepts/statements.md)s; `Ind`/`Data` terms; the inntektsår → [temporal](../concepts/temporal.md) |
| **Skattepliktiges anførsler** (taxpayer's submissions) | the taxpayer's claims & disputed points | directly attributed facts/legal readings; only competing legal renderings become [`Alternatives`](../concepts/alternatives.md) |
| **Sekretariatets vurderinger** (the secretariat's assessment) | the rule, its **vilkår**, and whether each is met | directly attributed [`PrescriptiveStatement`](../concepts/statements.md)/[`ConstitutiveStatement`](../concepts/statements.md) rules + one `FactualStatement` per finding; recommendation status via Role |
| **Konklusjon** (the conclusion) | the entitlement granted/denied | the head/result: a [`Right`/`Permission`](../concepts/deontic.md) for the skattepliktige |
| **Dissens** (if split: flertall/mindretall) | majority vs minority reasoning | direct `decider`/`dissenter` Role attribution; `Alternatives` only for alternative legal renderings |

## The legal-source companions

- **`*.config.json`** — lists the `rettsgrunnlag`/`tonto` used and an
  `instansiering_hint` naming the rettssubjekt (skattepliktige) and pliktsubjekt
  (skattemyndigheten). Use it to pick the right hjemmel and parties.
- **`rettsinformasjon.json`** — for each cited provision: the `hjemmel_id`
  (→ `@refersTo`), the `aliaser` (→ `@refID`/`@refIDSystemName`), and the
  **versjoner** with `ikrafttredelse`/`opphevet` dates and per-version
  **parametre** (e.g. `terskelbeloep` kr 3 300 vs kr 5 000) → drives
  [temporal versioning](../concepts/temporal.md).

## Recognizing vilkår

The assessment states each vilkår then declares it met:
*"Vilkåret om **terskelbeløp** er etter dette oppfylt."* The phrase pattern is
`Vilkåret om X er … oppfylt`. Each such sentence is **two** things at once:

1. a **condition Atom** in the rule body (the *if*), and
2. a **FactualStatement** asserting that, for this taxpayer, the condition holds.

For `vedtak_frodo_ferge` the four vilkår of FSFIN § 6-44-4 are: terskelbeløp
(> kr 3 300), reisetidsregelen (egen bil nødvendig), dokumentasjon (kvittering),
and rimeligste billettalternativ.

## See also

- [vedtak-to-legalruleml.md](vedtak-to-legalruleml.md) — the step-by-step playbook.
- [worked-example.md](worked-example.md) — this sample fully mapped.
