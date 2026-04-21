#! /usr/bin/python
import re
import sys

import wx

from .. import auihandler as aui
from .view import View

class ValidationView(View, wx.TextCtrl):
    def __init__(self, parent, viewtype, module=None, caption="Validation"):
        style = wx.TE_READONLY | wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_RICH
        style |= wx.TE_NOHIDESEL # Need this to show selection for Select All on Windows
        wx.TextCtrl.__init__(self, parent, -1, "", wx.Point(0, 0), wx.Size(300, 100), style)
        View.__init__(self, parent, viewtype)
        self._frame = wx.GetApp().frame()
        self._module = module
        self._lineColStr = ""
        id = wx.ID_HIGHEST + 11
        self._id_goto = id; id += 1
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu, self)
        self.Bind(wx.EVT_MENU_RANGE, self.onContextMenuItem)
        self.Bind(wx.EVT_MENU, self.DoSelectAll, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_LEFT_DCLICK, self.onLDClick)
        if sys.platform == "win32":
            self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name(self.viewName)
        info.Caption("Validation")
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Dockable(True)
        info.Floatable(True)
        info.Float()
        # Set initial float position over mainview area -
        # and et initial size a bit less (width 90% & height 70%) than mainview area.
        mainViewRect = self._frame.viewManager().mainView().GetScreenRect()
        info.FloatingPosition(wx.Point(mainViewRect.x+mainViewRect.width*6//100, mainViewRect.y+mainViewRect.height*20//100))
        info.FloatingSize(wx.Size(mainViewRect.width*90//100, mainViewRect.height*70//100))
        info.Resizable(True)
        #info.BestSize(wx.Size(200, -1))
        return info

    def setText(self, text):
        self.SetValue(text)

    def getMessageCodeLineCol(self, position, isScreenPosition=True):
        lineColStr = ""
        lineIx = -1
        if position != wx.Point(-1, -1):
            pos = position
            if isScreenPosition:
                pos = self.ScreenToClient(position)
            hitStatus, colIx, rowIx = self.HitTest(pos)
            if hitStatus != wx.TE_HT_UNKNOWN:  # -2
                lineIx = rowIx
        else:
            pos = self.GetInsertionPoint()
            if pos >= 0:
                ok, colIx, rowIx = self.PositionToXY(pos)
                if ok:
                    lineIx = rowIx
            pass
        if lineIx >= 0:
            msg = self.GetLineText(lineIx)
            if msg:
                match = re.search(r" at line (\d+)(\:\d+)?", msg)
                if match:
                    if match[1]:
                        lineColStr = match[1]
                        if match[2]:
                            lineColStr += match[2]
                    pos = self.XYToPosition(0, lineIx)
                    self.SetSelection(pos + match.start() + 1, pos + match.end())
        return lineColStr

    def DoSelectAll(self, evt):
        self.SelectAll()
        pass

    def showContextMenu(self, evt):
        #print("ValidationView.showContextMenu")
        menu = wx.Menu()
        menu.Append(wx.ID_SELECTALL, "Select All")
        menu.Append(wx.ID_COPY, "Copy")
        if self._module and self._module.moduleType() == 'code':
            self._lineColStr = self.getMessageCodeLineCol(evt.GetPosition()) # on screen
            menu.AppendSeparator()
            menu.Append(self._id_goto, "Goto Code Line")
            menu.Enable(self._id_goto, self._lineColStr != "")
        self.PopupMenu(menu)

    def onContextMenuItem(self, event):
        id = event.GetId()
        #print("event id", id)
        if id == self._id_goto:
            self.gotoCodeLineCol(self._lineColStr)
        self._lineColStr = ""

    def gotoCodeLineCol(self, lineColStr):
        if lineColStr:
            if hasattr(self._parent, "gotoLineCol"):
                pageindex = self._frame.viewManager().mainView().GetPageIndex(self._parent)
                if pageindex != wx.NOT_FOUND:
                    self._frame.viewManager().mainView().SetSelection(pageindex)
                    self._parent.gotoLineCol(lineColStr)
                    self._parent.SetFocus()

    def OnContextMenu(self, evt):
        # Problem: When fired on Windows by ContextMenu key gives wrong menu and subsequent exception.
        #print("ValidationView.OnContextMenu")
        self.showContextMenu(evt)

    def onLDClick(self, evt):
        lineColStr = self.getMessageCodeLineCol(evt.GetPosition(), isScreenPosition=False)  # in this window
        if lineColStr:
            self.gotoCodeLineCol(lineColStr)
            evt.Skip(False)
        else:
            evt.Skip(True)

    def OnKeyUp(self, evt):
        # This alone seems to stop the wrong context menu popping up in Windows
        pass
