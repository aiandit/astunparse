<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>

  <xsl:template match="/*" mode="indentstr"/>
  <xsl:template match="*" mode="indentstr">
    <xsl:text> </xsl:text>
    <xsl:apply-templates select=".." mode="indentstr"/>
  </xsl:template>

  <xsl:template match="*" mode="indent">
    <xsl:text>&#xa;</xsl:text>
    <xsl:apply-templates select="." mode="indentstr"/>
  </xsl:template>

  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="/*">
    <xsl:text>{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}
</xsl:text>
  </xsl:template>

  <xsl:template match="*">
    <xsl:value-of select="."/>
  </xsl:template>
  <xsl:template match="str">
    <xsl:text>"</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>"</xsl:text>
  </xsl:template>

  <xsl:template match="*[* or @_class]">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>{</xsl:text>
    <xsl:for-each select="*">
      <xsl:if test="position() > 1">
	<xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:text>"</xsl:text>
      <xsl:value-of select="local-name()"/>
      <xsl:text>": </xsl:text>
      <xsl:apply-templates select="."/>
    </xsl:for-each>
    <xsl:if test="@_class">
      <xsl:if test="*">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:text>"_class": "</xsl:text>
      <xsl:value-of select="@_class"/>
      <xsl:text>"</xsl:text>
    </xsl:if>
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>}
</xsl:text>
  </xsl:template>

  <xsl:template match="*[str|num]">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="*[@_class = 'list']">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>[</xsl:text>
    <xsl:for-each select="*">
      <xsl:if test="position() > 1">
	<xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:apply-templates select="."/>
    </xsl:for-each>
    <xsl:text>]
</xsl:text>
  </xsl:template>

</xsl:stylesheet>
