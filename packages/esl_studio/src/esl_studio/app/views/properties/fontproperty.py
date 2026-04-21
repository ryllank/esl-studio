#! /usr/bin/python

import sys

import wx
import wx.propgrid as wxpg

import esl_diagram.canvas.fontwork as Fntwrk

from ... import utils as Utils
from .coreproperties import CompoundProperty

class FontPropertiesButtonEditor(wxpg.PGTextCtrlEditor):

    _editors = {} # register instance of editor for each property grid

    @classmethod
    def SetEditorToProperty(cls, property):
        propertyGrid = property.GetGrid()
        editor = cls._editors.get(propertyGrid)
        if editor is None:
            name = "FontPropertiesButtonEditor"+str(len(cls._editors))
            editor = propertyGrid.RegisterEditor(cls, name)
            cls._editors[propertyGrid] = editor
        property.SetEditor(editor)

    def __init__(self):
        self._buttons = None
        self._propGrid = None
        wxpg.PGTextCtrlEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        self._propGrid = propGrid
        # Create and populate buttons-subwindow
        buttons = wxpg.PGMultiButton(propGrid, sz)

        # Add a bitmap button
        buttons.AddBitmapButton(Utils.getButtonBitmap(Utils.buttonIconFile("btnfont")))

        # Create the 'primary' editor control
        wndList = super(FontPropertiesButtonEditor, self).CreateControls(
           propGrid,
           property,
           pos,
           buttons.GetPrimarySize())

        # Finally, move buttons-subwindow to correct position and make sure
        # returned wxPGWindowList contains our custom button list.
        buttons.Finalize(propGrid, pos)

        self._buttons = buttons

        # Note: For linux prior to v4.1.1 seems we had to boost the button widths (and adjust positions) fully removed.

        wndList.SetSecondary(buttons)
        return wndList

    def OnEvent(self, propGrid, property, ctrl, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            useValue = propGrid.GetUncommittedPropertyValue()
            fontData = wx.FontData()
            fontData.SetInitialFont(useValue)
            fontData.EnableEffects(False)
            dlg = wx.FontDialog(propGrid, fontData)
            if dlg.ShowModal() == wx.ID_OK:
                propGrid.EditorsValueWasModified()
                value = dlg.GetFontData().GetChosenFont()
                property.SetValueInEvent(value)
            result = True
        else:
            result = super(FontPropertiesButtonEditor, self).OnEvent(propGrid, property, ctrl, event)
        return result

class FontProperty(wxpg.PGProperty, CompoundProperty):

    FontStyles = ["Normal", "Italic", "Oblique"]
    FontStyle_values = ["normal", "italic", "oblique"]
    FontStyle_wxValues = [wx.FONTSTYLE_NORMAL, wx.FONTSTYLE_ITALIC, wx.FONTSTYLE_SLANT]
    if sys.platform == "win32":
        # Note that under wxMSW this style [wx.FONTSTYLE_SLANT] is the same as wxFONTSTYLE_ITALIC.
        FontStyles = ["Normal", "Italic"]
        FontStyle_values = ["normal", "italic"]
        FontStyle_wxValues = [wx.FONTSTYLE_NORMAL, wx.FONTSTYLE_ITALIC]
    FontWeights = ["Normal", "Bold", "Lighter"]
    FontWeight_values = ["normal", "bold", "lighter"]
    FontWeight_wxValues = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_BOLD, wx.FONTWEIGHT_LIGHT]
    FontFaces = None

    def __init__(self, view, label, name, value):
        CompoundProperty.__init__(self)
        self._view = view
        self._font = value
        wxpg.PGProperty.__init__(self, label, name)

        prop = wxpg.IntProperty("Point Size", "point")
        prop.SetHelpString("Size of the font in points")
        self.AddPrivateChild(prop) # 0 Point Size

        if FontProperty.FontFaces is None:
            fontEnum = wx.FontEnumerator()
            fontEnum.EnumerateFacenames()
            FontProperty.FontFaces = fontEnum.GetFacenames()
            FontProperty.FontFaces.sort()

        prop = wxpg.EnumProperty("Font Face", "face", wxpg.PGChoices(FontProperty.FontFaces))
        prop.SetHelpString("The font face (or family) name")
        self.AddPrivateChild(prop) # 1 Font Face

        prop = wxpg.EnumProperty("Style", "style", FontProperty.FontStyles, [0, 1, 2])
        help = "Style of font (normal, italic or oblique where applicable)"
        if sys.platform == "win32":
            help = "Style of font (normal or italic (or oblique) where applicable)"
        prop.SetHelpString(help)
        self.AddPrivateChild(prop) # 2 Style

        prop = wxpg.EnumProperty("Weight", "weight", FontProperty.FontWeights, [0, 1, 2])
        prop.SetHelpString("Style of font (normal, bold or lighter where applicable)")
        self.AddPrivateChild(prop) # 3 Weight

        self.setValue(name, self._font)
        self._view.pgm().SetPropertyReadOnly(self, True, wxpg.PG_DONT_RECURSE)

    def setValue(self, name, font):
        if name:
            self.SetName(name)
        self.SetValue(font)
        self._font = font
        self.m_value = self._font  # This fires RefreshChildren

    def ValueToString(self, value, argFlags=0):
        elements = Fntwrk.fontElements(value) # font-size, font-family (or face), font-style, font-weight ] #TODO more (underlined, strikethrough?)
        valueStr = str(elements[0])
        valueStr += "; " + elements[1]
        if elements[2] != "normal":
            valueStr += "; " + elements[2]
        if elements[3] != "normal":
            valueStr += "; " + elements[3]
        return valueStr

    def RefreshChildren(self):
        elements = Fntwrk.fontElements(self.m_value)
        self.Item(0).SetValue(elements[0])
        face = elements[1]
        if face not in FontProperty.FontFaces:
            font = wx.Font(elements[0], wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            face = font.GetFaceName()
        self.Item(1).SetValueFromString(face, wxpg.PG_FULL_VALUE)
        style = elements[2]
        if sys.platform == "win32" and style == "oblique":
            style = "italic"
        self.Item(2).SetValue(FontProperty.FontStyle_values.index(style))
        self.Item(3).SetValue(FontProperty.FontWeight_values.index(elements[3]))
        if face != elements[1]:
            self.setValue(None, font)

    def ChildChanged(self, thisValue, childIndex, childValue):
        if childIndex == 0:
            thisValue.SetPointSize(childValue)
        if childIndex == 1:
            thisValue.SetFaceName(FontProperty.FontFaces[childValue])
        if childIndex == 2:
            thisValue.SetStyle(FontProperty.FontStyle_wxValues[childValue])
        if childIndex == 3:
            thisValue.SetWeight(FontProperty.FontWeight_wxValues[childValue])
        self.setValue(None, thisValue)
        return self._font

    def OnEvent(self, propgrid, wnd_primary, event):
        if not self.IsExpanded() and isinstance(event, wx.ChildFocusEvent):
            propgrid.EnsureVisible(self.Item(0))
        return True
