#! /usr/bin/python

import copy

import wx
import wx.propgrid as wxpg

from ... import utils as Utils
from .coreproperties import PROPERTY_STANDARD_COLOUR, PROPERTY_DEFAULT_COLOUR, PROPERTY_ALERT_COLOUR, PROPERTY_UNCHECKED_COLOUR
from ...application.eslvalue import ESLValue

class ESLValueStrPropertyButtonEditor(wxpg.PGTextCtrlEditor):

    _editors = {} # register instance of editor for each property grid

    @classmethod
    def SetEditorToProperty(cls, property, propertyGrid):
        editor = cls._editors.get(propertyGrid)
        if editor is None:
            name = "ESLValueStrPropertyButtonEditor"+str(len(cls._editors))
            editor = propertyGrid.RegisterEditor(cls, name)
            cls._editors[propertyGrid] = editor
        property.SetEditor(editor)

    def __init__(self):
        self._buttons = None
        self._propGrid = None
        self._buttonMode = ""
        wxpg.PGTextCtrlEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        self._propGrid = propGrid
        # Create and populate buttons-subwindow
        buttons = wxpg.PGMultiButton(propGrid, sz)

        ref = property.GetName()

        self._onBitmap = Utils.getButtonBitmap(Utils.buttonIconFile("tick"))
        self._offBitmap = Utils.getButtonBitmap(Utils.buttonIconFile("not-tick"))

        self._buttonMode = property.mode()
        if property.mode() == 'check':
            bitmap = self._onBitmap
        else:
            bitmap = self._offBitmap
        buttons.AddBitmapButton(bitmap)

        # Create the 'primary' editor control
        wndList = super(ESLValueStrPropertyButtonEditor, self).CreateControls(
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
        #print("ESLValueStrPropertyButtonEditor.CreateControls")
        return wndList

    def setButtonMode(self, mode):
        if self._buttons:
            if mode != self._buttonMode:
                button = self._buttons.GetButton(0)
                if mode == 'check':
                    button.SetBitmap(self._onBitmap)
                else:
                    button.SetBitmap(self._offBitmap)
                self._buttonMode = mode

    def OnEvent(self, propGrid, property, ctrl, event):
        result = False
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            currentMode = property.mode()
            propertyValueStr = property.GetValue()
            if currentMode == 'check':  # Toggle mode but not in the property itself
                mode = 'raw'
            else:
                mode = 'check'
            self.setButtonMode(mode)
            propertyValueStr = propertyValueStr.replace("|"+currentMode+"|", "|"+mode+"|")
            if mode == 'raw':
                if propertyValueStr.startswith("{valid|"):
                    propertyValueStr = propertyValueStr.replace("{valid|", "{unchecked|")
            property.SetValueInEvent(propertyValueStr)
            result = True # ? it doesn't seem to matter if this left False or not ?
        else:
            result = super(ESLValueStrPropertyButtonEditor, self).OnEvent(propGrid, property, ctrl, event)
        return result

    def  UpdateControl(self, property, ctrl):
        mode = property.mode()
        self.setButtonMode(mode)
        super(ESLValueStrPropertyButtonEditor, self).UpdateControl(property, ctrl)

class ESLValueStrProperty(wxpg.StringProperty):

    InvalidValueHelpAddition = "The value has been validity checked and found invalid (shown with an exclamation mark)."
    UncheckedValueHelpAddition = "The value has not been validity checked (shown with a question mark) and may be invalid."
    DefaultValueHelpAddition = "As no explicit value is given the default value for this property (shown with an asterisk) will be generated."

    def __init__(self, label, name, eslValue, helpString=""):
        self._label = label
        self._helpString = helpString
        self._eslValue = eslValue.detachedCopy(None)
        wxpg.StringProperty.__init__(self, label, name, self._eslValue.saveStr())

    def eslValue(self):
        return self._eslValue

    def ValueToString(self, value, argFlags=0): # returns string for display (i.e. valueStr, not the internal string i.e. saveStr)
        displayStr = ""
        if value is not None:
            if isinstance(value, ESLValue):
                displayStr = value.valueStr()
                defaultStr = value.defaultValueStr()
            elif isinstance(value, str):
                dummyESLValue = self._eslValue.detachedCopy(None)
                dummyESLValue.loadStr(value, checkValidity=False)
                displayStr = dummyESLValue.valueStr()
                defaultStr = dummyESLValue.defaultValueStr()
            else:
                raise Exception("ESLValueStrProperty.ValueToString expecting value to be a string or ESLValue - got "+str(type(value)))
            if not displayStr and defaultStr:
                displayStr = defaultStr
        return displayStr

    def StringToValue(self, text, argFlags=0): # returns an internal string for the property (which it does NOT set (i.e. saveStr)
        ok = True
        dummyESLValue = self._eslValue.detachedCopy(None)
        if text and text.startswith("{"): # full saveStr
            dummyESLValue.loadStr(text, checkValidity=True)
        else: # just the valueStr
            if text == dummyESLValue.defaultValueStr():
                text = ""
            dummyESLValue.set_valueStr(text)
        strValue = dummyESLValue.saveStr()
        return ok, strValue

    def SetValue(self, value, pList=None, flags=None):
        strValue = ""
        eslValue = None
        if isinstance(value, ESLValue):
            strValue = value.saveStr()
            self._eslValue = value
        elif isinstance(value, str):
            strValue = value
            self._eslValue.loadStr(strValue)
        else:
            raise Exception("ESLValueStrProperty.SetValue expecting value to be a string or ESLValue - got "+str(type(value)))
        pass

        super(ESLValueStrProperty, self).SetValue(strValue)
        self.checkShowFeatures()

    def valueStr(self):
        return self._eslValue.valueStr()

    def mode(self):
        return self._eslValue.mode()
    def set_mode(self, mode):
        self._eslValue.set_mode(mode)
    def validity(self):
        return self._eslValue.validity()
    def set_validity(self, validity):
        self._eslValue.set_validity(validity)

    def helpString(self):
        return self._helpString

    def SetHelpString(self, helpString):
        self._helpString = helpString
        #super(ESLValueStrProperty, self).SetHelpString(helpString) - happens later in checkShowFeatures

    def checkShowFeatures(self):
        label = self._label
        helpString = self._helpString
        priorLabel = self.GetLabel()
        bgColour = PROPERTY_STANDARD_COLOUR
        if self._eslValue.validity() == 'invalid':
            bgColour = PROPERTY_ALERT_COLOUR
            label += " !"
            if helpString: helpString += "\n"
            helpString += ESLValueStrProperty.InvalidValueHelpAddition
            validityMsg = self._eslValue.validityMsg()
            if validityMsg:
                helpString += "\n" + validityMsg
        elif self._eslValue.defaultValueStr() and not self._eslValue.valueStr():
            bgColour = PROPERTY_DEFAULT_COLOUR
            label += " *"
            if helpString: helpString += "\n"
            helpString += ESLValueStrProperty.DefaultValueHelpAddition
        elif self._eslValue.validity() == 'unchecked':
            bgColour = PROPERTY_UNCHECKED_COLOUR
            label += " ?"
            if helpString: helpString += "\n"
            helpString += ESLValueStrProperty.UncheckedValueHelpAddition
        self.GetCell(0).SetBgCol(bgColour)
        self.GetCell(1).SetBgCol(bgColour)
        self.SetLabel(label)
        super(ESLValueStrProperty, self).SetHelpString(helpString)
        #print("<ESLValueStrProperty.checkShowFeatures label="+label+" priorLabel="+priorLabel+" changed="+str(bool(label != priorLabel)))
        if label != priorLabel:
            grid = self.GetGrid()
            if grid:
                grid.RefreshProperty(self)
                pass
            pass
        self.RefreshEditor()
