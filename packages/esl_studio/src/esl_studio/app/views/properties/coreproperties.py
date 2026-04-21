#! /usr/bin/python

import sys
import wx
import wx.propgrid as wxpg

from ... import utils as Utils

PROPERTY_STANDARD_COLOUR = wx.WHITE
PROPERTY_DEFAULT_COLOUR = wx.Colour(240,240,240) #F0F0F0
PROPERTY_ALERT_COLOUR = wx.Colour(255,240,230) #FFF0E6
PROPERTY_UNCHECKED_COLOUR = wx.Colour(240,255,255) #F0FFFF
PROPERTY_NO_EDIT_COLOUR = wx.Colour(240,240,240) #F0F0F0
if sys.platform == "win32":
    PROPERTY_DEFAULT_COLOUR = wx.Colour(224,224,224) #E0E0E0
    PROPERTY_ALERT_COLOUR = wx.Colour(255,224,214) #FFE0D6
    PROPERTY_UNCHECKED_COLOUR = wx.Colour(224,255,255) #E0FFFF
    PROPERTY_NO_EDIT_COLOUR = wx.Colour(224,224,224) #E0E0E0

class CompoundProperty():
    def __init__(self):
        pass

    def enableWithChildren(self, enable): # override if some children should not be enabled/disabled in line with full property
        self.Enable(enable)

    def whitenChildren(self):
        nrChildren = 0
        try:
            nrChildren = self.GetChildCount()
        except:
            pass
        for ix in range(nrChildren):
            self.Item(ix).GetCell(1).SetBgCol(PROPERTY_STANDARD_COLOUR)

    def setCellBgColNoEdit(self):
        self.GetCell(1).SetBgCol(PROPERTY_NO_EDIT_COLOUR)
        Utils.queueFunctionCall(self.whitenChildren)

_LOGICAL_VALUES = ["FALSE", "TRUE"]
class LogicalProperty(wxpg.EnumProperty):
    def __init__(self, label, name, value):
        internalValue = self.StringToValue(value)
        #wxpg.EnumProperty.__init__(self, label, name, _LOGICAL_VALUES, [0,1], _LOGICAL_VALUES.index(internalValue))
        wxpg.EnumProperty.__init__(self, label, name, _LOGICAL_VALUES, [0, 1], internalValue)

    def StringToValue(self, text, argFlags=0):
        internalValue = 0
        if text.upper() == _LOGICAL_VALUES[1]:
            internalValue = 1
        return internalValue

    def ValueToString(self, internalValue, argFlags=0):
        if isinstance(internalValue, str):
            valueStr = internalValue
        else:
            if internalValue < 0 or internalValue > 1:
                internalValue = 0
            valueStr = _LOGICAL_VALUES[internalValue]
        return valueStr

class FlagsProperty(wxpg.FlagsProperty):
    def __init__(self, label, name, itemNamesArray, choiceBitsArray, valueBits):
        wxpg.FlagsProperty.__init__(self, label, name)
        self.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)
        self.SetChoices(wxpg.PGChoices(itemNamesArray, choiceBitsArray))
        self.SetValue(valueBits)

    def setNameAndValue(self, name, valueBits):
        self.SetName(name)
        self.SetValue(valueBits)

    def setNameChoicesAndValue(self, name, itemNamesArray, choiceBitsArray, valueBits):
        self.SetName(name)
        self.SetChoices(wxpg.PGChoices(itemNamesArray, choiceBitsArray))
        self.SetValue(valueBits)

    def setHelpStrings(self, helpStringsArray):
        nrHelps = len(helpStringsArray)
        nrItems = self.GetItemCount()
        for i in range(min(nrHelps, nrItems)):
            self.Item(i).SetHelpString(helpStringsArray[i])

    def OnEvent(self, propgrid, wnd_primary, event):
        if not self.IsExpanded() and isinstance(event, wx.ChildFocusEvent):
            propgrid.EnsureVisible(self.Item(0))
        return True

def isSmallScreen():
    result = wx.SystemSettings.GetScreenType() <= wx.SYS_SCREEN_PDA
    return result

def getGoodEditorDialogPosition(propGrid, property, dlg):
    splitterX = propGrid.GetSplitterPosition()
    x = splitterX
    y = property.GetY()
    x, y = propGrid.ClientToScreen(x, y)
    dlgSz = dlg.GetSize()
    grdSz = propGrid.GetSize()
    sw = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
    sh = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
    if x > sw/2:
        newX = x + (grdSz.width - splitterX) - dlgSz.x # left
    else:
        newX = x # right
    if y > sh/2:
        newY = y - dlgSz.y # above
    else:
        newY = y + propGrid.GetRowHeight() # below
    return newX, newY
