#! /usr/bin/python

import copy
import wx
import wx.propgrid as wxpg

from ...application.displaydefinition import PlotAxis
from .coreproperties import CompoundProperty

class PlotAxisProperty(wxpg.PGProperty, CompoundProperty):

    OriginTexts = ["Auto", "Zero", "Min", "Max"]

    def __init__(self, view, propertyName, varRef="", plotAxis=None):
        CompoundProperty.__init__(self)
        self._view = view
        self._varRef = varRef
        if plotAxis:
            self._plotAxis = copy.copy(plotAxis)
        else:
            self._plotAxis = PlotAxis()
        wxpg.PGProperty.__init__(self, propertyName, varRef)
        """
            min                 min             min=<min>           | * 0.0 is default - used when auto-scale
            max                 max             max=<max>           | * 0.0 is default - used when auto-scale
            divs                divs            divs=<n-divisions>  | * 0 is default
            origin              origin          origin=             | "auto"(default) | "zero" | "min" | "max"
            autoScale           Auto Scaling    auto-scale=         | "true"(default) | "false"    
            log                 Logarithmic     log=                | "true" | "false"(default)           
            grid                Display Grid    grid=               | "true" | "false"(default)          
        """
        self._min = wxpg.FloatProperty("Min", "min")
        self._min.SetHelpString("Minimum value for the plot axis")
        self.AddPrivateChild(self._min) #0

        self._max = wxpg.FloatProperty("Max", "max")
        self._max.SetHelpString("Maximum value for the plot axis")
        self.AddPrivateChild(self._max) #1

        self._divs = wxpg.IntProperty("Divs", "divs")
        self._divs.SetHelpString("Number of divisions for the plot axis")
        self.AddPrivateChild(self._divs) #2

        self._origin = wxpg.EnumProperty("Axis Origin", 'origin', PlotAxisProperty.OriginTexts,
                                            [0, 1, 2, 3])
        self._origin.SetHelpString("Automatically pick where this axis intersects other axis, or set at zero (if available), or set at max or min of other axis.")
        self.AddPrivateChild(self._origin) #3

        self._autoScale = wxpg.BoolProperty("Auto Scaling", 'autoScale')
        self._autoScale.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)
        self._autoScale.SetHelpString("Automatically scale axis, else fix between min and max settings (if set).")
        self.AddPrivateChild(self._autoScale) #4

        self._log = wxpg.BoolProperty("Logarithmic", 'log')
        self._log.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)
        self._log.SetHelpString("Show values scaled logarithmically (if value range appropriate - positive), else linear.")
        self.AddPrivateChild(self._log) #5

        self._grid = wxpg.BoolProperty("Display Grid", 'grid')
        self._grid.SetAttribute(wxpg.PG_BOOL_USE_CHECKBOX, True)
        self._grid.SetHelpString("Show grid lines for this axis.")
        self.AddPrivateChild(self._grid) #6

        self.m_value = "" # This fires RefreshChildren
        self._view.pgm().SetPropertyReadOnly(self, True, wxpg.PG_DONT_RECURSE)

    def setAxis(self, varRef, plotAxis):
        self._varRef = varRef
        self.SetName(varRef)
        self._plotAxis = copy.copy(plotAxis)
        self._min.SetValue(float(self._plotAxis.min))
        self._max.SetValue(float(self._plotAxis.max))
        self._divs.SetValue(int(self._plotAxis.divs))
        self._origin.SetValue(PlotAxis.Origin_values.index(self._plotAxis.origin))
        self._autoScale.SetValue(self._plotAxis.autoScale)
        self._log.SetValue(self._plotAxis.log)
        self._grid.SetValue(self._plotAxis.grid)

    def priorPropertyValue(self):
        return self._priorPropertyValue

    def propertyValue(self):
        result = self._plotAxis.save(None, 0, True)
        return result

    def updateFields(self, propertyValue):
        self._plotAxis.loadData(propertyValue)
        self.RefreshChildren()

    def ValueToString(self, value, flags):
        valStr = ""
        return valStr

    def RefreshChildren(self):
        self.Item(0).SetValue(float(self._plotAxis.min))
        self.Item(1).SetValue(float(self._plotAxis.max))
        self.Item(2).SetValue(int(self._plotAxis.divs))
        self.Item(3).SetValue(PlotAxis.Origin_values.index(self._plotAxis.origin))
        self.Item(4).SetValue(self._plotAxis.autoScale)
        self.Item(5).SetValue(self._plotAxis.log)
        self.Item(6).SetValue(self._plotAxis.grid)

    def ChildChanged(self, thisValue, childIndex, childValue):
        self._priorPropertyValue = self.propertyValue()
        if childIndex == 0:
            self._plotAxis.min = childValue
        elif childIndex == 1:
            self._plotAxis.max = childValue
        elif childIndex == 2:
            self._plotAxis.divs = childValue
        elif childIndex == 3:
            self._plotAxis.origin = PlotAxis.Origin_values[childValue]
        elif childIndex == 4:
            self._plotAxis.autoScale = childValue
        elif childIndex == 5:
            self._plotAxis.log = childValue
        elif childIndex == 6:
            self._plotAxis.grid = childValue
        return None

    def OnEvent(self, propgrid, wnd_primary, event):
        if not self.IsExpanded() and isinstance(event, wx.ChildFocusEvent):
            propgrid.EnsureVisible(self.Item(0))
        return True
