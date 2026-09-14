<?xml version="1.0" encoding="UTF-8"?>
<!--
  lrml-to-dot.xsl — Visualize a LegalRuleML (.lrml) file as a Graphviz graph.

  Generic transform: it does not hard-code this vedtak. The rules are:
    * Every element carrying an @key becomes a node (a leading ':' on RuleML
      CURIE keys is stripped, so "#keyref" values match).
    * A keyless <lrml:LegalReference>/<lrml:Reference> becomes a node under its
      @refersTo internal id.
    * Every <lrml:Association> becomes an implicit hub node (it has no @key).
    * Every internal reference becomes a labeled edge from the nearest
      enclosing keyed node (or Association) to the referenced @key:
        - any attribute whose value starts with '#'  (keyref, hasCreationDate, …)
        - the @over / @under attributes on <lrml:Override>
      The edge label is the local-name of the referencing element
      (appliesSource, inScope, toTarget, forExpression, …) or
      'over'/'under' for Override.

  Node shape/colour is chosen by the element's local-name so the legal
  structure (rules vs facts vs overrides vs context …) is visible at a glance.

  Usage:
    xsltproc legalruleml/viz/lrml-to-dot.xsl samples/out/<name>.lrml \
      | dot -Tsvg -o <name>.svg
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:lrml="http://docs.oasis-open.org/legalruleml/ns/v1.0/"
    xmlns:ruleml="http://ruleml.org/spec">

  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:strip-space elements="*"/>

  <!-- ── Root: emit the digraph wrapper ─────────────────────── -->
  <xsl:template match="/">
    <xsl:text>digraph LegalRuleML {&#10;</xsl:text>
    <xsl:text>  rankdir=LR;&#10;</xsl:text>
    <xsl:text>  graph [fontname="Helvetica", fontsize=11, splines=true, nodesep=0.35, ranksep=0.7];&#10;</xsl:text>
    <xsl:text>  node  [fontname="Helvetica", fontsize=10, style="filled,rounded", color="#888888"];&#10;</xsl:text>
    <xsl:text>  edge  [fontname="Helvetica", fontsize=8, color="#555555", arrowsize=0.7];&#10;&#10;</xsl:text>

    <!-- Nodes -->
    <xsl:apply-templates
        select="//*[@key][not(self::lrml:Association)] | //lrml:LegalReference[@refersTo and not(@key)] | //lrml:Reference[@refersTo and not(@key)]"
        mode="node"/>
    <xsl:apply-templates select="//lrml:Association" mode="assoc-node"/>

    <xsl:text>&#10;</xsl:text>

    <!-- Edges: internal references (#-prefixed attribute values) -->
    <xsl:apply-templates select="//@*[starts-with(., '#')]" mode="ref-edge"/>
    <!-- Edges: Override over/under -->
    <xsl:apply-templates select="//lrml:Override/@over | //lrml:Override/@under" mode="override-edge"/>

    <xsl:text>}&#10;</xsl:text>
  </xsl:template>

  <!-- ── Keyed nodes (and keyless references) ───────────────── -->
  <xsl:template match="*" mode="node">
    <xsl:variable name="ln" select="local-name()"/>
    <xsl:variable name="id">
      <xsl:call-template name="self-id"/>
    </xsl:variable>
    <xsl:text>  "</xsl:text><xsl:value-of select="$id"/><xsl:text>" [label="</xsl:text>
    <xsl:value-of select="$ln"/>
    <xsl:text>\n</xsl:text><xsl:value-of select="$id"/>
    <!-- show a compact hint of the payload where useful -->
    <xsl:call-template name="node-hint"/>
    <xsl:text>"</xsl:text>
    <xsl:call-template name="node-style">
      <xsl:with-param name="ln" select="$ln"/>
    </xsl:call-template>
    <xsl:text>];&#10;</xsl:text>
  </xsl:template>

  <!-- ── Association hub nodes ──────────────────────────────
       A hjemmel Association carries a @key (see
       wiki/concepts/hjemmel-anchoring.md); unkeyed ones fall back to
       generate-id(), matching what "source-id" resolves edges to. -->
  <xsl:template match="lrml:Association" mode="assoc-node">
    <xsl:text>  "</xsl:text>
    <xsl:choose>
      <xsl:when test="@key"><xsl:call-template name="self-id"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="generate-id()"/></xsl:otherwise>
    </xsl:choose>
    <xsl:text>" [label="Association</xsl:text>
    <xsl:if test="@key"><xsl:text>\n</xsl:text><xsl:call-template name="self-id"/></xsl:if>
    <xsl:text>", shape=point, width=0.12, color="#1f77b4", fillcolor="#1f77b4"];&#10;</xsl:text>
  </xsl:template>

  <!-- ── Reference edges (#-prefixed attribute values) ──────── -->
  <xsl:template match="@*" mode="ref-edge">
    <!-- skip @over/@under (handled separately) and @key itself -->
    <xsl:if test="not(local-name() = 'over' or local-name() = 'under' or local-name() = 'key')">
      <xsl:variable name="src">
        <xsl:call-template name="source-id"/>
      </xsl:variable>
      <xsl:variable name="target" select="substring-after(., '#')"/>
      <xsl:if test="string-length($src) &gt; 0 and string-length($target) &gt; 0">
        <xsl:text>  "</xsl:text><xsl:value-of select="$src"/>
        <xsl:text>" -> "</xsl:text><xsl:value-of select="$target"/>
        <xsl:text>" [label="</xsl:text><xsl:value-of select="local-name(..)"/><xsl:text>"</xsl:text>
        <xsl:choose>
          <xsl:when test="local-name(..) = 'filledBy' or local-name(..) = 'forExpression'">
            <xsl:text>, color="#0f766e", fontcolor="#115e59", penwidth=2</xsl:text>
          </xsl:when>
          <xsl:when test="local-name(..) = 'appliesAlternatives'">
            <xsl:text>, color="#7c3aed", fontcolor="#6d28d9", penwidth=2, style=dashed</xsl:text>
          </xsl:when>
          <xsl:when test="local-name(..) = 'inScope'">
            <xsl:text>, color="#7c3aed", fontcolor="#6d28d9", penwidth=2</xsl:text>
          </xsl:when>
        </xsl:choose>
        <xsl:text>];&#10;</xsl:text>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <!-- ── Override edges ─────────────────────────────────────── -->
  <xsl:template match="lrml:Override/@over | lrml:Override/@under" mode="override-edge">
    <xsl:variable name="src">
      <xsl:call-template name="source-id"/>
    </xsl:variable>
    <xsl:variable name="target" select="substring-after(., '#')"/>
    <xsl:text>  "</xsl:text><xsl:value-of select="$src"/>
    <xsl:text>" -> "</xsl:text><xsl:value-of select="$target"/>
    <xsl:text>" [label="</xsl:text><xsl:value-of select="local-name()"/>
    <xsl:text>", style=dashed, color="#d62728", fontcolor="#d62728"];&#10;</xsl:text>
  </xsl:template>

  <!-- ── Helper: node id of the current element ─────────────── -->
  <xsl:template name="self-id">
    <xsl:choose>
      <xsl:when test="starts-with(@key, ':')">
        <xsl:value-of select="substring(@key, 2)"/>
      </xsl:when>
      <xsl:when test="@key">
        <xsl:value-of select="@key"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@refersTo"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ── Helper: id of the nearest enclosing keyed/Association node ── -->
  <xsl:template name="source-id">
    <xsl:variable name="anchor"
        select="ancestor-or-self::*[@key or local-name() = 'Association'][1]"/>
    <xsl:choose>
      <xsl:when test="$anchor/@key">
        <xsl:for-each select="$anchor">
          <xsl:call-template name="self-id"/>
        </xsl:for-each>
      </xsl:when>
      <xsl:when test="$anchor">
        <xsl:value-of select="generate-id($anchor)"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!-- ── Helper: shape/colour by element type ───────────────── -->
  <xsl:template name="node-style">
    <xsl:param name="ln"/>
    <xsl:choose>
      <xsl:when test="$ln = 'PrescriptiveStatement'">
        <xsl:text>, shape=box, fillcolor="#cfe8ff"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'ConstitutiveStatement'">
        <xsl:text>, shape=box, fillcolor="#d8f0d8"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'FactualStatement'">
        <xsl:text>, shape=ellipse, fillcolor="#fff2cc"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'OverrideStatement'">
        <xsl:text>, shape=diamond, fillcolor="#f4cccc"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'Alternatives'">
        <xsl:text>, shape=folder, fillcolor="#ead1dc"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'Context'">
        <xsl:text>, shape=component, fillcolor="#e6e6e6"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'TemporalCharacteristic' or $ln = 'Time'">
        <xsl:text>, shape=note, fillcolor="#fce5cd"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'LegalReference' or $ln = 'LegalSource'">
        <xsl:text>, shape=note, fillcolor="#d9d2e9"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'Agent' or $ln = 'Figure'">
        <xsl:text>, shape=box, fillcolor="#dbeafe", color="#2563eb"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'Role'">
        <xsl:text>, shape=box, fillcolor="#ccfbf1", color="#0f766e"</xsl:text>
      </xsl:when>
      <xsl:when test="$ln = 'Authority' or $ln = 'Jurisdiction'">
        <xsl:text>, shape=box, fillcolor="#f3f3f3"</xsl:text>
      </xsl:when>
      <!-- a keyed rule fragment: one vilkår with its own hjemmel -->
      <xsl:when test="$ln = 'Atom'">
        <xsl:text>, shape=box, style="filled", fillcolor="#e8f1fb"</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>, shape=box, fillcolor="#ffffff"</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ── Helper: compact payload hint for a few node types ──── -->
  <xsl:template name="node-hint">
    <xsl:choose>
      <!-- Factual statements: show the relation + first data value -->
      <xsl:when test="local-name() = 'FactualStatement'">
        <xsl:variable name="rel" select=".//ruleml:Rel[1]/@iri"/>
        <xsl:if test="$rel">
          <xsl:text>\n</xsl:text>
          <xsl:if test=".//ruleml:Neg"><xsl:text>¬</xsl:text></xsl:if>
          <xsl:value-of select="$rel"/>
        </xsl:if>
        <xsl:if test=".//ruleml:Data">
          <xsl:text> = </xsl:text><xsl:value-of select="normalize-space(.//ruleml:Data[1])"/>
        </xsl:if>
      </xsl:when>
      <!-- Legal references: show the human refID -->
      <xsl:when test="local-name() = 'LegalReference' and @refID">
        <xsl:text>\n</xsl:text><xsl:value-of select="@refID"/>
      </xsl:when>
      <!-- Keyed vilkår atoms: show the relation they assert -->
      <xsl:when test="local-name() = 'Atom' and ruleml:Rel/@iri">
        <xsl:text>\n</xsl:text><xsl:value-of select="ruleml:Rel/@iri"/>
      </xsl:when>
      <!-- Time: show the literal value -->
      <xsl:when test="local-name() = 'Time'">
        <xsl:text>\n</xsl:text><xsl:value-of select="normalize-space(.)"/>
      </xsl:when>
      <!-- Procedural Role: show its profile IRI and Actor. -->
      <xsl:when test="local-name() = 'Role'">
        <xsl:if test="@iri">
          <xsl:text>\n</xsl:text><xsl:value-of select="@iri"/>
        </xsl:if>
        <xsl:if test="lrml:filledBy/@keyref">
          <xsl:text>\nfilledBy </xsl:text><xsl:value-of select="lrml:filledBy[1]/@keyref"/>
        </xsl:if>
      </xsl:when>
      <!-- Context: make the selected legal rendering visible in the node. -->
      <xsl:when test="local-name() = 'Context' and lrml:inScope/@keyref">
        <xsl:text>\nselects </xsl:text><xsl:value-of select="lrml:inScope[1]/@keyref"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
