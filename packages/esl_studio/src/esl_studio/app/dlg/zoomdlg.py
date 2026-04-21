#! /usr/bin/python

import wx
from wx import xrc

from .. import utils as Utils

class ZoomDlg(wx.Dialog):

    _instance = None

    @classmethod
    def Instance(cls, parent, initScale):
        if cls._instance == None:
            cls._instance = cls(parent)
        cls._instance.setInitScale(initScale)
        return cls._instance

    def __init__(self, parent):
        wx.Dialog.__init__(self)
        self._parent = parent
        resfile = Utils.resourceFile('zoomdlg.xrc')
        if resfile:
            res = xrc.XmlResource(resfile)
            if res:
                res.LoadDialog(self, parent, 'ZoomDlg')
                self.setup()

    def setup(self):
        self._spnZoom = xrc.XRCCTRL(self, 'spnZoom')
        self._spnZoom.SetWindowStyle(wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_SPINCTRL, self.onSpinCtrlChange, self._spnZoom)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSpinCtrlTextEntered, self._spnZoom)
        self._sldZoom = xrc.XRCCTRL(self, 'sldZoom')
        self.Bind(wx.EVT_SLIDER, self.onSliderChange, self._sldZoom)
        self._btnOk = xrc.XRCCTRL(self, "btnOk")
        self.Bind(wx.EVT_BUTTON, self.onOkClicked, self._btnOk)
        self._btnCancel = xrc.XRCCTRL(self, "btnCancel")
        self.Bind(wx.EVT_BUTTON, self.onCancelClicked, self._btnCancel)

    def setInitScale(self, initScale):
        self._initScale = initScale
        scale = round(self._initScale)
        self._spnZoom.SetValue(scale)
        self._sldZoom.SetValue(scale)

    def GetValue(self):
        scale = self._sldZoom.GetValue()
        return scale

    def closeDlg(self):
        self.EndModal(wx.ID_CANCEL)
        return True

    def onOkClicked(self, event):
        self.EndModal(wx.ID_OK)

    def onCancelClicked(self, event):
        self.EndModal(wx.ID_CANCEL)

    def onSliderChange(self, evt):
        scale = self._sldZoom.GetValue()
        if scale != self._spnZoom.GetValue():
            self._spnZoom.SetValue(scale)

    def onSpinCtrlChange(self, evt):
        scale = self._spnZoom.GetValue()
        if scale != self._sldZoom.GetValue():
            self._sldZoom.SetValue(scale)

    def onSpinCtrlTextEntered(self, evt):
        self.onSpinCtrlChange(evt)
