# common.fontwork.py

import wx

_knownFontFaces = None
def getFont(xmlElement, initialfont = None):
    global _knownFontFaces
    font = None
    if initialfont is None:
        fontfamily = wx.FONTFAMILY_DEFAULT
        fontface = ""
        fontsize = 10
        fontstyle = wx.FONTSTYLE_NORMAL
        fontweight = wx.FONTWEIGHT_NORMAL
    else:
        fontface = initialfont.GetFaceName()
        if not fontface: fontfamily = initialfont.GetFamily()
        else: fontfamily = wx.FONTFAMILY_DEFAULT
        fontsize = initialfont.GetPointSize()
        fontstyle = initialfont.GetStyle()
        fontweight = initialfont.GetWeight()
    if xmlElement:
        fontfamilystr = xmlElement.getAttribute("font-family")
        fontsizestr = xmlElement.getAttribute("font-size")
        fontstylestr = xmlElement.getAttribute("font-style")
        fontweightstr = xmlElement.getAttribute("font-weight")
        if fontfamilystr or fontsizestr or fontstylestr or fontweightstr:
            if fontfamilystr:
                fontface = ''
                if fontfamilystr == 'serif': fontfamily = wx.FONTFAMILY_ROMAN
                elif fontfamilystr == 'sans-serif': fontfamily = wx.FONTFAMILY_SWISS
                elif fontfamilystr == 'cursive': fontfamily = wx.FONTFAMILY_SCRIPT
                elif fontfamilystr == 'fantasy': fontfamily = wx.FONTFAMILY_DECORATIVE
                elif fontfamilystr == 'monospace': fontfamily = wx.FONTFAMILY_MODERN # or wx.FONTFAMILY_TELETYPE ?
                else: fontface = fontfamilystr
            if fontsizestr: fontsize = int(fontsizestr)
            if fontstylestr == '' or fontstylestr == 'normal': fontstyle = wx.FONTSTYLE_NORMAL
            elif fontstylestr == 'italic': fontstyle = wx.FONTSTYLE_ITALIC
            elif fontstylestr == 'oblique': fontstyle = wx.FONTSTYLE_SLANT
            if fontweightstr == '' or fontweightstr == 'normal': fontweight = wx.FONTWEIGHT_NORMAL
            elif fontweightstr == 'bold': fontweight = wx.FONTWEIGHT_BOLD
            elif fontweightstr == 'lighter': fontweight = wx.FONTWEIGHT_LIGHT
    if _knownFontFaces is None:
        fontEnum = wx.FontEnumerator()
        fontEnum.EnumerateFacenames()
        _knownFontFaces = fontEnum.GetFacenames()
    if fontface and fontface not in _knownFontFaces:
        fontface = ''
    font = wx.Font(fontsize, fontfamily, fontstyle,
               fontweight, False, fontface)
    return font

def fontElements(font, defaultFont=None):
    elements = [0,"","normal","normal"] # font-size, font-family (or face), font-style, font-weight ] #TODO more (text-decoration: "underline", text-decoration="line-through" (for strikethrough - we can have both (sep by space))
    pointsize = font.GetPointSize()
    elements[0] = pointsize

    fontface = font.GetFaceName()
    fontfamily = font.GetFamily()
    if fontface: # and fontface != 'sans':
         elements[1] = fontface
    else:
        #result += ' font-family="' + fontfamily + '"'
        if fontfamily == wx.FONTFAMILY_ROMAN: fontfamilystr = 'serif'
        elif fontfamily == wx.FONTFAMILY_SWISS: fontfamilystr = 'sans-serif'
        elif fontfamily == wx.FONTFAMILY_SCRIPT: fontfamilystr = 'cursive'
        elif fontfamily == wx.FONTFAMILY_DECORATIVE: fontfamilystr = 'fantasy'
        else: fontfamilystr = 'monospace'
        elements[1] = fontfamilystr

    fontstyle = font.GetStyle()
    elements[2] = "normal"
    if fontstyle == wx.FONTSTYLE_ITALIC:
        elements[2] = "italic"
    elif fontstyle == wx.FONTSTYLE_SLANT:
        elements[2] = "oblique"

    fontweight = font.GetWeight()
    elements[3] = "normal"
    if fontweight == wx.FONTWEIGHT_BOLD:
        elements[3] = "bold"
    elif fontweight == wx.FONTWEIGHT_LIGHT:
        elements[3] = "lighter"
    return elements

def fontStr(font, defaultFont=None, saveDefaults=False):
    result = ""
    elements = fontElements(font)
    result += ' font-size="' + str(elements[0]) + '"'
    result += ' font-family="' + elements[1] + '"'
    if saveDefaults or elements[2] != "normal":
        result += ' font-style="' + elements[2] + '"'
    if saveDefaults or elements[3] != "normal":
        result += ' font-weight="' + elements[3] + '"'

    if defaultFont:
        default_result = fontStr(defaultFont, None, saveDefaults)
        default_parts = default_result.split()
        for default_part in default_parts:
            result = result.replace(default_part, '')
        result = result.strip()
        if result:
            result = ' ' + result
    return result

def setFontXmlElements(elementXmlElement, newValue):
    elements = fontElements(newValue)
    elementXmlElement.setAttribute("font-size", elements[0])
    if elements[1]:
        elementXmlElement.setAttribute("font-family", elements[1])
    if elements[2]:
        elementXmlElement.setAttribute("font-style", elements[2])
    if elements[3]:
        elementXmlElement.setAttribute("font-weight", elements[3])
