# Worked example — `vedtak_frodo_ferge` → LegalRuleML

A full run of the [playbook](vedtak-to-legalruleml.md) on
[`samples/in/frodo/vedtak_frodo_ferge.md`](../../../samples/in/frodo/vedtak_frodo_ferge.md)
(case SK-2022-0117). The case: Frodo Lommelun claims a reisefradrag for ferry
costs under **FSFIN § 6-44-4** for inntektsår **2022**; the secretariat grants
kr 6 240 but **rejects** the sub-claim that crossing in his own rowboat counts as
"ferge". The XML below validates against the vendored OASIS schema
(`python3 legalruleml/bin/validate_lrml.py …`).

## 1. The legal reasoning, in prose

- **Rule (FSFIN § 6-44-4):** a reisefradrag for ferge/bom is granted *if*
  (i) costs exceed the **terskelbeløp** (kr 3 300 for 2022),
  (ii) own car is necessary per the **reisetidsregel**,
  (iii) costs are **documented** by receipt, and
  (iv) the **cheapest ticket** option is used.
- **Facts:** all four vilkår are found satisfied (kr 6 240 > kr 3 300; >2 h/day
  saved; receipts from Bukkelandsferja AS; årskort = cheapest).
- **Definitional dispute:** does crossing in *egen robåt* count as "ferge"? The
  secretariat says **no** (rowing is not a "kostnad til ferge i forskriftens
  forstand"). → a `ConstitutiveStatement` defining ferge, with the taxpayer's
  broader reading as the losing alternative, resolved by an `Override`.
- **Conclusion:** Frodo is granted (Right) a fradrag of kr 6 240; the kr 900
  rowboat amount is denied.

## 2. The mapping at a glance

| Vedtak element | LegalRuleML |
|---|---|
| FSFIN § 6-44-4 | `LegalReference` (`refersTo="ref-fsfin-6-44-4"`) + `LegalSource` |
| the deduction rule | `PrescriptiveStatement ps-fradrag` → `Rule` (4 vilkår in `if`) |
| "innrømmes fradrag" | `then` = `Right`, slot `Bearer` = Frodo |
| 4× "Vilkåret … oppfylt" | `FactualStatement` fs-terskel / fs-reisetid / fs-dok / fs-rimeligst |
| "ferge i forskriftens forstand" | `ConstitutiveStatement cs-ferge-sekr` (narrow) |
| taxpayer's robåt reading | `ConstitutiveStatement cs-ferge-skattyter` (broad), losing alternative |
| board adopts narrow reading | `OverrideStatement ov-ferge` (`over` sekr, `under` skattyter) |
| robåt-kryssing is not ferge, denied | `fs-robaat` (Neg) + `fs-konkl-robaat` (Neg) |
| operative grant kr 6 240 | `ps-konkl-2022` (empty-body Rule, `Right` head) |
| inntektsår 2022 / kr 3 300 | `Time :t-2022` + `TemporalCharacteristic tc-2022` + `Context ctx-2022` |
| Skatteklagenemnda / sekretariatet | `Authority auth-skl` |
| Norge / skatt | `Jurisdiction jur-no-skatt` |
| each justifying passage | quote in the `.prov.xml` sidecar (§4 below) |

## 3. The LegalRuleML file (compact serialization)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lrml:LegalRuleML
    xmlns="https://example.org/ratatouille/onto#"
    xmlns:lrml="http://docs.oasis-open.org/legalruleml/ns/v1.0/"
    xmlns:ruleml="http://ruleml.org/spec"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    hasCreationDate="#t-vedtak">

  <!-- ── Prefixes (default xmlns above = the domain ontology) ── -->
  <lrml:Prefix pre="fsfin" refID="https://lovdata.no/forskrift/1999-11-19-1158/"/>
  <lrml:Prefix pre="lrmlv" refID="http://docs.oasis-open.org/legalruleml/ns/v1.0/vocab#"/>

  <!-- ── Metadata: legal sources / references ───────────────── -->
  <lrml:LegalReferences>
    <lrml:LegalReference refersTo="ref-fsfin-6-44-4"
        refID="FSFIN § 6-44-4"
        refIDSystemName="rettsinformasjon-aliaser"/>
  </lrml:LegalReferences>
  <lrml:LegalSources>
    <!-- Exact Rettsregister ID resolved through Rettsrev. -->
    <lrml:LegalSource key="src-fsfin-6-44-4"
      sameAs="forskrift-1999-11-19-1158/section:6-44-4"/>
    <lrml:LegalSource key="src-vedtak-sk-2022-0117"
        sameAs="urn:skatteklagenemnda:SK-2022-0117"/>
  </lrml:LegalSources>

  <!-- ── Metadata: provenance & jurisdiction ────────────────── -->
  <lrml:Authorities>
    <lrml:Authority key="auth-skl"
        sameAs="https://www.skatteetaten.no/skatteklagenemnda"/>
  </lrml:Authorities>
  <lrml:Jurisdictions>
    <lrml:Jurisdiction key="jur-no-skatt" sameAs="https://publications.europa.eu/resource/authority/country/NOR"/>
  </lrml:Jurisdictions>
  <lrml:Agents>
    <lrml:Agent key="agent-modell"/>
  </lrml:Agents>
  <lrml:Roles>
    <!-- Roles wire agents to expressions via filledBy/forExpression -->
    <lrml:Role key="role-author" iri="https://example.org/roles#author">
      <lrml:filledBy keyref="#agent-modell"/>
      <lrml:forExpression keyref="#r-fradrag"/>
    </lrml:Role>
  </lrml:Roles>

  <!-- ── Metadata: time & temporal characteristics ──────────── -->
  <lrml:Times>
    <!-- RuleML keys are CURIEs (leading ':'); Data must be date/dateTime/duration -->
    <ruleml:Time key=":t-2022"><ruleml:Data xsi:type="xs:date">2022-01-01</ruleml:Data></ruleml:Time>
    <ruleml:Time key=":t-vedtak"><ruleml:Data xsi:type="xs:date">2023-03-15</ruleml:Data></ruleml:Time>
  </lrml:Times>
  <lrml:TemporalCharacteristics>
    <!-- FSFIN § 6-44-4 in the version applicable to inntektsår 2022
         (terskelbeløp kr 3 300; pre-2023 endringsforskrift) -->
    <lrml:TemporalCharacteristic key="tc-2022">
      <lrml:forStatus iri="http://docs.oasis-open.org/legalruleml/ns/v1.0/vocab#Applicable"/>
      <lrml:atTime keyref="#t-2022"/>
    </lrml:TemporalCharacteristic>
  </lrml:TemporalCharacteristics>

  <!-- ── Associations ────────────────────────────────────────
       One hjemmel per Association, keyed, targeting only the fragments
       actually read out of that provision — an Association pairs every
       source with every target, so a lumped one asserts links that were
       never made (→ hjemmel-anchoring.md). -->
  <lrml:Associations>
    <lrml:Association key="assoc-fsfin-6-44-4">
      <lrml:appliesSource keyref="#ref-fsfin-6-44-4"/>
      <lrml:appliesSource keyref="#src-fsfin-6-44-4"/>
      <lrml:appliesAuthority keyref="#auth-skl"/>
      <lrml:appliesJurisdiction keyref="#jur-no-skatt"/>
      <lrml:appliesTemporalCharacteristic keyref="#tc-2022"/>
      <lrml:toTarget keyref="#ps-fradrag"/>
      <lrml:toTarget keyref="#cs-ferge-sekr"/>
    </lrml:Association>
    <!-- the vedtak itself is the source of the findings -->
    <lrml:Association key="assoc-vedtak">
      <lrml:appliesSource keyref="#src-vedtak-sk-2022-0117"/>
      <lrml:appliesAuthority keyref="#auth-skl"/>
      <lrml:toTarget keyref="#stmts"/>
    </lrml:Association>
  </lrml:Associations>

  <!-- ── Context: the 2022 reading (terskelbeløp = 3300) ─────── -->
  <lrml:Context key="ctx-2022">
    <lrml:appliesTemporalCharacteristic keyref="#tc-2022"/>
    <lrml:inScope keyref="#ps-fradrag"/>
  </lrml:Context>

  <!-- ── Alternatives: the disputed definition of "ferge" ─────── -->
  <lrml:Alternatives key="alt-ferge">
    <lrml:hasAlternative keyref="#cs-ferge-sekr"/>      <!-- adopted -->
    <lrml:hasAlternative keyref="#cs-ferge-skattyter"/> <!-- rejected -->
  </lrml:Alternatives>

  <!-- ── Statements ─────────────────────────────────────────── -->
  <lrml:Statements key="stmts">

    <!-- The deduction rule (FSFIN § 6-44-4): 4 vilkår ⇒ Right to fradrag.
         The threshold is a real rule argument (terskel), version-selected
         by ctx-2022. -->
    <lrml:PrescriptiveStatement key="ps-fradrag">
      <ruleml:Rule key=":r-fradrag" closure="universal">
        <ruleml:if>
          <ruleml:And>
            <!-- (i) kostnader > terskelbeløp -->
            <ruleml:Atom>
              <ruleml:Rel iri=":overstigerTerskelbeloep"/>
              <ruleml:Var>skattepliktig</ruleml:Var>
              <ruleml:Var>beloep</ruleml:Var>
              <ruleml:Var>terskel</ruleml:Var>
            </ruleml:Atom>
            <!-- (ii) egen bil nødvendig etter reisetidsregelen -->
            <ruleml:Atom>
              <ruleml:Rel iri=":oppfyllerReisetidsregelen"/>
              <ruleml:Var>skattepliktig</ruleml:Var>
            </ruleml:Atom>
            <!-- (iii) dokumentert med kvittering -->
            <ruleml:Atom>
              <ruleml:Rel iri=":dokumentertMedKvittering"/>
              <ruleml:Var>skattepliktig</ruleml:Var>
            </ruleml:Atom>
            <!-- (iv) rimeligste billettalternativ -->
            <ruleml:Atom>
              <ruleml:Rel iri=":rimeligsteBillettalternativ"/>
              <ruleml:Var>skattepliktig</ruleml:Var>
            </ruleml:Atom>
          </ruleml:And>
        </ruleml:if>
        <ruleml:then>
          <lrml:Right>
            <!-- Bearer is a slot key, the party term is the slot value -->
            <ruleml:slot>
              <lrml:Bearer iri=":skattepliktig-rolle"/>
              <ruleml:Var>skattepliktig</ruleml:Var>
            </ruleml:slot>
            <ruleml:Atom>
              <ruleml:Rel iri=":harReisefradragFerge"/>
              <ruleml:Var>skattepliktig</ruleml:Var>
              <ruleml:Var>beloep</ruleml:Var>
            </ruleml:Atom>
          </lrml:Right>
        </ruleml:then>
      </ruleml:Rule>
    </lrml:PrescriptiveStatement>

    <!-- Facts: each vilkår found satisfied for Frodo Lommelun.
         FactualStatement keeps the explicit hasTemplate wrapper (not skippable). -->
    <lrml:FactualStatement key="fs-terskel">
      <lrml:hasTemplate>
        <ruleml:Atom>
          <ruleml:Rel iri=":overstigerTerskelbeloep"/>
          <ruleml:Ind iri=":frodo">Frodo Lommelun</ruleml:Ind>
          <ruleml:Data xsi:type="xs:decimal">6240</ruleml:Data>
          <ruleml:Data xsi:type="xs:decimal">3300</ruleml:Data>
        </ruleml:Atom>
      </lrml:hasTemplate>
    </lrml:FactualStatement>
    <lrml:FactualStatement key="fs-reisetid">
      <lrml:hasTemplate>
        <ruleml:Atom><ruleml:Rel iri=":oppfyllerReisetidsregelen"/><ruleml:Ind iri=":frodo"/></ruleml:Atom>
      </lrml:hasTemplate>
    </lrml:FactualStatement>
    <lrml:FactualStatement key="fs-dok">
      <lrml:hasTemplate>
        <ruleml:Atom><ruleml:Rel iri=":dokumentertMedKvittering"/><ruleml:Ind iri=":frodo"/></ruleml:Atom>
      </lrml:hasTemplate>
    </lrml:FactualStatement>
    <lrml:FactualStatement key="fs-rimeligst">
      <lrml:hasTemplate>
        <ruleml:Atom><ruleml:Rel iri=":rimeligsteBillettalternativ"/><ruleml:Ind iri=":frodo"/></ruleml:Atom>
      </lrml:hasTemplate>
    </lrml:FactualStatement>

    <!-- Definitional dispute: what counts as "ferge"? -->
    <!-- Adopted (secretariat): rowboat crossing is NOT ferge -->
    <lrml:ConstitutiveStatement key="cs-ferge-sekr">
      <ruleml:Rule key=":r-ferge-sekr" closure="universal">
        <ruleml:if>
          <ruleml:And>
            <ruleml:Atom><ruleml:Rel iri=":overfartMed"/><ruleml:Var>reise</ruleml:Var><ruleml:Var>fartoey</ruleml:Var></ruleml:Atom>
            <ruleml:Atom><ruleml:Rel iri=":ervervsmessigFergetjeneste"/><ruleml:Var>fartoey</ruleml:Var></ruleml:Atom>
          </ruleml:And>
        </ruleml:if>
        <ruleml:then>
          <ruleml:Atom><ruleml:Rel iri=":erFergekostnad"/><ruleml:Var>reise</ruleml:Var></ruleml:Atom>
        </ruleml:then>
      </ruleml:Rule>
    </lrml:ConstitutiveStatement>

    <!-- Rejected (taxpayer): own rowboat ALSO counts as ferge -->
    <lrml:ConstitutiveStatement key="cs-ferge-skattyter">
      <ruleml:Rule key=":r-ferge-skattyter" closure="universal">
        <ruleml:if>
          <ruleml:Atom><ruleml:Rel iri=":overfartMedEgenRobaat"/><ruleml:Var>reise</ruleml:Var></ruleml:Atom>
        </ruleml:if>
        <ruleml:then>
          <ruleml:Atom><ruleml:Rel iri=":erFergekostnad"/><ruleml:Var>reise</ruleml:Var></ruleml:Atom>
        </ruleml:then>
      </ruleml:Rule>
    </lrml:ConstitutiveStatement>

    <!-- The board adopts the secretariat's narrow definition
         (lex specialis: "ferge i forskriftens forstand") -->
    <lrml:OverrideStatement key="ov-ferge">
      <lrml:Override over="#cs-ferge-sekr" under="#cs-ferge-skattyter"/>
    </lrml:OverrideStatement>

    <!-- The adopted definition applied to the concrete reise (P10) -->
    <lrml:FactualStatement key="fs-robaat">
      <lrml:hasTemplate>
        <ruleml:Neg>
          <ruleml:Atom><ruleml:Rel iri=":erFergekostnad"/><ruleml:Ind iri=":robaat-kryssing">kryssingen med egen robåt</ruleml:Ind></ruleml:Atom>
        </ruleml:Neg>
      </lrml:hasTemplate>
    </lrml:FactualStatement>

    <!-- Operative conclusion (P8): unconditional grant = empty-body rule
         with a deontic head (a Right cannot live in a FactualStatement) -->
    <lrml:PrescriptiveStatement key="ps-konkl-2022">
      <ruleml:Rule key=":r-konkl-2022">
        <ruleml:if><ruleml:And/></ruleml:if>
        <ruleml:then>
          <lrml:Right>
            <ruleml:slot>
              <lrml:Bearer iri=":skattepliktig-rolle"/>
              <ruleml:Ind iri=":frodo">Frodo Lommelun</ruleml:Ind>
            </ruleml:slot>
            <ruleml:Atom>
              <ruleml:Rel iri=":innroemmesFergefradrag"/>
              <ruleml:Ind iri=":frodo"/>
              <ruleml:Data xsi:type="xs:decimal">6240</ruleml:Data>
            </ruleml:Atom>
          </lrml:Right>
        </ruleml:then>
      </ruleml:Rule>
    </lrml:PrescriptiveStatement>

    <!-- The denied sub-claim, stated explicitly -->
    <lrml:FactualStatement key="fs-konkl-robaat">
      <lrml:hasTemplate>
        <ruleml:Neg>
          <ruleml:Atom><ruleml:Rel iri=":innroemmesFergefradragForReise"/><ruleml:Ind iri=":frodo"/><ruleml:Ind iri=":robaat-kryssing"/></ruleml:Atom>
        </ruleml:Neg>
      </lrml:hasTemplate>
    </lrml:FactualStatement>

  </lrml:Statements>
</lrml:LegalRuleML>
```

## 4. The PROV sidecar (`vedtak_frodo_ferge.prov.xml`)

Text isomorphism lives in a sibling file so the `.lrml` stays schema-pure
(→ [sources-isomorphism §vedtak-quotes](../concepts/sources-isomorphism.md#vedtak-quotes)).
Three quotes shown; a real run anchors every statement:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prov:Bundle xml:id="prov-text-anchors"
    xmlns:prov="http://www.w3.org/ns/prov#">

  <!-- the statutory wording, as the vedtak reproduces it: both edges -->
  <prov:Entity xml:id="quote-hjemmel-fsfin-6-44-4">
    <prov:value>Etter FSFIN § 6-44-4 gis fradrag for kostnader til ferge og bom
      ved arbeidsreise dersom kostnadene overstiger kr 3 300 i året, bruk av egen
      bil er nødvendig etter reisetidsregelen, kostnadene dokumenteres med
      kvittering, og rimeligste billettalternativ legges til grunn.</prov:value>
    <prov:wasQuotedFrom prov:resource="#src-fsfin-6-44-4"/>
    <prov:wasQuotedFrom prov:resource="#src-vedtak-sk-2022-0117"/>
  </prov:Entity>

  <prov:Entity xml:id="quote-fs-terskel">
    <prov:value>Dokumenterte fergekostnader utgjør kr 6 240 og overstiger
      terskelbeløpet på kr 3 300. Vilkåret om terskelbeløp er oppfylt.</prov:value>
    <prov:wasQuotedFrom prov:resource="#src-vedtak-sk-2022-0117"/>
  </prov:Entity>

  <prov:Entity xml:id="quote-ov-ferge">
    <prov:value>Roing med egen robåt er ingen kostnad til ferge i forskriftens
      forstand; sekretariatets forståelse legges til grunn.</prov:value>
    <prov:wasQuotedFrom prov:resource="#src-vedtak-sk-2022-0117"/>
  </prov:Entity>

  <prov:wasDerivedFrom prov:generatedEntity="vedtak_frodo_ferge.lrml#r-fradrag"
                       prov:usedEntity="#quote-hjemmel-fsfin-6-44-4"/>
  <prov:wasDerivedFrom prov:generatedEntity="vedtak_frodo_ferge.lrml#fs-terskel"
                       prov:usedEntity="#quote-fs-terskel"/>
  <prov:wasDerivedFrom prov:generatedEntity="vedtak_frodo_ferge.lrml#ov-ferge"
                       prov:usedEntity="#quote-ov-ferge"/>
</prov:Bundle>
```

## 5. Notes on the modelling choices

- **Why `Right` (not `Obligation`) for the conclusion** — the entitlement
  "innrømmes fradrag" is a benefit the skattepliktige may claim; modelled as a
  directed [`<lrml:Right>`](../concepts/deontic.md) with slot `Bearer` = Frodo.
- **Why the operative grant is a `PrescriptiveStatement` with an empty body** —
  a deontic operator may not appear in a `FactualStatement`; an unconditional
  deontic conclusion is a rule with `<ruleml:if><ruleml:And/></ruleml:if>`
  (the "deontic instance" pattern from the spec's ex3).
- **Why the robåt sub-issue keeps both readings** — both readings are part of
  the *argumentation*; preserving the rejected one and selecting the adopted
  legal rendering in Context is exactly what
  [requirement R5/R3](../concepts/overview.md) asks for. See
  [alternatives.md](../concepts/alternatives.md) and
  [voices-and-attribution.md](../concepts/voices-and-attribution.md). The sample
  XML predates this profile and its generic winner/loser Override must be
  migrated before it is used as the voice-attribution template.
- **Why kr 3 300 (not kr 5 000)** — the case is inntektsår 2022, before the
  endringsforskrift; the version is selected by `ctx-2022` +
  [`tc-2022`](../concepts/temporal.md), using `rettsinformasjon.json`'s
  `fsfin_6_44@2000-01-01` version (`terskelbeloep` kr 3 300).
- **Why `@refID="FSFIN § 6-44-4"`** — taken verbatim from the
  `rettsinformasjon.json` `aliaser`; `@refersTo="ref-fsfin-6-44-4"` is the
  reference's own internal id, which the Association's
  `appliesSource keyref="#ref-fsfin-6-44-4"` resolves to
  ([isomorphism](../concepts/sources-isomorphism.md)).
- **Why the pinpoint stops at `§ 6-44-4`, without a ledd** — the vedtak cites
  the provision as a whole ("Etter FSFIN § 6-44-4 gis fradrag …"). Guessing
  which ledd each of the four vilkår sits in would fabricate a citation. Where
  a vedtak *does* cite deeper — `samples/out/vedtak_kort_FSFIN_6_44_4.lrml`
  cites `FSFIN § 6-44-1, 2 ledd` for the nødvendighet vilkår — that vilkår's
  `<ruleml:Atom>` gets its own `@key` and its own Association
  ([hjemmel-anchoring.md](../concepts/hjemmel-anchoring.md)).
- The relation IRIs (`:overstigerTerskelbeloep`, `:erFergekostnad`, …) are
  bare-colon CURIEs resolved against the **default `xmlns`** on the root (the
  domain-ontology namespace, cf. the `*.tonto` files).

## See also

- [vedtak-to-legalruleml.md](vedtak-to-legalruleml.md) — the playbook this follows.
- [patterns-and-pitfalls.md](patterns-and-pitfalls.md) — generalised guidance.
- [vedtak-anatomy.md](vedtak-anatomy.md) — the vedtak structure.
