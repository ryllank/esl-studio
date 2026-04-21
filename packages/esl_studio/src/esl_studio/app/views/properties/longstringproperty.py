#! /usr/bin/python

import wx
import wx.propgrid as wxpg

from .coreproperties import isSmallScreen, getGoodEditorDialogPosition
from ... import utils as Utils
from ..stc import Stc

# Note: A lot of this code taken from wxWidgets src/propgrid/props.cpp (wxLongStringProperty::DisplayEditorDialog) converted, restructured and improved.

class LongStringPropertyDlg(wx.Dialog):

    def __init__(self, property, propGrid, textStr, extn):
        self._property = property
        self._propGrid = propGrid
        self._editor = None
        caption = self._property.dlgTitle
        if not caption:
            caption = self._property.GetLabel()
        style = self._property.dlgStyle
        wx.Dialog.__init__(self, propGrid.GetPanel(), wx.ID_ANY, caption, wx.DefaultPosition, wx.DefaultSize, style) # have to explicitly set position and size later
        self.setup(textStr, extn)

    def setup(self, textStr, extn):
        self.SetFont(self._propGrid.GetFont()) # To allow entering chars of the same set as the propGrid

        # Multi-line text editor dialog.
        spacing = 4 if isSmallScreen() else 8
        topsizer = wx.BoxSizer(wx.VERTICAL)
        rowsizer = wx.BoxSizer(wx.HORIZONTAL)

        # For TextCtrl (not used)
        #edStyle = wx.TE_MULTILINE
        #if self._property.HasFlag(wxpg.PG_PROP_READONLY):
        #    edStyle |= wx.TE_READONLY
        #self._editor = wx.TextCtrl(self, wx.ID_ANY, textStr,
        #           wx.DefaultPosition, wx.DefaultSize, edStyle)
        self._editor = Stc(self)
        self._editor.setStcText(textStr, extn)
        readOnly = False
        if self._property.HasFlag(wxpg.PG_PROP_READONLY):
            readOnly = True
        self._editor.setReadOnly(readOnly)
        rowsizer.Add(self._editor, wx.SizerFlags(1).Expand().Border(wx.ALL, spacing))
        topsizer.Add(rowsizer, wx.SizerFlags(1).Expand())
        btnSizerFlags = wx.CANCEL
        if not self._property.HasFlag(wxpg.PG_PROP_READONLY):
            btnSizerFlags |= wx.OK
        buttonSizer = self.CreateStdDialogButtonSizer(btnSizerFlags)
        topsizer.Add(buttonSizer, wx.SizerFlags(0).Right().Border(wx.BOTTOM | wx.RIGHT, spacing))
        self.SetSizer(topsizer)
        topsizer.SetSizeHints(self)
        position, size = self._property.getDlgGeometry()
        if size == wx.DefaultSize:
            if not isSmallScreen():
                self.SetSize(400, 300)
                self.Move(getGoodEditorDialogPosition(self._propGrid, self._property, self))
        else:
            self.Move(position)
            self.SetSize(size)

    def GetValue(self):
        result = self._editor.GetValue()
        return result

class LongStringProperty(wxpg.LongStringProperty):
    def __init__(self, label, ref, value="", extn=".esl"):
        wxpg.LongStringProperty.__init__(self, label, ref, value=value)
        self.dlgTitle = ""
        self.dlgStyle = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.CLIP_CHILDREN
        self._dlgGeometry = {}
        self._extn = extn

    def setDlgGeometry(self, position, size):
        ref = self.GetName()
        self._dlgGeometry[ref] = (position, size)

    def getDlgGeometry(self):
        ref = self.GetName()
        geometry = self._dlgGeometry.get(ref)
        if geometry is None:
            geometry = (wx.DefaultPosition, wx.DefaultSize)
        return geometry

    def DisplayEditorDialog(self, propGrid, text):
        result = False
        newText = ""
        textStr = Utils.unescapeText(text)
        dlg = LongStringPropertyDlg(self, propGrid, textStr, self._extn)
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            textStr = dlg.GetValue()
            newText = Utils.escapeText(textStr)
            result = True
        self.setDlgGeometry(dlg.GetPosition(), dlg.GetSize())
        dlg.Destroy()
        return result, newText
