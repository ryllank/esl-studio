#! /usr/bin/python

import wx

TransparentColour = wx.Colour(255, 255, 255, 0)  # this looks White in colour dlg - alt: wx.TransparentColour # this looks black in colour dlg

_UseOwnColourNames = True
_UseTheColourDatabase = False

# name : htmlHexForm
_PrimaryColours = { # these are (preferred) names for a unique set of colours
    "Alice Blue" :	"#F0F8FF",
    "Antique White" :	"#FAEBD7",
    #
    "Aquamarine" :	"#7FFFD4",
    "Azure" :	"#F0FFFF",
    "Beige" :	"#F5F5DC",
    "Bisque" :	"#FFE4C4",
    "Black" :	"#000000",
    "Blanched Almond" :	"#FFEBCD",
    "Blue" :	"#0000FF",
    "Blue Violet" :	"#8A2BE2",
    "Brown" :	"#A52A2A",
    "Burlywood" :	"#DEB887",
    "Cadet Blue" :	"#5F9EA0",
    "Chartreuse" :	"#7FFF00",
    "Chocolate" :	"#D2691E",
    "Coral" :	"#FF7F50",
    "Cornflower Blue" :	"#6495ED",
    "Cornsilk" :	"#FFF8DC",
    "Crimson" :	"#DC143C",
    "Cyan" :	"#00FFFF",
    "Dark Blue" :	"#00008B",
    "Dark Cyan" :	"#008B8B",
    "Dark Goldenrod" :	"#B8860B",
    "Dark Green" :	"#006400",
    "Dark Grey" :	"#A9A9A9",
    "Dark Khaki" :	"#BDB76B",
    "Dark Magenta" :	"#8B008B",
    "Dark Olive Green" :	"#556B2F",
    "Dark Orange" :	"#FF8C00",
    "Dark Orchid" :	"#9932CC",
    "Dark Red" :	"#8B0000",
    "Dark Salmon" :	"#E9967A",
    "Dark Sea Green" :	"#8FBC8F",
    "Dark Slate Blue" :	"#483D8B",
    "Dark Slate Grey" :	"#2F4F4F",
    "Dark Turquoise" :	"#00CED1",
    "Dark Violet" :	"#9400D3",
    "Deep Pink" :	"#FF1493",
    "Deep Sky Blue" :	"#00BFFF",
    "Dim Grey" :	"#696969",
    "Dodger Blue" :	"#1E90FF",
    "Firebrick" :	"#B22222",
    "Floral White" :	"#FFFAF0",
    "Forest Green" :	"#228B22",
    #
    "Gainsboro" :	"#DCDCDC",
    "Ghost White" :	"#F8F8FF",
    "Goldenrod" :	"#DAA520",
    "Gold" :	"#FFD700",
    "Green" :	"#008000",
    "Green Yellow" :	"#ADFF2F",
    "Grey" :	"#808080",
    "Honeydew" :	"#F0FFF0",
    "Hot Pink" :	"#FF69B4",
    "Indian Red" :	"#CD5C5C",
    "Indigo" :	"#4B0082",
    "Ivory" :	"#FFFFF0",
    "Khaki" :	"#F0E68C",
    "Lavender Blush" :	"#FFF0F5",
    "Lavender" :	"#E6E6FA",
    "Lawn Green" :	"#7CFC00",
    "Lemon Chiffon" :	"#FFFACD",
    "Light Blue" :	"#ADD8E6",
    "Light Coral" :	"#F08080",
    "Light Cyan" :	"#E0FFFF",
    "Light Goldenrod Yellow" :	"#FAFAD2",
    "Light Green" :	"#90EE90",
    "Light Grey" :	"#D3D3D3",
    "Light Pink" :	"#FFB6C1",
    "Light Salmon" :	"#FFA07A",
    "Light Sea Green" :	"#20B2AA",
    "Light Sky Blue" :	"#87CEFA",
    "Light Slate Grey" :	"#778899",
    "Light Steel Blue" :	"#B0C4DE",
    "Light Yellow" :	"#FFFFE0",
    "Lime" :	"#00FF00",
    "Lime Green" :	"#32CD32",
    "Linen" :	"#FAF0E6",
    "Magenta" :	"#FF00FF",
    "Maroon" :	"#800000",
    "Medium Aquamarine" :	"#66CDAA",
    "Medium Blue" :	"#0000CD",
    "Medium Orchid" :	"#BA55D3",
    "Medium Purple" :	"#9370DB",
    "Medium Sea Green" :	"#3CB371",
    "Medium Slate Blue" :	"#7B68EE",
    "Medium Spring Green" :	"#00FA9A",
    "Medium Turquoise" :	"#48D1CC",
    "Medium Violet Red" :	"#C71585",
    "Midnight Blue" :	"#191970",
    "Mint Cream" :	"#F5FFFA",
    "Misty Rose" :	"#FFE4E1",
    "Moccasin" :	"#FFE4B5",
    "Navajo White" :	"#FFDEAD",
    "Navy" :	"#000080",
    "Old Lace" :	"#FDF5E6",
    "Olive" :	"#808000",
    "Olive Drab" :	"#6B8E23",
    "Orange" :	"#FFA500",
    "Orange Red" :	"#FF4500",
    "Orchid" :	"#DA70D6",
    "Pale Goldenrod" :	"#EEE8AA",
    "Pale Green" :	"#98FB98",
    "Pale Turquoise" :	"#AFEEEE",
    "Pale Violet Red" :	"#DB7093",
    "Papaya Whip" :	"#FFEFD5",
    "Peach Puff" :	"#FFDAB9",
    "Peru" :	"#CD853F",
    "Pink" :	"#FFC0CB",
    "Plum" :	"#DDA0DD",
    "Powder Blue" :	"#B0E0E6",
    "Purple" :	"#800080",
    "Red" :	"#FF0000",
    "Rosy Brown" :	"#BC8F8F",
    "Royal Blue" :	"#41690",
    "Saddle Brown" :	"#8B4513",
    "Salmon" :	"#FA8072",
    "Sandy Brown" :	"#F4A460",
    "Sea Green" :	"#2E8B57",
    "Seashell" :	"#FFF5EE",
    "Sienna" :	"#A0522D",
    "Silver" :	"#C0C0C0",
    "Sky Blue" :	"#87CEEB",
    "Slate Blue" :	"#6A5ACD",
    "Slate Grey" :	"#708090",
    "Snow" :	"#FFFAFA",
    "Spring Green" :	"#00FF7F",
    "Steel Blue" :	"#4682B4",
    "Tan" :	"#D2B48C",
    "Teal" :	"#008080",
    "Thistle" :	"#D8BFD8",
    "Tomato" :	"#FF6347",
    "Turquoise" :	"#40E0D0",
    "Violet" :	"#EE82EE",
    "Wheat" :	"#F5DEB3",
    "White" :	"#FFFFFF",
    "White Smoke" :	"#F5F5F5",
    "Yellow" :	"#FFFF00",
    "Yellow Green" :	"#9ACD32",
}
_AlternateColours = { # these are new names of duplicate or new colours
    # Alternates
    "Aqua" :	"#00FFFF",
    "Fuchsia" :	"#FF00FF",
    "Light Goldenrod" :	"#EEDD82",
    "Light Slate Blue" :	"#8470FF",
    "Navy Blue" :	"#000080",
    "Rebecca Purple" :	"#663399",      # new colour
}
_coloursInitialised = False
_consolidatedNames = {} # collapsed uppercase primary+alternate names
_coloursNames = {} # reverse look up colours to primary names (as specified above)
_alternateNames = {} # reverse look up colours to alternate names (to catch new colours)


def _initialiseColours():
    global _coloursInitialised
    if not _coloursInitialised:
        # Setup consolidated names of primary+alternate colours
        for name, htmlHexForm in _PrimaryColours.items():
            name = name.upper()
            name = name.replace(" ", "")
            _consolidatedNames[name] = htmlHexForm
        for name, htmlHexForm in _AlternateColours.items():
            name = name.upper()
            name = name.replace(" ", "")
            _consolidatedNames[name] = htmlHexForm
        # Setup reverse lookup of primary colours
        for name, htmlHexForm in _PrimaryColours.items():
            _coloursNames[htmlHexForm] = name
        for name, htmlHexForm in _AlternateColours.items():
            _alternateNames[htmlHexForm] = name
        _coloursInitialised = True

def _get(colourName:str) -> wx.Colour:
    result = None
    # Clean up, and apply common substitutions
    colourName = colourName.strip()
    colourName = colourName.upper()
    colourName = colourName.replace(" ", "")
    colourName = colourName.replace("GRAY", "GREY")
    htmlHexForm = _consolidatedNames.get(colourName, None)
    if htmlHexForm:
        result = wx.Colour(htmlHexForm)
    return result

def _name(colour:wx.Colour) -> str:
    result = ""
    htmlHexForm = colour.GetAsString(wx.C2S_HTML_SYNTAX)
    if htmlHexForm:
        result = _coloursNames.get(htmlHexForm, "") # just primary ones
    if not result: # to catch new names (duplicates should be caught above)
        result = _alternateNames.get(htmlHexForm, "")
    return result

def get(colourName:str) -> wx.Colour:
    global _UseOwnColourNames, _UseTheColourDatabase
    result = None
    if _UseOwnColourNames:
        _initialiseColours()
        result = _get(colourName)
    if result is None:
        if _UseTheColourDatabase:
            result = wx.TheColourDatabase.Find(colourName)
            if not result or not result.IsOk():
                result = None
    if result is None:
        result = wx.Colour()
        result.Set(colourName)
    if not result or not result.IsOk() or result == wx.NullColour:
        result = None
    #TEMP
    #pr = ">Colours.get "+colourName
    #if result is None:
    #    pr += " None"
    #else:
    #    pr += ": "+str(name(result))+" for "+str(result)
    #print(pr)
    return result

def name(colour:wx.Colour) -> str:
    global _UseOwnColourNames, _UseTheColourDatabase
    result = ""
    if _UseOwnColourNames:
        _initialiseColours()
        result = _name(colour)
        pass
    if not result:
        if _UseTheColourDatabase:
           result = wx.TheColourDatabase.FindName(colour)
    if not result:
        result = colour.GetAsString(wx.C2S_HTML_SYNTAX)
    return result
