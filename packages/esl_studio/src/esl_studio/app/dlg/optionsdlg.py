#! /usr/bin/python

import os
import sys

import wx
import wx.adv
from wx import xrc
from collections import OrderedDict

from ..config import Config
from .. import utils as Utils
from .profiledlg import ProfileDlg
from ..configupdate import ConfigUpdate

class OptionsDlg(wx.adv.PropertySheetDialog):

    _instance = None

    @classmethod
    def Instance(cls, parent):
        if cls._instance == None:
            cls._instance = cls(parent)
        return cls._instance

    def __init__(self, parent):
        wx.adv.PropertySheetDialog.__init__(self)
        self._parent = parent
        self._configSettings = Config.Settings
        resfile = Utils.resourceFile('optionsdlg.xrc')
        if resfile:
            res = xrc.XmlResource(resfile)
            if res:
                res.LoadObject(self, parent, 'OptionsDlg', 'wxPropertySheetDialog')
                self.setupDlg()
                self.Fit()

    def setupDlg(self):
        self.setFromConfig()
        self.registerEvents()
        # Radio buttons for Diagram/Smart Links
        item = self.FindWindowByName('Diagrams/SmartLink2Segments')
        if item:
            item.SetToolTip('Smart linking with rectilinear 2 segment lines')
        item = self.FindWindowByName('Diagrams/SmartLink3Segments')
        if item:
            item.SetToolTip('Smart linking with rectilinear 3 segment lines')
        item = self.FindWindowByName('Diagrams/SmartLinkStraight')
        if item:
            item.SetToolTip('Smart linking with straight lines')
        # Radio buttons for Advanced/Bleep Sound
        item = self.FindWindowByName('Advanced/BleepBeep')
        if item:
            item.SetToolTip('Use a short Beep sound')
        item = self.FindWindowByName('Advanced/BleepErrorSound')
        if item:
            if sys.platform == 'win32':
                description = 'Use Windows Error sound'
            else:
                description = 'Use a system Error sound (if available)'
            item.SetToolTip(description)
        item = self.FindWindowByName('Advanced/BleepOff')
        if item:
            item.SetToolTip('Don\'t make a sound')

    def setFromConfig(self):
        for path in self._configSettings:
            settingsInfo = self._configSettings[path]
            show = settingsInfo.show
            if path == "General/Splash" and Utils.isFrozen():
                show = False
            item = self.FindWindowByName(path)
            if item:
                if show:
                    value = Config.getValue(path)
                    if isinstance(item, wx.TextCtrl) and not isinstance(item, str):
                        value = str(value)
                    item.SetValue(value)
                    description = settingsInfo.description
                    if description:
                        item.SetToolTip(description)
                else:
                    item.Show(False)
            else:
                if path == 'Diagrams/Smart Links':
                    value = Config.getValue(path)
                    self.setSmartLinksRadioButtons(value)
                elif path == 'Advanced/Bleep Sound':
                    value = Config.getValue(path)
                    self.setBleepSoundRadioButtons(value)

    def registerEvents(self):
        self._btnProfile = self.FindWindowByName("btnProfile")
        if self._btnProfile:
            self._btnProfile.Bind(wx.EVT_BUTTON, self.onProfileClicked, self._btnProfile)
        self._btnDiagramReset = self.FindWindowByName("btnDiagramReset")
        if self._btnDiagramReset:
            self._btnDiagramReset.Bind(wx.EVT_BUTTON, self.onDiagramResetClicked, self._btnDiagramReset)
        self._btnSave = self.FindWindowByName("btnSave")
        if self._btnSave:
            self._btnSave.Bind(wx.EVT_BUTTON, self.onSaveClicked, self._btnSave)
        self._btnLoad = self.FindWindowByName("btnLoad")
        if self._btnLoad:
            self._btnLoad.Bind(wx.EVT_BUTTON, self.onLoadClicked, self._btnLoad)

    def updateConfig(self):
        for path in self._configSettings:
            value = None
            if path == 'Diagrams/Smart Links':
                value = self.getSmartLinksRadioButtonsValue()
            elif path == 'Advanced/Bleep Sound':
                value = self.getBleepSoundRadioButtonsValue()
            else:
                item = self.FindWindowByName(path)
                if item:
                    value = item.GetValue()
            if value is not None:
                Config.setValue(path, value)
        # check if Profile Files need updating too
        configProfileFilesStr = Config.getValue('Profile/Profile Files')
        profileDlg = ProfileDlg.Instance(self)
        profileFiles = profileDlg.getDlgProfileFiles()
        profileFilesStr = Config.PATH_SEPARATOR.join(profileFiles)
        if profileFilesStr != configProfileFilesStr:
            Config.setValue('Profile/Profile Files', profileFilesStr)
            self._parent.commands().reloadProfile() # does full refresh application (if save application not cancelled)
        # Refresh current application view - only for instant change config options
        self.refreshForConfigUpdate()

    def refreshForConfigUpdate(self):
        frame = self._parent
        # General/Show Full Application Path
        applicationTitle = frame.application().filepath()
        if not Config.getBool('General/Show Full Application Path'):
            applicationTitle = os.path.basename(applicationTitle)
        frame.SetTitle(frame._title + ' ' + applicationTitle)
        #### TODO Diagrams/Show Grid,Grid Snap, Smart Link smart2Segments|smart3Segments|Straight - for all diagrams (the BlockDiagramThemePropertyOptions)
        #### TODO ? Views/Properties/Help Views/SimulationParameters/Help & Views/Package/Help for all packages

    def resetFromConfig(self):
        self.setFromConfig()
        self.resetProfileDlgFiles()

    def resetProfileDlgFiles(self):
        # Restore dlg profile files to that of config
        profileDlg = ProfileDlg.Instance(self)
        profileDlg.setProfileFiles()

    def onProfileClicked(self, evt):
        profileDlg = ProfileDlg.Instance(self)
        if profileDlg.ShowModal() == wx.ID_OK:
            self._parent.commands().reloadProfile()
            pass

    def onDiagramResetClicked(self, evt):
        options = Config.getBlockDiagramThemePropertyOptions()
        item = self.FindWindowByName('Diagrams/Show Grid')
        if item:
            item.SetValue(options[0])
        item = self.FindWindowByName('Diagrams/Grid Snap')
        if item:
            item.SetValue(options[1])
        smartLinksDraw = options[2]
        self.setSmartLinksRadioButtons(smartLinksDraw)

    def setSmartLinksRadioButtons(self, smartLinksDraw):
        item = self.FindWindowByName('Diagrams/SmartLink2Segments')
        if item:
            item.SetValue(smartLinksDraw not in ["smart3segments", "straight"]) # unrecognised means smart2segments
        item = self.FindWindowByName('Diagrams/SmartLink3Segments')
        if item:
            item.SetValue(smartLinksDraw == "smart3segments")
        item = self.FindWindowByName('Diagrams/SmartLinkStraight')
        if item:
            item.SetValue(smartLinksDraw == "straight")

    def setBleepSoundRadioButtons(self, bleepSoundOption):
        item = self.FindWindowByName('Advanced/BleepBeep')
        if item:
            item.SetValue(bleepSoundOption == "Bleep sound")
        item = self.FindWindowByName('Advanced/BleepErrorSound')
        if item:
            item.SetValue(bleepSoundOption == "Error sound")
        item = self.FindWindowByName('Advanced/BleepOff')
        if item:
            item.SetValue(bleepSoundOption not in ["Bleep sound", "Error sound"]) # unrecognised means Off

    def getSmartLinksRadioButtonsValue(self):
        value = None
        item = self.FindWindowByName('Diagrams/SmartLink2Segments')
        if item and item.GetValue() == True:
            value = 'smart2segments'
        else:
            item = self.FindWindowByName('Diagrams/SmartLink3Segments')
            if item and item.GetValue() == True:
                value = 'smart3segments'
            else:
                item = self.FindWindowByName('Diagrams/SmartLinkStraight')
                if item and item.GetValue() == True:
                    value = 'straight'
        return value

    def getBleepSoundRadioButtonsValue(self):
        value = None
        item = self.FindWindowByName('Advanced/BleepBeep')
        if item and item.GetValue() == True:
            value = 'Beep sound'
        else:
            item = self.FindWindowByName('Advanced/BleepErrorSound')
            if item and item.GetValue() == True:
                value = 'Error sound'
            else:
                item = self.FindWindowByName('Advanced/BleepOff')
                if item and item.GetValue() == True:
                    value = 'Off'
        return value

    def onSaveClicked(self, event):
        wildcard = "Config files (*.ini)|*.ini|"\
                   "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save current dialog configuration settings to a config file",
                    os.getcwd(), "", wildcard,
                    style = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                configPathValues = OrderedDict()
                for path in self._configSettings:
                    if path == 'Diagrams/Smart Links':
                        value = self.getSmartLinksRadioButtonsValue()
                    elif path == 'Advanced/Bleep Sound':
                        value = self.getBleepSoundRadioButtonsValue()
                    else:
                        item = self.FindWindowByName(path)
                        if item:
                            value = item.GetValue()
                        else:  # Also save entries that are not in the dialog (i.e. in the actual config).
                            value = Config.getValue(path)
                    configPathValues[path] = value
                Config.saveConfigFile(ans[0], configPathValues)

    def onLoadClicked(self, event):
        wildcard = "Config files (*.ini)|*.ini|" \
                    "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Load dialog with configuration settings from a config file",
                            os.getcwd(), "", wildcard,
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                rawConfigPathValues = Config.readRawConfigFilePathValues(ans[0])
                if rawConfigPathValues:
                    version = rawConfigPathValues.get("Settings/version")
                    updateLevel = ConfigUpdate.checkForConfigUpdateLevel(version)
                    updatedConfigPathValues = ConfigUpdate.checkForUpdatedConfig(updateLevel, rawConfigPathValues)
                    for path, value in updatedConfigPathValues.items():
                        item = self.FindWindowByName(path)
                        if item:
                            item.SetValue(value)
                            # Note: This does not update the actual config (so can Cancel)
                        elif path == 'Diagrams/Smart Links':
                            self.setSmartLinksRadioButtons(value)
                        elif path == 'Advanced/Bleep Sound':
                            self.setBleepSoundRadioButtons(value)
                        elif path == "Profile/Profile Files": # which is a String
                            profileDlg = ProfileDlg.Instance(self)
                            profileFiles = value.split(Config.PATH_SEPARATOR)
                            profileDlg.updateDlgProfileFiles(profileFiles) # in dlg, not to config
