#! /usr/bin/python

import wx.propgrid as wxpg

class SpinProperty(wxpg.IntProperty):
    def __init__(self, label, name, value=100, min=0, max=1000):
        wxpg.IntProperty.__init__(self, label, name)
        self._min = min
        self._max = max
        self.m_value = value

    def DoGetEditorClass(self):
        self._got_editor = wxpg.PropertyGridInterface.GetEditorByName("SpinCtrl")
        return self._got_editor

    def ValueToString(self, value, argFlags=0):
        if value < self._min:
            value = self._min
        if value > self._max:
            value = self._max
        valueStr = str(value)
        return str(valueStr)

    def StringToValue(self, strng, argFlags=0):
        ok = False
        value = None
        try:
            value = int(strng)
            ok = True
        except (ValueError, TypeError):
            pass
        except:
            raise
        return ok, value
