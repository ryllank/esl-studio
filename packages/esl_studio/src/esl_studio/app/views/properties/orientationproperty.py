#! /usr/bin/python

import wx.propgrid as wxpg

class OrientationProperty(wxpg.EnumProperty):
    # The property value is the str for an Orientation
    OrientationStrings = [
        "normal",
        "rotate90",
        "rotate180",
        "rotate270",
        "mirrorXAxis",
        "mirrorYAxis",
        "mirrorUpDiag",
        "mirrorDownDiag"
    ]
    EnumStrings = [
        "Normal orientation",
        "Left (anticlockwise) 90°",
        "Upside-down 180°",
        "Right (clockwise) 90°",
        "Mirror vertically (about X axis)",
        "Mirror horizontally (about Y axis)",
        "Mirror Top Left (about Up diagonal)",
        "Mirror Top Right (about Down diagonal)"
    ]

    @classmethod
    def GetOrientation(self, internalValue):
        orientationStr = OrientationProperty.OrientationStrings[internalValue]
        return orientationStr

    def __init__(self, label, name, value):
        internalValue = OrientationProperty.OrientationStrings.index(value)
        wxpg.EnumProperty.__init__(self, label, name, OrientationProperty.EnumStrings, list(range(len(OrientationProperty.OrientationStrings))), internalValue)

    def setNameAndValue(self, name, value):
        self.SetName(name)
        ok, internalValue = self.StringToValue(value)
        if ok:
            self.SetValue(internalValue)

    def StringToValue(self, orientationStr, argFlags=0):
        ok = False
        internalValue = None
        if orientationStr in OrientationProperty.OrientationStrings:
            internalValue = OrientationProperty.OrientationStrings.index(orientationStr)
            ok = True
        return ok, internalValue

    def ValueToString(self, internalValue, argFlags=0):
        valueStr = "?"
        if isinstance(internalValue, str):
            if internalValue in OrientationProperty.OrientationStrings:
                internalValue = OrientationProperty.OrientationStrings.index(internalValue)
        if isinstance(internalValue, int):
            valueStr = OrientationProperty.EnumStrings[internalValue]
        return valueStr
