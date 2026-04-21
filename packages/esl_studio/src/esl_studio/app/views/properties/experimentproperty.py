#! /usr/bin/python

import sys
import copy
import wx
import wx.propgrid as wxpg

from ... import utils as Utils
from .longstringproperty import LongStringProperty

class ExperimentPropertyButtonEditor(wxpg.PGTextCtrlEditor):

    _editors = {} # register instance of editor for each property grid

    @classmethod
    def SetEditorToProperty(cls, property):
        propertyGrid = property.GetGrid()
        editor = cls._editors.get(propertyGrid)
        if editor is None:
            name = "ExperimentPropertyButtonEditor_"+str(len(cls._editors))
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

        buttons.AddBitmapButton(Utils.getButtonBitmap(Utils.buttonIconFile("btnopen")))
        buttons.AddBitmapButton(Utils.getButtonBitmap(Utils.buttonIconFile("btndefault")))

        # Create the 'primary' editor control
        wndList = super(ExperimentPropertyButtonEditor, self).CreateControls(
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
            evtId = event.GetId()
            if evtId == self._buttons.GetButtonId(1):
                priorValue = property.GetValue()
                view = propGrid.GetGrandParent()
                generate = view.frame().control().generate()
                generate.refresh()
                experimentText = generate.generateESLExperiment()
                #property.SetValue(experimentText)
                resultTuple = ExperimentProperty.DisplayEditorDialog(property, propGrid, experimentText)
                result = resultTuple[0]
                if result:
                    resultText = Utils.unescapeText(resultTuple[1])
                    if resultText == experimentText:
                        resultText = ""
                    else:
                        resultText = Utils.escapeText(resultText)
                    if resultText != priorValue:
                        #res = propGrid.SetPropertyValue(wxpg.PGPropArgCls(property), resultText) #-- means that 'old-value' is same as new when set up alterations
                        #res = propGrid.ChangePropertyValue(wxpg.PGPropArgCls(property), resultText) #-- get exception in/after OnPropGridChange
                        property.SetValueInEvent(resultText)
                    else:
                        result = False
            else:
                result = super(ExperimentPropertyButtonEditor, self).OnEvent(propGrid, property, ctrl, event)
        else:
            result = super(ExperimentPropertyButtonEditor, self).OnEvent(propGrid, property, ctrl, event)
        return result

class ExperimentProperty(LongStringProperty):
    def __init__(self, view, label, ref):
        self._view = view
        self._label = label
        self._ref = ref
        LongStringProperty.__init__(self, label, ref)
        pass
