#! /usr/bin/python

import sys
import wx
import wx.propgrid as wxpg

from ... import utils as Utils
from .coreproperties import getGoodEditorDialogPosition

class MultiChoicePropertyButtonEditor(wxpg.PGTextCtrlEditor):

    _editors = {} # register instance of editor for each property grid

    @classmethod
    def SetEditorToProperty(cls, property):
        propertyGrid = property.GetGrid()
        editor = cls._editors.get(propertyGrid)
        if editor is None:
            name = "MultiChoicePropertyButtonEditor"+str(len(cls._editors))
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

        ref = property.GetName()

        buttons.AddBitmapButton(Utils.getButtonBitmap(Utils.buttonIconFile("btnselect")))

        # Create the 'primary' editor control
        wndList = super(MultiChoicePropertyButtonEditor, self).CreateControls(
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
        result = True
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            dlg = wx.MultiChoiceDialog(propGrid, "Make a selection:", property.label, property.choices)
            x, y = getGoodEditorDialogPosition(propGrid, property, dlg)
            dlg.Move(x, y)
            dlg.SetSelections(property.value)
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetSelections()
                property.SetValueInEvent(value)
                property.value = value
        return result

class MultiChoiceProperty(wxpg.PGProperty):
    def __init__(self, label, ref, choices, value):
        self.label = label
        self._ref = ref
        wxpg.PGProperty.__init__(self, label, ref)
        self.choices = choices
        self.setValue(value)
        pass

    def setValue(self, value):
        if len(value) > 0:
            if isinstance(value[0], str):
                self.value = []
                for val in value:
                    if val in self.choices:
                        self.value.append(self.choices.index(val))
            else:
                self.value = value
        else:
            self.value = []
        self.m_value = self.value

    def ValueToString(self, value, argFlags=0):
        valStr = ""
        if value == self.m_value:
            if value != self.value:
                self.value = value
        for item in value:
            if not isinstance(item, str):
                item = self.choices[item]
            if valStr:
                valStr += ", " # note space will need triming
            valStr += item
        return valStr

    def setNameChoicesAndValue(self, name, choices, value):
        self.SetName(name)
        self.choices = choices
        self.setValue(value)
