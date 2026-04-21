#! /usr/bin/python

import sys

import wx
import wx.propgrid as wxpg

import esl_diagram.canvas.colournames as Colours

# Text enter event type found by experiment
if sys.platform == "win32":
    TEXT_ENTER_EVENT_TYPE = 10209
else:
    TEXT_ENTER_EVENT_TYPE = 10127

class ColourProperty(wxpg.ColourProperty):

    TransparentNames = ["none", "clear", "blank", "transparent", "invisible"]

    def __init__(self, label, name, value=None, allowNone=False):
        global _ColourDB_updated
        self._editor = None
        self._allowNone = allowNone
        colourVal = None
        if value is not None:
            colourVal = self.convertToWxColour(value)
        wxpg.ColourProperty.__init__(self, label, name, colourVal)

    def convertToWxColour(self, internalColourStr):
        if self._allowNone and internalColourStr.lower() in ColourProperty.TransparentNames:
            result = Colours.TransparentColour
        else:
            result = Colours.get(internalColourStr)
        return result

    def convertFromWxColour(self, wxColourVal):
        global _ColourRGBsToNamesDict
        result = ""
        if isinstance(wxColourVal, list):
            wxColourVal = wx.Colour(wxColourVal)
        if self._allowNone and wxColourVal == Colours.TransparentColour:
            result = "none"
        else:
            result = Colours.name(wxColourVal)
        return result

    def DoGetEditorClass(self):
        # Determines editor used by property.
        # You can replace 'TextCtrl' below with any of these
        # builtin-in property editor identifiers: Choice, ComboBox,
        # TextCtrlAndButton, ChoiceAndButton, CheckBox, SpinCtrl,
        # DatePickerCtrl.
        editor = wxpg.PGEditor_TextCtrlAndButton
        if self._editor is None:
            self._editor = editor
        return editor

    def OnEvent(self, propgrid, wnd_primary, event):
        res = False
        type = event.GetEventType()
        # TEMP to print (event types for Linux and Windows for excessive events - to see wood from trees).
        #if type != 10001 and type != 10311 and \
        #   type != 10124 and type != 10008:
        #    print(">ColourProperty.OnEvent event=" + str(event)+" type="+str(event.GetEventType()))
        if event.IsCommandEvent():
            type = event.GetEventType()
            if type == wx.wxEVT_COMMAND_BUTTON_CLICKED: # wx.wxEVT_COMBOBOX_DROPDOWN wx.wxEVT_COMBOBOX
                #print("*ColourProperty.OnEvent wxEVT_COMMAND_BUTTON_CLICKED " + str(event)+" type="+str(type))
                data = wx.ColourData()
                data.SetColour(self.m_value)
                data.SetChooseAlpha(False)
                #for Windows ?? - should we save the custom colours
                if sys.platform == 'win32':
                    data.SetChooseFull(True)
                    alpha = wx.ALPHA_OPAQUE
                    for i in range(wx.ColourData.NUM_CUSTOM):
                        n = i*(256//wx.ColourData.NUM_CUSTOM)
                        colour = wx.Colour(n, n, n)#, alpha)
                        data.SetCustomColour(i, colour) # these show as grey palette in Linux (hue & sat are 0) (if dont do these get a random assortment of colours)
                dlg = wx.ColourDialog(propgrid, data)
                ans = dlg.ShowModal()
                if ans == wx.ID_OK:
                    retData = dlg.GetColourData()
                    newValue = retData.GetColour()
                    self.SetValueInEvent(newValue)
                    res = True
            elif type == wx.EVT_TEXT_ENTER or type == TEXT_ENTER_EVENT_TYPE:
                #print("*ColourProperty.OnEvent TEXT_ENTER " + str(event) + " type=" + str(type))
                colourStr = event.GetString()
                colorVal = self.convertToWxColour(colourStr)
                self.SetValueInEvent(colorVal)
        return res

    def setNameAndValue(self, name, value):
        if name:
            self.SetName(name)
        internalValue = self.convertToWxColour(value)
        self.SetValue(internalValue)

    def ValueToString(self, value, argFlags):
        if isinstance(value, list):
            value = wx.Colour(value)
        if isinstance(value, wx.Colour):
            valueStr = self.convertFromWxColour(value)
        else:
            valueStr = str(value)
        return valueStr

    def StringToValue(self, text, argFlags):
        value = self.convertToWxColour(text)
        return (True, value)
