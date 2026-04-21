#! /usr/bin/python

import sys

import wx

from .. import auihandler as aui
from .view import View

class MessagesView(View, wx.TextCtrl):
    def __init__(self, parent, viewtype):
        style = wx.TE_READONLY | wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_RICH
        style |= wx.TE_NOHIDESEL # Need this to show selection for Select All on Windows
        wx.TextCtrl.__init__(self, parent, -1, "", wx.Point(0, 0), wx.Size(300, 100), style)
        View.__init__(self, parent, viewtype)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu, self)
        # Copy is automatic (i.e. using built-in handling)
        self.Bind(wx.EVT_MENU, self.DoSelectAll, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.DoClear, id=wx.ID_DELETE)
        if sys.platform == "win32":
            self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("messagesView")
        info.Caption("Messages")
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Bottom()
        return info

    def appendText(self, text):
        pos = self.GetLastPosition()
        self.AppendText(text)
        self.ShowPosition(pos)

    def DoSelectAll(self, evt):
        self.SelectAll()
        pass

    def DoClear(self, evt):
        self.Clear()

    def showContextMenu(self, evt):
        menu = wx.Menu()
        menu.Append(wx.ID_SELECTALL, "Select All")
        menu.Append(wx.ID_COPY, "Copy")
        menu.Append(wx.ID_DELETE, "Clear Messages")
        if self.IsEmpty():
            menu.Enable(wx.ID_SELECTALL, False)
            menu.Enable(wx.ID_DELETE, False)
        if self._mode == "browsing":
            menu.Enable(wx.ID_DELETE, False)
        self.PopupMenu(menu)

    def OnContextMenu(self, evt):
        self.showContextMenu(evt)

    def OnKeyUp(self, evt):
        # This alone seems to stop the wrong context menu popping up in Windows
        pass
