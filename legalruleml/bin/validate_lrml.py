#!/usr/bin/env python3
"""Validate a LegalRuleML file (and its optional PROV sidecar).

Usage: python3 legalruleml/bin/validate_lrml.py [--strict] [--hjemmel] [--voices] [--relations] <name>.lrml

Checks:
  1. XSD validity against the vendored OASIS compact schema
     (legalruleml/xsd-schema/compact/lrml-compact.xsd, via xmllint).
  2. No PROV markup inside the .lrml itself (quotes live in the
     <name>.prov.xml sidecar).
  3. @key uniqueness (leading ':' stripped, per spec §7) and resolution of
     every local reference (@keyref, @over, @under, @hasCreationDate).
  4. Acyclicity of the @key/@keyref graph (spec §5.12).
  5. Every <ruleml:Rule> has <ruleml:if> and <ruleml:then> (unless it extends
     another rule via @keyref).
  6. Sidecar <name>.prov.xml, when present: every prov:wasQuotedFrom resolves
     to a LegalSource/Source key in the .lrml, and every prov:wasDerivedFrom
     links an existing .lrml key to an existing quote entity.
  7. Hjemmel anchoring (concepts/hjemmel-anchoring.md): every appliesSource
     names a source/reference; an Association carries at most one hjemmel;
     every rule statement and every keyed rule fragment is the direct target
     of a hjemmel Association.
  8. Voice attribution profile (concepts/voices-and-attribution.md): substantive
      Roles connect Actors directly to expressions; Context separately selects
      Statements; Alternatives contain legal renderings, and Override endpoints
      are Legal Rules rather than facts.
  9. Optional document-local relation manifest (<name>.relations.json): exact
      relation coverage, stable signatures, keyed usages, procedural voices,
      source-form evidence, and LRML hash freshness.
 10. Sibling source manifest and voice ledger: source digest, canonical
     character spans, non-overlap, verbatim quotes, and PROV value equality.

Options:
    --strict    treat the hjemmel and voice-profile warnings (7-8) as errors.
  --hjemmel   print the traceability table (fragment → citation → URN → quote).
    --voices    enable the voice profile and print actor/role/expression and
                            Context-selection traceability. The profile is also enabled when
                            a recognized substantive procedural Role occurs in the file.
    --relations require and validate the relation manifest, then print its
                canonical relation/signature/usage table.

Exit code 0 = all checks pass, 1 = at least one error.
"""

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path

from validate_source_bundle import validate_source_bundle

LRML = "http://docs.oasis-open.org/legalruleml/ns/v1.0/"
RULEML = "http://ruleml.org/spec"
PROV = "http://www.w3.org/ns/prov#"
XML = "http://www.w3.org/XML/1998/namespace"

SCHEMA = (
    Path(__file__).resolve().parent.parent
    / "xsd-schema"
    / "compact"
    / "lrml-compact.xsd"
)

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def strip_key(value: str) -> str:
    """RuleML keys may be CURIEs like ':t-2022'; the empty-prefix colon is
    stripped for uniqueness/reference purposes (spec §7)."""
    return value[1:] if value.startswith(":") else value


def local_ref(value: str) -> str | None:
    """Return the key a local reference ('#foo') points at, else None."""
    return value[1:] if value.startswith("#") else None


def validate_xsd(path: Path) -> None:
    result = subprocess.run(
        ["xmllint", "--nonet", "--noout", "--schema", str(SCHEMA), str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        for line in (result.stderr or result.stdout).strip().splitlines():
            err(f"XSD: {line}")


def collect_keys(root: ET.Element) -> dict[str, ET.Element]:
    keys: dict[str, ET.Element] = {}
    for el in root.iter():
        key = el.get("key")
        if key is not None:
            k = strip_key(key)
            if k in keys:
                err(f"duplicate @key '{k}'")
            keys[k] = el
        # LegalReference/Reference declare their internal id via @refersTo
        if el.tag in (f"{{{LRML}}}LegalReference", f"{{{LRML}}}Reference"):
            rid = el.get("refersTo")
            if rid is not None:
                if rid in keys:
                    err(f"duplicate id '{rid}' (LegalReference @refersTo collides)")
                keys[rid] = el
    return keys


def check_refs(root: ET.Element, keys: dict[str, ET.Element]) -> None:
    ref_attrs = ("keyref", "over", "under", "hasCreationDate")
    for el in root.iter():
        for attr in ref_attrs:
            val = el.get(attr)
            if val is None:
                continue
            target = local_ref(val)
            if target is None:
                # non-local (e.g. an external IRI in keyref) — leave to XSD
                continue
            if strip_key(target) not in keys:
                err(f"@{attr}='{val}' does not resolve to any @key/@refersTo")


def check_acyclic(root: ET.Element, keys: dict[str, ET.Element]) -> None:
    # edge K -> T when the element keyed K contains a reference to key T
    edges: dict[str, set[str]] = {}

    def refs_in(el: ET.Element) -> set[str]:
        out = set()
        for sub in el.iter():
            for attr in ("keyref", "over", "under"):
                val = sub.get(attr)
                if val:
                    t = local_ref(val)
                    if t:
                        out.add(strip_key(t))
        return out

    for k, el in keys.items():
        edges[k] = refs_in(el) & keys.keys()

    WHITE, GREY, BLACK = 0, 1, 2
    state = dict.fromkeys(edges, WHITE)

    def dfs(node: str, path: list[str]) -> None:
        state[node] = GREY
        for nxt in edges.get(node, ()):
            if state.get(nxt) == GREY:
                err(f"@key/@keyref cycle: {' -> '.join(path + [node, nxt])}")
            elif state.get(nxt) == WHITE:
                dfs(nxt, path + [node])
        state[node] = BLACK

    for node in edges:
        if state[node] == WHITE:
            dfs(node, [])


def check_rules(root: ET.Element) -> None:
    for rule in root.iter(f"{{{RULEML}}}Rule"):
        has_if = rule.find(f"{{{RULEML}}}if") is not None
        has_then = rule.find(f"{{{RULEML}}}then") is not None
        if rule.get("keyref"):
            continue  # extends another rule; partial content is fine
        if not (has_if and has_then):
            err(
                f"<ruleml:Rule key='{rule.get('key')}'> lacks "
                f"{'if' if not has_if else ''}{'/' if not (has_if or has_then) else ''}"
                f"{'then' if not has_then else ''} (not skippable, spec §5.19.6)"
            )


SOURCE_TAGS = (f"{{{LRML}}}LegalSource", f"{{{LRML}}}Source")
REFERENCE_TAGS = (f"{{{LRML}}}LegalReference", f"{{{LRML}}}Reference")
RULE_STATEMENT_TAGS = (
    f"{{{LRML}}}PrescriptiveStatement",
    f"{{{LRML}}}ConstitutiveStatement",
)
STATEMENT_TAGS = RULE_STATEMENT_TAGS + (
    f"{{{LRML}}}FactualStatement",
    f"{{{LRML}}}OverrideStatement",
    f"{{{LRML}}}PenaltyStatement",
    f"{{{LRML}}}ReparationStatement",
)
ACTOR_TAGS = (f"{{{LRML}}}Agent", f"{{{LRML}}}Figure")
SUBSTANTIVE_ROLE_NAMES = {
    "claimant",
    "first-instance-decider",
    "recommender",
    "decider",
    "dissenter",
}
AUTHOR_ROLE_NAMES = {"author", "model-author"}
ROLE_EXPRESSION_TAGS = STATEMENT_TAGS + (
    f"{{{RULEML}}}Rule",
    f"{{{RULEML}}}Atom",
)


def iri_name(value: str) -> str:
    """Return the final fragment/path component of an IRI."""
    return value.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _child_refs(element: ET.Element, local_name: str) -> tuple[str, ...]:
    return tuple(
        strip_key(ref)
        for child in element.findall(f"{{{LRML}}}{local_name}")
        if (ref := local_ref(child.get("keyref") or "")) is not None
    )


class VoiceRole:
    """One Role and its direct Actor/expression edges (Core §4.3.2)."""

    def __init__(self, element: ET.Element) -> None:
        self.element = element
        self.key = strip_key(element.get("key") or "(unkeyed)")
        self.iri = element.get("iri") or ""
        key_name = self.key.removeprefix("role-")
        known_names = SUBSTANTIVE_ROLE_NAMES | AUTHOR_ROLE_NAMES
        self.name = (
            iri_name(self.iri)
            if self.iri
            else (key_name if key_name in known_names else "")
        )
        self.actors = list(_child_refs(element, "filledBy"))
        self.expressions = list(_child_refs(element, "forExpression"))

    @property
    def substantive(self) -> bool:
        return self.name in SUBSTANTIVE_ROLE_NAMES

    @property
    def author(self) -> bool:
        return self.name in AUTHOR_ROLE_NAMES or self.key == "role-author"


def collect_voice_roles(root: ET.Element) -> list[VoiceRole]:
    return [VoiceRole(element) for element in root.iter(f"{{{LRML}}}Role")]


def _statement_ancestor_key(
    key: str, keys: dict[str, ET.Element], parents: dict[ET.Element, ET.Element]
) -> str | None:
    element = keys.get(key)
    while element is not None:
        if element.tag in STATEMENT_TAGS:
            statement_key = element.get("key")
            return strip_key(statement_key) if statement_key else None
        element = parents.get(element)
    return None


def check_voices(
    root: ET.Element,
    keys: dict[str, ET.Element],
    roles: list[VoiceRole],
    strict: bool,
) -> None:
    """Validate this repository's spec-informed voice attribution profile."""
    report = err if strict else warn
    parents = {child: parent for parent in root.iter() for child in parent}
    substantive_roles = [role for role in roles if role.substantive]

    for role in roles:
        if role.substantive and not role.iri:
            report(f"Role '{role.key}' has no @iri identifying its function")
        for actor_key in role.actors:
            actor = keys.get(actor_key)
            if actor is not None and actor.tag not in ACTOR_TAGS:
                report(
                    f"Role '{role.key}' filledBy '#{actor_key}' targets "
                    f"<{actor.tag.rsplit('}', 1)[-1]}>, not an Agent/Figure"
                )
        if role.substantive and not role.actors:
            report(f"substantive Role '{role.key}' has no filledBy Actor")
        if role.substantive and not role.expressions:
            report(f"substantive Role '{role.key}' has no forExpression target")
        for expression_key in role.expressions:
            expression = keys.get(expression_key)
            if expression is not None and expression.tag == f"{{{LRML}}}Context":
                report(
                    f"Role '{role.key}' forExpression '#{expression_key}' targets a Context; "
                    "Core §4.3.2 requires direct responsibility for an expression"
                )
            elif expression is not None and expression.tag not in ROLE_EXPRESSION_TAGS:
                report(
                    f"Role '{role.key}' forExpression '#{expression_key}' targets "
                    f"<{expression.tag.rsplit('}', 1)[-1]}>, not a keyed statement/rule/atom"
                )

    if substantive_roles:
        attributed_statements = {
            statement_key
            for role in substantive_roles
            for expression_key in role.expressions
            if (statement_key := _statement_ancestor_key(expression_key, keys, parents))
        }
        for statements in root.iter(f"{{{LRML}}}Statements"):
            for statement in statements:
                if statement.tag not in STATEMENT_TAGS or not statement.get("key"):
                    continue
                statement_key = strip_key(statement.get("key") or "")
                if statement_key not in attributed_statements:
                    report(
                        f"material statement '#{statement_key}' has no direct substantive "
                        "Role.forExpression attribution"
                    )

        used_actors = {actor for role in roles for actor in role.actors}
        for actor_tag in ACTOR_TAGS:
            for actor in root.iter(actor_tag):
                declared_actor_key = actor.get("key")
                if (
                    declared_actor_key
                    and strip_key(declared_actor_key) not in used_actors
                ):
                    report(
                        f"{actor_tag.rsplit('}', 1)[-1]} "
                        f"'#{strip_key(declared_actor_key)}' fills no Role"
                    )

    for context in root.iter(f"{{{LRML}}}Context"):
        context_key = strip_key(context.get("key") or "(unkeyed)")
        for target_key in _child_refs(context, "inScope"):
            target = keys.get(target_key)
            if target is not None and target.tag not in STATEMENT_TAGS + (
                f"{{{LRML}}}Statements",
            ):
                report(
                    f"Context '{context_key}' inScope '#{target_key}' targets "
                    f"<{target.tag.rsplit('}', 1)[-1]}>, not a Statement(s)"
                )

    for alternatives in root.iter(f"{{{LRML}}}Alternatives"):
        alternatives_key = strip_key(alternatives.get("key") or "(unkeyed)")
        for sources_key in _child_refs(alternatives, "fromLegalSources"):
            target = keys.get(sources_key)
            if target is not None and target.tag != f"{{{LRML}}}LegalSources":
                report(
                    f"Alternatives '{alternatives_key}' fromLegalSources '#{sources_key}' "
                    f"targets <{target.tag.rsplit('}', 1)[-1]}>, not a LegalSources collection"
                )
        for target_key in _child_refs(alternatives, "hasAlternative"):
            target = keys.get(target_key)
            if target is not None and target.tag == f"{{{LRML}}}FactualStatement":
                report(
                    f"Alternatives '{alternatives_key}' contains FactualStatement "
                    f"'#{target_key}'; Core §4.2.4 is for mutually exclusive legal renderings"
                )

    for override in root.iter(f"{{{LRML}}}Override"):
        for endpoint in ("over", "under"):
            override_target = local_ref(override.get(endpoint) or "")
            if override_target is None:
                continue
            override_target = strip_key(override_target)
            target = keys.get(override_target)
            if target is not None and target.tag not in RULE_STATEMENT_TAGS:
                report(
                    f"Override @{endpoint}='#{override_target}' targets "
                    f"<{target.tag.rsplit('}', 1)[-1]}>; Core §§3.4/4.2.1 require Legal Rule priority"
                )


def voices_report(
    root: ET.Element, keys: dict[str, ET.Element], roles: list[VoiceRole]
) -> None:
    print("VOICES")
    substantive = False
    for role in roles:
        if not role.substantive:
            continue
        substantive = True
        actors = ", ".join(f"#{actor}" for actor in role.actors) or "(no actor)"
        print(f"  {actors}  — {role.name} [{role.key}]")
        for expression_key in role.expressions:
            expression = keys.get(expression_key)
            kind = expression.tag.rsplit("}", 1)[-1] if expression is not None else "?"
            print(f"      → {expression_key} ({kind})")
    if not substantive:
        print("  (no substantive procedural Roles)")
    elif any(role.name == "decider" for role in roles):
        print("STATUS  operative: decider Role present")
    elif any(role.name == "recommender" for role in roles):
        print("STATUS  recommendation-only: no decider Role")
    else:
        print("STATUS  substantive voices present; no decider Role")

    print("CONTEXT SELECTIONS")
    contexts = list(root.iter(f"{{{LRML}}}Context"))
    if not contexts:
        print("  (none)")
    for context in contexts:
        context_key = strip_key(context.get("key") or "(unkeyed)")
        alternatives = _child_refs(context, "appliesAlternatives")
        scopes = _child_refs(context, "inScope")
        print(f"  {context_key}")
        for alternative in alternatives:
            print(f"      alternatives → {alternative}")
        for scope in scopes:
            print(f"      inScope → {scope}")

    print("RULE PRIORITIES")
    overrides = list(root.iter(f"{{{LRML}}}Override"))
    if not overrides:
        print("  (none)")
    for override in overrides:
        over = override.get("over") or "(missing)"
        under = override.get("under") or "(missing)"
        print(f"  {over} over {under}")


class Hjemmel:
    """One <lrml:Association>, seen as a hjemmel link.

    A hjemmel association names exactly one provision (a LegalSource and/or its
    LegalReference) and targets the fragments read out of it; see
    wiki/concepts/hjemmel-anchoring.md.
    """

    def __init__(self, element: ET.Element, label: str) -> None:
        self.element = element
        self.label = label
        self.source_keys: list[str] = []
        self.reference_keys: list[str] = []
        self.unknown_keys: list[str] = []
        self.targets: list[str] = []

    @property
    def is_hjemmel(self) -> bool:
        return bool(self.source_keys or self.reference_keys)


def collect_hjemmel(root: ET.Element, keys: dict[str, ET.Element]) -> list[Hjemmel]:
    out: list[Hjemmel] = []
    for index, assoc in enumerate(root.iter(f"{{{LRML}}}Association"), start=1):
        key = assoc.get("key")
        hjemmel = Hjemmel(
            assoc, f"key='{strip_key(key)}'" if key else f"#{index} (unkeyed)"
        )
        for child in assoc:
            ref = local_ref(child.get("keyref") or "")
            if ref is None:
                continue
            ref = strip_key(ref)
            tag = child.tag
            if tag == f"{{{LRML}}}toTarget":
                hjemmel.targets.append(ref)
            elif tag == f"{{{LRML}}}appliesSource":
                target = keys.get(ref)
                if target is None:
                    continue  # already reported by check_refs
                if target.tag in SOURCE_TAGS:
                    hjemmel.source_keys.append(ref)
                elif target.tag in REFERENCE_TAGS:
                    hjemmel.reference_keys.append(ref)
                else:
                    hjemmel.unknown_keys.append(ref)
        out.append(hjemmel)
    return out


def keyed_descendants(element: ET.Element) -> set[str]:
    """Every @key below (and on) an element, colon-stripped."""
    return {strip_key(key) for el in element.iter() if (key := el.get("key"))}


def check_hjemmel(
    root: ET.Element,
    keys: dict[str, ET.Element],
    associations: list[Hjemmel],
    strict: bool,
) -> None:
    """Hjemmel anchoring: rules must be traceable to the provision they formalize.

    An Association is a cross-product ("each non-target entity is paired with
    every target entity"), so an Association carrying several provisions claims
    every target derives from all of them. See wiki/concepts/hjemmel-anchoring.md.
    """
    report = err if strict else warn

    for hjemmel in associations:
        for ref in hjemmel.unknown_keys:
            tag = keys[ref].tag.rsplit("}", 1)[-1]
            err(
                f"Association {hjemmel.label}: appliesSource keyref='#{ref}' resolves to "
                f"<lrml:{tag}>, not a LegalSource/LegalReference"
            )
        if len(hjemmel.source_keys) > 1 or len(hjemmel.reference_keys) > 1:
            cited = ", ".join(
                f"#{k}" for k in hjemmel.source_keys + hjemmel.reference_keys
            )
            report(
                f"Association {hjemmel.label} carries more than one hjemmel ({cited}) "
                f"over {len(hjemmel.targets)} target(s) — an Association pairs every "
                f"source with every target, so split it one hjemmel per Association"
            )

    anchored: set[str] = set()
    for hjemmel in associations:
        if hjemmel.is_hjemmel:
            anchored.update(hjemmel.targets)

    for tag in RULE_STATEMENT_TAGS:
        for statement in root.iter(tag):
            key = statement.get("key")
            if key is None:
                continue
            if keyed_descendants(statement) & anchored:
                continue
            name = tag.rsplit("}", 1)[-1]
            report(
                f"<lrml:{name} key='{strip_key(key)}'> is not the direct target of any "
                f"Association naming a hjemmel — the rule is not traceable to a provision"
            )

    for atom in root.iter(f"{{{RULEML}}}Atom"):
        key = atom.get("key")
        if key is None:
            continue
        if strip_key(key) not in anchored:
            report(
                f"<ruleml:Atom key='{strip_key(key)}'> carries a key but no Association "
                f"targets it — a fragment key exists to carry its own hjemmel link"
            )


def hjemmel_report(
    path: Path,
    root: ET.Element,
    keys: dict[str, ET.Element],
    associations: list[Hjemmel],
) -> None:
    """Print the fragment → citation → URN → quote table for review."""
    quotes = sidecar_quotes(path.with_suffix(".prov.xml"))
    print(f"HJEMMEL  {path.name}")
    anchored = False
    for hjemmel in associations:
        if not hjemmel.is_hjemmel:
            continue
        anchored = True
        citation = ", ".join(
            keys[ref].get("refID") or ref for ref in hjemmel.reference_keys
        )
        print(f"  Association {hjemmel.label}{'  — ' + citation if citation else ''}")
        for src in hjemmel.source_keys:
            print(f"    {keys[src].get('sameAs') or '(no @sameAs)'}  [{src}]")
        if not hjemmel.source_keys:
            print("    (no LegalSource — the citation has no resolvable text)")
        for target in hjemmel.targets:
            element = keys.get(target)
            kind = element.tag.rsplit("}", 1)[-1] if element is not None else "?"
            print(f"      → {target} ({kind})")
            for quote in quotes.get(target, []):
                snippet = " ".join(quote.split())
                print(f"          “{snippet[:96]}{'…' if len(snippet) > 96 else ''}”")
    if not anchored:
        print("  (no Association names a hjemmel)")


def sidecar_quotes(sidecar: Path) -> dict[str, list[str]]:
    """Map each anchored fragment key to the quote texts derived onto it."""
    if not sidecar.is_file():
        return {}
    try:
        prov_root = ET.parse(sidecar).getroot()
    except ET.ParseError:
        return {}
    text_by_id: dict[str, str] = {}
    for entity in prov_root.iter(f"{{{PROV}}}Entity"):
        eid = entity.get(f"{{{XML}}}id")
        value = entity.find(f"{{{PROV}}}value")
        if eid and value is not None:
            text_by_id[eid] = "".join(value.itertext())
    out: dict[str, list[str]] = {}
    for link in prov_root.iter(f"{{{PROV}}}wasDerivedFrom"):
        generated = link.get(f"{{{PROV}}}generatedEntity") or ""
        used = local_ref(link.get(f"{{{PROV}}}usedEntity") or "")
        if "#" not in generated or used is None:
            continue
        quote = text_by_id.get(used)
        if quote:
            out.setdefault(strip_key(generated.rsplit("#", 1)[-1]), []).append(quote)
    return out


def check_no_embedded_prov(root: ET.Element) -> None:
    for el in root.iter():
        if el.tag.startswith(f"{{{PROV}}}"):
            err(
                f"embedded PROV element <{el.tag}> — quotes belong in the "
                f".prov.xml sidecar, the .lrml must stay schema-pure"
            )
            return
        for attr in el.attrib:
            if attr.startswith(f"{{{PROV}}}"):
                err(
                    f"embedded PROV attribute on <{el.tag}> — move the "
                    f"derivation link to the .prov.xml sidecar"
                )
                return


def check_sidecar(sidecar: Path, keys: dict[str, ET.Element]) -> None:
    try:
        prov_root = ET.parse(sidecar).getroot()
    except ET.ParseError as exc:
        err(f"sidecar {sidecar.name}: XML parse error: {exc}")
        return

    source_keys = {
        strip_key(key)
        for tag in ("LegalSource", "Source")
        for el in keys_iter(keys, f"{{{LRML}}}{tag}")
        if (key := el.get("key"))
    }
    quote_ids = set()
    for entity in prov_root.iter(f"{{{PROV}}}Entity"):
        eid = entity.get(f"{{{XML}}}id")
        if not eid:
            err("sidecar: <prov:Entity> without xml:id")
            continue
        quote_ids.add(eid)
        if entity.find(f"{{{PROV}}}value") is None:
            err(f"sidecar: quote '{eid}' has no <prov:value>")
        for q in entity.findall(f"{{{PROV}}}wasQuotedFrom"):
            res = q.get(f"{{{PROV}}}resource") or ""
            target = res.rsplit("#", 1)[-1] if "#" in res else None
            if target is None or target not in source_keys:
                err(
                    f"sidecar: quote '{eid}' wasQuotedFrom '{res}' does not "
                    f"resolve to a LegalSource/Source key in the .lrml"
                )

    n_links = 0
    for link in prov_root.iter(f"{{{PROV}}}wasDerivedFrom"):
        gen = link.get(f"{{{PROV}}}generatedEntity") or ""
        used = link.get(f"{{{PROV}}}usedEntity") or ""
        n_links += 1
        gen_key = gen.split("#")[-1] if "#" in gen else None
        if not gen_key or strip_key(gen_key) not in keys:
            err(
                f"sidecar: wasDerivedFrom generatedEntity '{gen}' does not "
                f"resolve to a @key in the .lrml"
            )
        used_id = local_ref(used)
        if not used_id or used_id not in quote_ids:
            err(
                f"sidecar: wasDerivedFrom usedEntity '{used}' does not "
                f"resolve to a quote <prov:Entity xml:id>"
            )
    if quote_ids and n_links == 0:
        warn(
            "sidecar declares quotes but no <prov:wasDerivedFrom> links — "
            "no fragment is anchored to them"
        )


def _relation_occurrences(
    root: ET.Element, keys: dict[str, ET.Element]
) -> dict[str, dict[str, object]]:
    parents = {child: parent for parent in root.iter() for child in parent}
    roles = collect_voice_roles(root)
    statement_owners: dict[str, set[str]] = {}
    for role in roles:
        if not role.substantive:
            continue
        for expression_key in role.expressions:
            statement_key = _statement_ancestor_key(expression_key, keys, parents)
            if statement_key is not None:
                statement_owners.setdefault(statement_key, set()).add(role.name)

    occurrences: dict[str, dict[str, object]] = {}
    for atom in root.iter(f"{{{RULEML}}}Atom"):
        relation = atom.find(f"{{{RULEML}}}Rel")
        iri = relation.get("iri") if relation is not None else None
        if not iri:
            continue
        element: ET.Element | None = atom
        statement_key = None
        while element is not None:
            if element.tag in STATEMENT_TAGS and element.get("key"):
                statement_key = strip_key(element.get("key") or "")
                break
            element = parents.get(element)
        terms: list[tuple[str, str | None]] = []
        for term in atom:
            kind = term.tag.rsplit("}", 1)[-1]
            if kind not in {"Var", "Ind", "Data"}:
                continue
            datatype = next(
                (
                    value
                    for name, value in term.attrib.items()
                    if name.rsplit("}", 1)[-1] == "type"
                ),
                None,
            )
            terms.append((kind, datatype))
        entry = occurrences.setdefault(
            iri,
            {
                "arities": set(),
                "terms": [],
                "usages": set(),
                "voices": set(),
                "usageVoices": {},
            },
        )
        arities = entry["arities"]
        term_profiles = entry["terms"]
        usages = entry["usages"]
        voices = entry["voices"]
        usage_voices = entry["usageVoices"]
        assert isinstance(arities, set)
        assert isinstance(term_profiles, list)
        assert isinstance(usages, set)
        assert isinstance(voices, set)
        assert isinstance(usage_voices, dict)
        arities.add(len(terms))
        term_profiles.append(terms)
        if statement_key is not None:
            usages.add(statement_key)
            owners = statement_owners.get(statement_key, set())
            voices.update(owners)
            usage_voices.setdefault(statement_key, set()).update(owners)
    return occurrences


def _sidecar_relation_evidence(
    sidecar: Path,
) -> tuple[dict[str, str], set[tuple[str, str]]]:
    if not sidecar.is_file():
        return {}, set()
    try:
        prov_root = ET.parse(sidecar).getroot()
    except ET.ParseError:
        return {}, set()
    quotes: dict[str, str] = {}
    for entity in prov_root.iter(f"{{{PROV}}}Entity"):
        quote_id = entity.get(f"{{{XML}}}id")
        value = entity.find(f"{{{PROV}}}value")
        if quote_id and value is not None:
            quotes[quote_id] = " ".join("".join(value.itertext()).split())
    links: set[tuple[str, str]] = set()
    for derivation in prov_root.iter(f"{{{PROV}}}wasDerivedFrom"):
        generated = derivation.get(f"{{{PROV}}}generatedEntity") or ""
        quote = local_ref(derivation.get(f"{{{PROV}}}usedEntity") or "")
        if "#" in generated and quote:
            links.add((strip_key(generated.rsplit("#", 1)[-1]), quote))
    return quotes, links


def check_relations(
    path: Path, root: ET.Element, keys: dict[str, ET.Element]
) -> list[dict[str, object]]:
    manifest_path = path.with_suffix(".relations.json")
    if not manifest_path.is_file():
        err(f"no relation manifest ({manifest_path.name})")
        return []
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        err(f"relation manifest {manifest_path.name}: cannot read JSON: {exc}")
        return []
    if not isinstance(payload, dict):
        err(f"relation manifest {manifest_path.name}: root must be an object")
        return []
    if payload.get("schemaVersion") != "1.0":
        err("relation manifest: schemaVersion must be '1.0'")
    if payload.get("source") != path.name:
        err(f"relation manifest: source must be '{path.name}'")
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if payload.get("sourceSha256") != source_hash:
        err("relation manifest: sourceSha256 does not match the LRML file")

    relations = payload.get("relations")
    if not isinstance(relations, list):
        err("relation manifest: relations must be an array")
        return []
    declared: dict[str, dict[str, object]] = {}
    for index, item in enumerate(relations):
        if not isinstance(item, dict):
            err(f"relation manifest: relations[{index}] must be an object")
            continue
        iri = item.get("iri")
        if not isinstance(iri, str) or not iri:
            err(f"relation manifest: relations[{index}].iri must be a non-empty string")
            continue
        if iri in declared:
            err(f"relation manifest: duplicate relation IRI '{iri}'")
            continue
        declared[iri] = item

    actual = _relation_occurrences(root, keys)
    for iri in sorted(actual.keys() - declared.keys()):
        err(f"relation manifest: LRML relation '{iri}' is not declared")
    for iri in sorted(declared.keys() - actual.keys()):
        err(f"relation manifest: declared relation '{iri}' is unused")

    quotes, evidence_links = _sidecar_relation_evidence(path.with_suffix(".prov.xml"))
    parents = {child: parent for parent in root.iter() for child in parent}
    for iri in sorted(actual.keys() & declared.keys()):
        item = declared[iri]
        observed = actual[iri]
        meaning = item.get("meaning")
        if not isinstance(meaning, str) or not meaning.strip():
            err(f"relation manifest: '{iri}' has no plain-language meaning")
        arities = observed["arities"]
        assert isinstance(arities, set)
        if len(arities) != 1:
            err(
                f"relation manifest: LRML relation '{iri}' has inconsistent arities {sorted(arities)}"
            )
            continue
        arity = next(iter(arities))
        if item.get("arity") != arity:
            err(
                f"relation manifest: '{iri}' declares arity {item.get('arity')!r}, LRML uses {arity}"
            )
        arguments = item.get("arguments")
        if not isinstance(arguments, list) or len(arguments) != arity:
            err(f"relation manifest: '{iri}' must declare {arity} ordered arguments")
        else:
            term_profiles = observed["terms"]
            assert isinstance(term_profiles, list)
            for position, argument in enumerate(arguments):
                if not isinstance(argument, dict):
                    err(
                        f"relation manifest: '{iri}' argument {position + 1} must be an object"
                    )
                    continue
                role = argument.get("role")
                kind = argument.get("kind")
                if not isinstance(role, str) or not role.strip():
                    err(
                        f"relation manifest: '{iri}' argument {position + 1} has no role"
                    )
                if kind not in {"individual", "data"}:
                    err(
                        f"relation manifest: '{iri}' argument {position + 1} kind must be individual or data"
                    )
                    continue
                for profile in term_profiles:
                    term_kind, datatype = profile[position]
                    if term_kind == "Var":
                        continue
                    observed_kind = "data" if term_kind == "Data" else "individual"
                    if observed_kind != kind:
                        err(
                            f"relation manifest: '{iri}' argument {position + 1} declares {kind}, "
                            f"LRML uses {observed_kind}"
                        )
                    declared_datatype = argument.get("datatype")
                    if (
                        kind == "data"
                        and declared_datatype
                        and datatype != declared_datatype
                    ):
                        err(
                            f"relation manifest: '{iri}' argument {position + 1} declares datatype "
                            f"{declared_datatype!r}, LRML uses {datatype!r}"
                        )

        observed_usages = observed["usages"]
        observed_voices = observed["voices"]
        usage_voices = observed["usageVoices"]
        assert isinstance(observed_usages, set)
        assert isinstance(observed_voices, set)
        assert isinstance(usage_voices, dict)
        usages = item.get("usages")
        if not isinstance(usages, list) or not all(
            isinstance(value, str) for value in usages
        ):
            err(
                f"relation manifest: '{iri}' usages must be an array of expression keys"
            )
        elif set(usages) != observed_usages:
            err(
                f"relation manifest: '{iri}' usages {sorted(set(usages))} do not match "
                f"LRML usages {sorted(observed_usages)}"
            )
        elif usages != sorted(set(usages)):
            err(f"relation manifest: '{iri}' usages must be sorted and unique")
        voices = item.get("voices")
        if not isinstance(voices, list) or not all(
            isinstance(value, str) for value in voices
        ):
            err(f"relation manifest: '{iri}' voices must be an array")
        elif set(voices) != observed_voices:
            err(
                f"relation manifest: '{iri}' voices {sorted(set(voices))} do not match "
                f"direct Role ownership {sorted(observed_voices)}"
            )
        elif voices != sorted(set(voices)):
            err(f"relation manifest: '{iri}' voices must be sorted and unique")

        source_forms = item.get("sourceForms")
        if not isinstance(source_forms, list) or not source_forms:
            err(f"relation manifest: '{iri}' must include sourceForms evidence")
            continue
        for source_index, source_form in enumerate(source_forms):
            if not isinstance(source_form, dict):
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] must be an object"
                )
                continue
            text = source_form.get("text")
            voice = source_form.get("voice")
            expression = source_form.get("expression")
            quote = source_form.get("quote")
            if not isinstance(text, str) or not text.strip():
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] has no text"
                )
            if not isinstance(voice, str):
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] voice must be a string"
                )
            if not isinstance(expression, str) or expression not in keys:
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] expression does not resolve"
                )
            source_statement = (
                _statement_ancestor_key(expression, keys, parents)
                if isinstance(expression, str)
                else None
            )
            if source_statement not in observed_usages:
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] expression "
                    "does not contain this relation"
                )
            statement_voices = usage_voices.get(source_statement, set())
            if isinstance(voice, str) and voice not in statement_voices:
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] voice does "
                    "not own its expression"
                )
            if not isinstance(quote, str) or quote not in quotes:
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] quote does not resolve"
                )
            elif isinstance(text, str) and " ".join(text.split()) not in quotes[quote]:
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] text is not "
                    "present in its quote"
                )
            if (
                isinstance(expression, str)
                and isinstance(quote, str)
                and (expression, quote) not in evidence_links
            ):
                err(
                    f"relation manifest: '{iri}' sourceForms[{source_index}] quote is not "
                    "derived onto its expression"
                )
    return [item for item in relations if isinstance(item, dict)]


def relations_report(path: Path, relations: list[dict[str, object]]) -> None:
    print(f"RELATIONS  {path.name}")
    for item in sorted(relations, key=lambda relation: str(relation.get("iri", ""))):
        arguments = item.get("arguments")
        signature = (
            ", ".join(
                f"{argument.get('role')}:{argument.get('kind')}"
                for argument in arguments
                if isinstance(argument, dict)
            )
            if isinstance(arguments, list)
            else "?"
        )
        voice_values = item.get("voices")
        usage_values = item.get("usages")
        voices = (
            ", ".join(str(value) for value in voice_values)
            if isinstance(voice_values, list)
            else "?"
        )
        usages = (
            ", ".join(str(value) for value in usage_values)
            if isinstance(usage_values, list)
            else "?"
        )
        print(
            f"  {item.get('iri', '?')}({signature})  voices=[{voices}]  usages=[{usages}]"
        )


def keys_iter(keys: dict[str, ET.Element], tag: str) -> Iterator[ET.Element]:
    return (el for el in keys.values() if el.tag == tag)


def main() -> int:
    args = sys.argv[1:]
    strict = "--strict" in args
    show_hjemmel = "--hjemmel" in args
    show_voices = "--voices" in args
    show_relations = "--relations" in args
    positional = [arg for arg in args if not arg.startswith("--")]
    known_options = ("--strict", "--hjemmel", "--voices", "--relations")
    unknown = [arg for arg in args if arg.startswith("--") and arg not in known_options]
    if len(positional) != 1 or unknown:
        print(__doc__.strip().splitlines()[2])
        return 2
    path = Path(positional[0])
    if not path.is_file():
        print(f"no such file: {path}")
        return 2

    validate_xsd(path)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        err(f"XML parse error: {exc}")
        root = None

    if root is not None:
        check_no_embedded_prov(root)
        keys = collect_keys(root)
        check_refs(root, keys)
        check_acyclic(root, keys)
        check_rules(root)
        associations = collect_hjemmel(root, keys)
        check_hjemmel(root, keys, associations, strict)
        roles = collect_voice_roles(root)
        voice_profile = show_voices or any(role.substantive for role in roles)
        if voice_profile:
            check_voices(root, keys, roles, strict)

        sidecar = path.with_suffix(".prov.xml")
        if sidecar.is_file():
            check_sidecar(sidecar, keys)
        else:
            warn(f"no PROV sidecar ({sidecar.name}) — text isomorphism not anchored")

        source_manifest = path.with_suffix(".source.json")
        voice_ledger = path.with_suffix(".voices.json")
        if sidecar.is_file() or source_manifest.is_file() or voice_ledger.is_file():
            if not source_manifest.is_file():
                err(f"no source manifest ({source_manifest.name}) for voice ledger")
            elif not voice_ledger.is_file():
                err(f"no voice ledger ({voice_ledger.name}) for source manifest")
            else:
                validate_source_bundle(
                    source_manifest,
                    voice_ledger,
                    sidecar if sidecar.is_file() else None,
                    lambda message: err(f"source bundle: {message}"),
                )

        if show_hjemmel:
            hjemmel_report(path, root, keys, associations)
        if show_voices:
            voices_report(root, keys, roles)
        if show_relations:
            relations = check_relations(path, root, keys)
            relations_report(path, relations)

    for w in warnings:
        print(f"WARN  {w}")
    if errors:
        for e in errors:
            print(f"ERROR {e}")
        print(f"FAIL  {path.name}: {len(errors)} error(s)")
        return 1
    print(
        f"OK    {path.name} valid"
        + ("" if not warnings else f" ({len(warnings)} warning(s))")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
