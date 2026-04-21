#! /usr/bin/python

import sys
import copy
import wx
import wx.propgrid as wxpg

from ... import utils as Utils
from .coreproperties import CompoundProperty
from ...esl.esl import EslBaseTypeNames
from ..properties.eslvaluestrproperty import ESLValueStrProperty, ESLValueStrPropertyButtonEditor

DATATYPES = list(map(lambda item: item.title(), EslBaseTypeNames))  # = ['Real', 'Integer', 'Logical']
VARIABLEKINDS = ['Parameter', 'Constant', 'Variable']

# Test for buttons in property lines
class VariablePropertiesButtonEditor(wxpg.PGTextCtrlEditor):

    _editors = {} # register instance of editor for each property grid

    @classmethod
    def SetEditorToProperty(cls, property):
        propertyGrid = property.GetGrid()
        editor = cls._editors.get(propertyGrid)
        if editor is None:
            name = "VariablePropertiesButtonEditor_"+str(len(cls._editors))
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

        isLast = property.getIsLastVariable()

        # Add a bitmap button
        buttons.AddBitmapButton(Utils.getButtonBitmap(Utils.buttonIconFile("btnminus")))

        if isLast:
            buttons.AddBitmapButton(Utils.getButtonBitmap(Utils.buttonIconFile("btnplus")))

        # Create the 'primary' editor control
        wndList = super(VariablePropertiesButtonEditor, self).CreateControls(
           propGrid,
           property,
           pos,
           buttons.GetPrimarySize())

        # Finally, move buttons-subwindow to correct position and make sure
        # returned wxPGWindowList contains our custom button list.
        buttons.Finalize(propGrid, pos)

        # We must maintain a reference to any editor objects we created
        # ourselves. Otherwise they might be freed prematurely. Also,
        # we need it in OnEvent() below, because in Python we cannot "cast"
        # result of wxPropertyGrid.GetEditorControlSecondary() into
        # PGMultiButton instance.
        self._buttons = buttons

        # Note: For linux prior to v4.1.1 seems we had to boost the button widths (and adjust positions) fully removed.

        wndList.SetSecondary(buttons)
        return wndList

    def OnEvent(self, propGrid, property, ctrl, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            buttons = self._buttons
            evtId = event.GetId()
            view = None
            view = propGrid.GetGrandParent()
            if view:
                if evtId == buttons.GetButtonId(0): # remove
                    # Do something when the first button is pressed
                    view.removeVariable(property)
                    return False  # Return false since value did not change
                if evtId == buttons.GetButtonId(1): # add
                    # Do something when the second button is pressed
                    view.newVariable()
                    return False  # Return false since value did not change

        return super(VariablePropertiesButtonEditor, self).OnEvent(propGrid, property, ctrl, event)

class VariableProperty(wxpg.PGProperty, CompoundProperty):
    def __init__(self, view, varRef, variable):
        CompoundProperty.__init__(self)
        self._view = view
        self._varRef = varRef
        self._variable = variable.detachedCopy(variable.parent())
        wxpg.PGProperty.__init__(self, variable.eslname(), varRef)
        self.kind = VARIABLEKINDS[2]
        if variable.parameter() == 'true': self.kind = VARIABLEKINDS[0]
        if variable.constant() == 'true': self.kind = VARIABLEKINDS[1]

        prop = wxpg.StringProperty("ESL Name", 'eslname', value=variable.eslname())
        prop.SetHelpString("An ESL identifier (A..Z 0..9 _) for the variable.\nThe ESL Name must be unique (in 28chars) in its scope (package, model, submodel).")
        self.AddPrivateChild(prop)

        prop = wxpg.StringProperty("Description", 'description', value=variable.description())
        prop.SetHelpString("Description (not used in generated ESL).")
        self.AddPrivateChild(prop)

        prop = wxpg.EnumProperty("Data Type", "datatype", DATATYPES, [0,1,2], DATATYPES.index(variable.datatype()))
        prop.SetHelpString("ESL data type for the variable.")
        self.AddPrivateChild(prop)

        idx = 2
        if variable.parameter() == 'true': idx = 0
        if variable.constant() == 'true': idx = 1
        prop = wxpg.EnumProperty("Kind of Variable", "kind", VARIABLEKINDS, [0,1,2], idx)
        prop.SetHelpString("Parameter - value can be set interactively but is not changed by simulation.\nVariable - value can change during simulation run.\nConstant - value fixed here.")
        self.AddPrivateChild(prop)

        prop = wxpg.StringProperty("Dimensions", 'dimensions', value=variable.dimensions())
        prop.SetHelpString("For ESL Array or Matrix - blank for Scalar\nFor each dimension (up to 3) can optionally set lower bound and must set an upper bound.\nExamples: 3,3 0..2,7..9,-1..1")
        self.AddPrivateChild(prop)

        prop = ESLValueStrProperty("Value", 'value', eslValue=variable.eslValue(), \
           helpString="Initial value for a variable\nFor an Array/Matrix, scalar elements separated by commas, must have the full number of elements.\n"+
                      "For a 2D/3D Matrix you may enclose in square brackets for row-major order (the default), or specifically enclose with slashes for column-major order.")
        self.AddPrivateChild(prop)
        propertyGrid = self._view.pgm().GetGrid()
        ESLValueStrPropertyButtonEditor.SetEditorToProperty(prop, propertyGrid)

        self.m_value = self.ValueToString(None, None)

        self._childIndexChanged = -1
        self._priorPropertyValue = self.propertyValue()

        self._view.pgm().SetPropertyReadOnly(self, True, wxpg.PG_DONT_RECURSE)
        self.setCellBgColNoEdit()

    def varRef(self):
        return self._varRef

    def variable(self):
        return self._variable

    def setVariableProperty(self, varRef, variable):
        self._varRef = varRef
        self.SetName(varRef)
        self._variable = variable.detachedCopy(variable.parent())
        self.SetLabel(variable.eslname())
        self._priorPropertyValue = self.propertyValue()
        self.RefreshChildren()

    def getIsLastVariable(self):
        return self._view.getIsLastVariable(self)

    def childIndexChanged(self):
        return self._childIndexChanged

    def priorPropertyValue(self):
        return self._priorPropertyValue

    def propertyValue(self):
        result = self._variable.save(None, 0, True)
        return result

    def updateFields(self, propertyValue):
        self._variable.loadData(propertyValue)
        self.RefreshChildren()
        pass

    def GetClassName(self):
        return self.__class__.__name__

    def ValueToString(self, value, flags):
        valStr = wx.GetApp().frame().control().generate().generateVariableDeclaration(self._variable, False)
        return valStr

    def RefreshChildren(self):
        self.Item(0).SetValue(self._variable.eslname())
        self.Item(1).SetValue(self._variable.description())
        self.Item(2).SetValue(DATATYPES.index(self._variable.datatype()))
        self.Item(3).SetValue(VARIABLEKINDS.index(self.kind))
        self._variable.set_parameter('true' if self.kind == VARIABLEKINDS[0] else 'false')
        self._variable.set_constant('true' if self.kind == VARIABLEKINDS[1] else 'false')
        self.Item(4).SetValue(self._variable.dimensions())
        self.Item(5).SetValue(self._variable.eslValue())

    def ChildChanged(self, thisValue, childIndex, childValue):
        self._priorPropertyValue = self.propertyValue()
        self._childIndexChanged = childIndex
        if childIndex == 0:
            self._variable.set_eslname(childValue)
        elif childIndex == 1:
            self._variable.set_description(childValue)
        elif childIndex == 2:
            self._variable.set_datatype(DATATYPES[childValue])
        if childIndex == 3:
            self.kind = VARIABLEKINDS[childValue]
            self._variable.set_parameter('true' if self.kind == VARIABLEKINDS[0] else 'false')
            self._variable.set_constant('true' if self.kind == VARIABLEKINDS[1] else 'false')
        if childIndex == 4:
            self._variable.set_dimensions(childValue)
        if childIndex == 5:
            self._variable.eslValue().loadStr(childValue, checkValidity=False)
        if childIndex in [ 2, 4, 5 ]:
            self.Item(5).checkShowFeatures()
        return None

    def checkValueShowFeatures(self):
        self.Item(5).checkShowFeatures()

    def OnEvent(self, propgrid, wnd_primary, event):
        if not self.IsExpanded() and isinstance(event, wx.ChildFocusEvent):
            eventObject = event.GetEventObject()
            if isinstance(eventObject, wx.TextCtrl):
                propgrid.EnsureVisible(self.Item(0))
        return True
