#! /usr/bin/python

import wx
import wx.propgrid as wxpg

from .coreproperties import CompoundProperty
from .spinproperty import SpinProperty

class ScaleProperty(wxpg.PGProperty, CompoundProperty): # use PGProperty when do children
    ScaleXLabelSync = "Scale (%)"
    ScaleXLabelNotSync = "Scale Width (%)"
    def __init__(self, view, label, name, value):
        CompoundProperty.__init__(self)
        self._view = view
        self._scale = value # string for scale (float) or comma separated 2 floats

        wxpg.PGProperty.__init__(self, label, name)

        sync, x, y = self.extractChildValues()
        self._last_sync = sync

        self._sync = wxpg.BoolProperty("Sync", 'sync', value=sync)
        self._sync.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)
        self._sync.SetHelpString("Synchronise width and height scale to preserve shape")
        self.AddPrivateChild(self._sync) #0

        scale_x_label = ScaleProperty.ScaleXLabelSync if sync else ScaleProperty.ScaleXLabelNotSync
        self._scale_x = SpinProperty(scale_x_label, "scale-x", value=round(x*100), min=5, max=400)
        self._scale_x.SetHelpString("Scale both width and height when synchronised, or scale for width (in X direction) for normal orientation (5-400%)")
        self.AddPrivateChild(self._scale_x) #1

        self._scale_y = SpinProperty("Scale Height (%)", "scale-y", value=round(y*100), min=5, max=400)
        self._scale_y.SetHelpString("Scale for height (in Y direction) for normal orientation (5-400%)")
        self.AddPrivateChild(self._scale_y) #2
        self._scale_y.Hide(sync)

        self.setValue(name, self._scale)
        self._view.pgm().SetPropertyReadOnly(self, True, wxpg.PG_DONT_RECURSE)
        self.setCellBgColNoEdit()

    def extractChildValues(self):
        sync = False
        x = 1.0
        y = 1.0
        scaleElements = self._scale.split(",")
        if len(scaleElements) == 1:
            sync = True
            x = float(scaleElements[0])
            y = x
        elif len(scaleElements) == 2:
            x = float(scaleElements[0])
            y = float(scaleElements[1])
        return sync, x, y

    def setValue(self, name, value):  # string of 2 comma separated floats
        if name:
            self.SetName(name)
        self._scale = value
        self.SetValue(self._scale)  # This fires RefreshChildren

    def GetValue(self):
        return self._scale

    def ValueToString(self, value, argFlags=0):
        valueStr = "1.0, 1.0"
        if value:
            valueStr = value
            valueElements = value.split(",")
            if len(valueElements) == 2:
                valueStr = str(valueElements[0])
                valueStr += ", " + str(valueElements[1])
        return valueStr

    def StringToValue(self, valueStr, argFlags=0):
        valueElements = valueStr.split(",")
        if len(valueElements) == 2:
            value = str(valueElements[0])
            value += "," + str(valueElements[1])
        else:
            value = "1.0,1.0"
        return value

    def updatePropertiesForSyncChange(self, sync):
        if sync != self._last_sync:
            scale_x_label = ScaleProperty.ScaleXLabelSync if sync else ScaleProperty.ScaleXLabelNotSync
            self._scale_x.SetLabel(scale_x_label)
            self._scale_y.Hide(sync)
            self._last_sync = sync

    def RefreshChildren(self):
        sync, x, y = self.extractChildValues()
        self.Item(0).SetValue(sync)
        self.Item(1).SetValue(round(100*x))
        if sync:
            y = x
        self.Item(2).SetValue(round(100*y))
        self.updatePropertiesForSyncChange(sync)

    def ChildChanged(self, thisValue, childIndex, childValue):
        sync, x, y = self.extractChildValues()
        if childIndex == 0:
            sync = childValue
        if childIndex == 1:
            x = str(childValue/100)
        if childIndex == 2:
            y = str(childValue/100)
        if childIndex == 0: # handle sync change
            if sync:
                y = x
            self.updatePropertiesForSyncChange(sync)
        # reconstruct value from children
        value = str(x)
        if not sync:
            value += "," + str(y)
        self._scale = value
        return self._scale

    def OnEvent(self, propgrid, wnd_primary, event):
        if not self.IsExpanded() and isinstance(event, wx.ChildFocusEvent):
            propgrid.EnsureVisible(self.Item(0))
        return True
