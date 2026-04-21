#! /usr/bin/python

import sys

import wx
from wx import xrc

from .. import utils as Utils
from .. import auihandler as aui
from .view import ModuleView
from ..propertieschangeevent import PropertiesChangeEvent
from ..application.setupinfo import SetupInfoData, SetupExecCommand, SetupTranslationLang

class SetupView(ModuleView, wx.Panel):
    DIRECT_RUN_INFO = "Run simulation directly: Display icons will be generated as PLOT/TABULATE/PREPARE statements. READ statements are not allowed."
    def __init__(self, parent, viewtype):
        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)
        ModuleView.__init__(self, parent, viewtype)
        self._parent = parent
        resfile = Utils.resourceFile("setup.xrc")
        if resfile:
            res = xrc.XmlResource(resfile)
            if res:
                self._innerPanel = res.LoadPanel(self, "SetupPnl") # works - not resizing
                ####res = res.LoadPanel(self, parent, "SetupPnl")
                pass

        self.set_caption("Setup")

        self._innerPanel.Fit()
        self._innerPanel.Layout()
        self.Fit()
        ##self.Bind(wx.EVT_SIZE, self.OnSize)
        self._setupInfoData = SetupInfoData()
        self._oldSetupInfoData = SetupInfoData()
        self._addnlLinkObjsFocus = False
        self._runCommandFocus = False
        self.setup()
        self.detectToCheckSelectedInMainView(self)

    def resetSetupView(self, data=None):
        self._setupInfoData = SetupInfoData()
        self._oldSetupInfoData = SetupInfoData()
        if data is not None:
            self._setupInfoData.copy(data)
            self._oldSetupInfoData.copy(self._setupInfoData)
        self._addnlLinkObjsFocus = False
        self._runCommandFocus = False
        self.updateData(self._setupInfoData)

    ##def OnSize(self, event):
    ##    self._innerPanel.Layout()

    def setMode(self, mode):
        ModuleView.setMode(self, mode)
        self.Enable(mode == "editing") # the easy way

    def defaultPaneInfo(self):
        info = aui.AuiPaneInfo()
        info.Name("SetupView")
        info.Caption("Setup")
        info.MinimizeButton(True)
        info.MaximizeButton(True)
        info.CloseButton(True)
        info.PaneBorder(True)
        info.Right()
        return info

    def setup(self):
        self._sttHeader = xrc.XRCCTRL(self, "sttHeader")
        self._chkGenerateOnly = xrc.XRCCTRL(self, "chkGenerateOnly")
        self._chkViewCode = xrc.XRCCTRL(self, "chkViewCode")
        self._sbxRunArea = xrc.XRCCTRL(self, "sbxRunArea")
        self._chkRunWithSEC = xrc.XRCCTRL(self, "chkRunWithSEC")
        self._sttRunInfo = xrc.XRCCTRL(self, "sttRunInfo")
        self._chcExecCommand = xrc.XRCCTRL(self, "chcExecCommand")
        self._radLangC = xrc.XRCCTRL(self, "radLangC")
        self._radLangFortran = xrc.XRCCTRL(self, "radLangFortran")
        self._chkSingle = xrc.XRCCTRL(self, "chkSingle")
        self._chk32bit = xrc.XRCCTRL(self, "chk32bit")
        self._chkGcc = xrc.XRCCTRL(self, "chkGcc")
        self._txtAddnlLinkObjs = xrc.XRCCTRL(self, "txtAddnlLinkObjs")
        self._txtBuildCommand = xrc.XRCCTRL(self, "txtBuildCommand")
        self._sttRunCommand = xrc.XRCCTRL(self, "sttRunCommand") #? do we use this
        self._txtRunCommand = xrc.XRCCTRL(self, "txtRunCommand")
        self.Bind(wx.EVT_CHECKBOX, self.onOptionChanged, self._chkViewCode)
        self.Bind(wx.EVT_CHECKBOX, self.onOptionChanged, self._chkGenerateOnly)
        self.Bind(wx.EVT_CHECKBOX, self.onOptionChanged, self._chkRunWithSEC)
        self.Bind(wx.EVT_CHOICE, self.onExecCommandChanged, self._chcExecCommand)
        self.Bind(wx.EVT_RADIOBUTTON, self.onLangChanged, self._radLangC)
        self.Bind(wx.EVT_RADIOBUTTON, self.onLangChanged, self._radLangFortran)
        self.Bind(wx.EVT_CHECKBOX, self.onExtraOptionChanged, self._chkSingle)
        self.Bind(wx.EVT_CHECKBOX, self.onExtraOptionChanged, self._chk32bit)
        self.Bind(wx.EVT_CHECKBOX, self.onExtraOptionChanged, self._chkGcc)
        self.Bind(wx.EVT_TEXT, self.onAddnlLinkObjsChanged, self._txtAddnlLinkObjs)
        self.Bind(wx.EVT_TEXT_ENTER, self.onAddnlLinkObjsChanged, self._txtAddnlLinkObjs)
        self.Bind(wx.EVT_TEXT, self.onRunCommandChanged, self._txtRunCommand)
        self.Bind(wx.EVT_TEXT_ENTER, self.onRunCommandChanged, self._txtRunCommand)

        if sys.platform != "win32":
            self._chk32bit.Enable(False)
            self._chk32bit.Show(False)
            self._chkGcc.Enable(False)
            self._chkGcc.Show(False)

    def onOptionChanged(self, event):
        self._oldSetupInfoData.copy(self._setupInfoData)
        self._setupInfoData.generateOnly = self._chkGenerateOnly.IsChecked()
        self._setupInfoData.viewCode = self._chkViewCode.IsChecked()
        self._setupInfoData.runWithSEC = self._chkRunWithSEC.IsChecked()
        self.onChange()
        pass

    def onExecCommandChanged(self, event):
        self._oldSetupInfoData.copy(self._setupInfoData)
        execCommandSelected = self._chcExecCommand.GetCurrentSelection()
        if execCommandSelected == 0:
            self._setupInfoData.execCommand = SetupExecCommand.INTERPRET
        elif execCommandSelected == 1:
            self._setupInfoData.execCommand = SetupExecCommand.TRANSLATE
        elif execCommandSelected == 2:
            self._setupInfoData.execCommand = SetupExecCommand.CUSTOM
        self.onChange()
        pass

    def onLangChanged(self, event):
        self._oldSetupInfoData.copy(self._setupInfoData)
        fortran = self._radLangFortran.GetValue()
        if not fortran:
            self._setupInfoData.translation = SetupTranslationLang.CPP
            self._setupInfoData.single = False
        else:
            self._setupInfoData.translation = SetupTranslationLang.FORTRAN
            self._setupInfoData.single = True
        self.onChange()
        pass

    def onExtraOptionChanged(self, event):
        self._oldSetupInfoData.copy(self._setupInfoData)
        self._setupInfoData.single = self._chkSingle.IsChecked()
        self._setupInfoData.x32bit = self._chk32bit.IsChecked()
        self._setupInfoData.gcc = self._chkGcc.IsChecked()
        self.onChange()
        pass

    def onAddnlLinkObjsChanged(self, event):
        self._oldSetupInfoData.copy(self._setupInfoData)
        self._setupInfoData.addnlLinkObjs = self._txtAddnlLinkObjs.GetValue()
        self.onChange()
        pass

    def onRunCommandChanged(self, event):
        self._oldSetupInfoData.copy(self._setupInfoData)
        self._setupInfoData.customRunCommand = self._txtRunCommand.GetValue()
        self.onChange()
        pass

    def onChange(self):
        self._addnlLinkObjsFocus = self._txtAddnlLinkObjs.HasFocus()
        self._runCommandFocus = self._txtRunCommand.HasFocus()
        newValue = SetupInfoData()
        newValue.copy(self._setupInfoData)
        oldValue = SetupInfoData()
        oldValue.copy(self._oldSetupInfoData)
        if newValue != oldValue:
            self.dispatchPropertyChange("setupinfo", "", "", newValue, oldValue)

    def enableWidgets(self):
        run = not self._chkGenerateOnly.IsChecked()
        gotESLSEC = self._parent.frame().control().simulationControl().gotESLSEC()
        useSEC = run and gotESLSEC
        self._chkRunWithSEC.Enable(useSEC)
        infoShown = self._sttRunInfo.IsShown()
        if run and (not useSEC or not self._chkRunWithSEC.IsChecked()):
            self._sttRunInfo.Show(True)
            size = self._sbxRunArea.GetSize()
            self._sttRunInfo.SetLabel(SetupView.DIRECT_RUN_INFO)
            self._sttRunInfo.Wrap(size.Width)
        else:
            self._sttRunInfo.Show(False)
        if infoShown != self._sttRunInfo.IsShown():
            self._innerPanel.Fit()
            self._innerPanel.Layout()
            self.Fit()
        execCommandSelected = self._chcExecCommand.GetCurrentSelection()
        translating = execCommandSelected == 1
        self._radLangC.Enable(translating)
        self._radLangFortran.Enable(translating)
        fortran = self._radLangFortran.GetValue()
        self._chkSingle.Enable(translating and not fortran)
        if sys.platform == "win32":
            self._chk32bit.Enable(translating)
            self._chkGcc.Enable(translating and not fortran)
        self._txtAddnlLinkObjs.SetEditable(translating)
        self._txtRunCommand.SetEditable(execCommandSelected == 2)
        pass

    def dispatchPropertyChange(self, category, propertyId, propertyTag, newValue, oldValue):
        propertieschange_event = PropertiesChangeEvent(category, propertyId,
                                                        propertyTag, newValue, oldValue)
        self._parent.GetEventHandler().AddPendingEvent(propertieschange_event) # see below about AddPendingEvent
        valid = propertieschange_event.IsAllowed()
        return valid

    def updateData(self, data):
        self._setupInfoData.copy(data)

        # Don't trigger changes
        self._chkGenerateOnly.SetValue(self._setupInfoData.generateOnly)
        self._chkViewCode.SetValue(self._setupInfoData.viewCode)
        self._chkRunWithSEC.SetValue(self._setupInfoData.runWithSEC)
        exec = 0
        if self._setupInfoData.execCommand == SetupExecCommand.TRANSLATE: exec = 1
        elif  self._setupInfoData.execCommand == SetupExecCommand.CUSTOM: exec = 2
        self._chcExecCommand.SetSelection(exec)
        fortran = self._setupInfoData.translation == SetupTranslationLang.FORTRAN
        self._radLangC.SetValue(not fortran)
        self._radLangFortran.SetValue(fortran)
        self._chkSingle.SetValue(self._setupInfoData.single)
        self._chk32bit.SetValue(self._setupInfoData.x32bit)
        self._chkGcc.SetValue(self._setupInfoData.gcc)
        self._txtAddnlLinkObjs.ChangeValue(self._setupInfoData.addnlLinkObjs)
        self._txtAddnlLinkObjs.SetInsertionPointEnd()
        if self._addnlLinkObjsFocus:
            self._txtAddnlLinkObjs.SetFocus()
            self._txtAddnlLinkObjs.SelectNone()
        self._txtBuildCommand.ChangeValue(self._setupInfoData.buildCommand())
        self._txtRunCommand.ChangeValue(self._setupInfoData.runCommand())
        self._txtRunCommand.SetInsertionPointEnd()
        if self._runCommandFocus:
            self._txtRunCommand.SetFocus()
            self._txtRunCommand.SelectNone()
        self.enableWidgets()
