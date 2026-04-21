#! /usr/bin/python

import os.path
import wx
from wx import xrc

from ..general import APP_NAME, PROFILE_FILE_EXT, PROFILE_DEFAULT_DIR
from .. import utils as Utils
from ..config import Config
from ..profile import Profile

class ProfileDlg(wx.Dialog):

    _instance = None

    @classmethod
    def Instance(cls, parent):
        if cls._instance == None:
            cls._instance = cls(parent)
            cls._instance.setProfileFiles()
        return cls._instance

    def __init__(self, parent):
        wx.Dialog.__init__(self)
        self._parent = parent
        resfile = Utils.resourceFile('profiledlg.xrc')
        if resfile:
            res = xrc.XmlResource(resfile)
            if res:
                res.LoadDialog(self, parent, 'ProfileDlg')
                self.setup()

    def setup(self):
        self._lbxAvailableFiles = xrc.XRCCTRL(self, 'lbxAvailableFiles')
        self.Bind(wx.EVT_LISTBOX, self.onAvailableFilesChanged, self._lbxAvailableFiles)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onAvailableFilesDClicked, self._lbxAvailableFiles)
        self._lbxProfileFiles = xrc.XRCCTRL(self, 'lbxProfileFiles')
        self.Bind(wx.EVT_LISTBOX, self.onProfileFilesChanged, self._lbxProfileFiles)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onProfileFilesDClicked, self._lbxProfileFiles)
        self._btnSave = xrc.XRCCTRL(self, "btnSave")
        self.Bind(wx.EVT_BUTTON, self.onSaveClicked, self._btnSave)
        self._btnLoad = xrc.XRCCTRL(self, "btnLoad")
        self.Bind(wx.EVT_BUTTON, self.onLoadClicked, self._btnLoad)
        self._btnAdd = xrc.XRCCTRL(self, "btnAdd")
        self.Bind(wx.EVT_BUTTON, self.onAddClicked, self._btnAdd)
        self._btnAdd.Enable(False)
        self._btnView = xrc.XRCCTRL(self, "btnView")
        self.Bind(wx.EVT_BUTTON, self.onViewClicked, self._btnView)
        self._btnView.Enable(False)
        self._btnRemove = xrc.XRCCTRL(self, "btnRemove")
        self.Bind(wx.EVT_BUTTON, self.onRemoveClicked, self._btnRemove)
        self._btnRemove.Enable(False)
        self._btnReset = xrc.XRCCTRL(self, "btnReset")
        self.Bind(wx.EVT_BUTTON, self.onResetClicked, self._btnReset)
        self._btnUp = xrc.XRCCTRL(self, "btnUp")
        self.Bind(wx.EVT_BUTTON, self.onUpClicked, self._btnUp)
        self._btnUp.Enable(False)
        self._btnDown = xrc.XRCCTRL(self, "btnDown")
        self.Bind(wx.EVT_BUTTON, self.onDownClicked, self._btnDown)
        self._btnDown.Enable(False)
        self._btnGet = xrc.XRCCTRL(self, "btnGet")
        self.Bind(wx.EVT_BUTTON, self.onGetClicked, self._btnGet)
        self._btnOk = xrc.XRCCTRL(self, "btnOk")
        self.Bind(wx.EVT_BUTTON, self.onOkClicked, self._btnOk)
        self._btnCancel = xrc.XRCCTRL(self, "btnCancel")
        self.Bind(wx.EVT_BUTTON, self.onCancelClicked, self._btnCancel)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def setProfileFiles(self):
        self._lbxAvailableFiles.Clear()
        availableProfileFiles, missingProfileDirs = Profile.availableProfileFiles()
        for file in availableProfileFiles:
            self._lbxAvailableFiles.Append(file)
        profileFilesStr = Config.getValue('Profile/Profile Files')
        profileFiles = profileFilesStr.split(Config.PATH_SEPARATOR)
        self._lbxProfileFiles.Clear()
        if len(profileFiles) > 0:
            for file in profileFiles:
                profileDir = os.path.dirname(file)
                if profileDir == PROFILE_DEFAULT_DIR or os.path.isfile(Utils.disEnvVarPath(file)):
                    self._lbxProfileFiles.Append(file)
        else:
            for file in availableProfileFiles:
                profileDir = os.path.dirname(file)
                if profileDir == PROFILE_DEFAULT_DIR or os.path.isfile(Utils.disEnvVarPath(file)):
                    self._lbxProfileFiles.Append(file)

    def closeDlg(self):
        self.EndModal(wx.ID_CANCEL)
        return True

    def enableWidgets(self):
        isAddable = False
        availablesSelected = self._lbxAvailableFiles.GetSelections()
        if len(availablesSelected) > 0:
            for availableIx in availablesSelected:
                if self._lbxAvailableFiles.GetString(availableIx) not in self._lbxProfileFiles.GetStrings():
                    isAddable = True
                    break
        self._btnAdd.Enable(isAddable)
        profilesSelected = self._lbxProfileFiles.GetSelections()
        self._btnView.Enable(len(profilesSelected) == 1)
        self._btnRemove.Enable(len(profilesSelected) > 0)
        n = self._lbxProfileFiles.GetCount()
        selectedIx = -1
        if len(profilesSelected) == 1:
            selectedIx = profilesSelected[0]
        self._btnUp.Enable(selectedIx > 0 and n > 1)
        self._btnDown.Enable(selectedIx >= 0 and n > 1 and selectedIx < n - 1)

    def onAvailableFilesChanged(self, event):
        self.enableWidgets()

    def onAvailableFilesDClicked(self, event):
        self.onAddClicked(event)

    def onProfileFilesChanged(self, event):
        self.enableWidgets()

    def onProfileFilesDClicked(self, event):
        profilesSelected = self._lbxProfileFiles.GetSelections()
        if len(profilesSelected) == 0:
            profileFile = profilesSelected[0]
            # No action taken

    def onSaveClicked(self, event):
        wildcard = "File list files (*.lst)|*.lst|"\
                   "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Save selected profile files to a list file",
                    os.getcwd(), "", wildcard,
                    style = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                file = open(ans[0], 'w')
                if file:
                    fileList = self._lbxProfileFiles.GetStrings()
                    for item in fileList:
                        file.write(item + '\n')
                    file.close()

    def onLoadClicked(self, event):
        wildcard = "File list files (*.lst)|*.lst|" \
                    "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Load selected profile files from a list file",
                            os.getcwd(), "", wildcard,
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                file = open(ans[0], 'r')
                if file:
                    fileList = file.readlines()
                    file.close()
                    self.updateDlgProfileFiles(fileList)

    def updateDlgProfileFiles(self, fileList):
        self._lbxProfileFiles.Clear()
        for item in fileList:
            item = item.strip()
            if item and item[0] != '#':
                self._lbxProfileFiles.Append(item)
        self.enableWidgets()

    def getDlgProfileFiles(self):
        profileFiles = self._lbxProfileFiles.GetStrings()
        return profileFiles

    def onAddClicked(self, event):
        availablesSelected = self._lbxAvailableFiles.GetSelections()
        if len(availablesSelected) > 0:
            selected = []
            for availableIx in availablesSelected:
                addWanted = self._lbxAvailableFiles.GetString(availableIx)
                if addWanted not in self._lbxProfileFiles.GetStrings():
                    self._lbxAvailableFiles.Deselect(availableIx)
                    self._lbxProfileFiles.Append(addWanted)
                    selected.append(self._lbxProfileFiles.GetCount() - 1)
            self._lbxProfileFiles.SetSelection(wx.NOT_FOUND)
            for i in selected:
                self._lbxProfileFiles.SetSelection(i)
            self.enableWidgets()

    def onViewClicked(self, event):
        profilesSelected = self._lbxProfileFiles.GetSelections()
        if len(profilesSelected) == 1:
            profileFile = self._lbxProfileFiles.GetStrings()[profilesSelected[0]]
            fullFilePath = Utils.disEnvVarPath(profileFile)
            profileDir = os.path.dirname(profileFile)
            if profileDir == PROFILE_DEFAULT_DIR:
                fullFilePath = os.path.join(Utils.defaultProfileDir(), os.path.basename(profileFile))
            if os.path.isfile(fullFilePath):
                wx.GetApp().frame().commands().viewTextFilePage(fullFilePath)

    def onRemoveClicked(self, event):
        profilesSelected = self._lbxProfileFiles.GetSelections()
        for i in range(len(profilesSelected)-1, -1, -1):
            self._lbxProfileFiles.Delete(profilesSelected[i])
        self._lbxProfileFiles.SetSelection(wx.NOT_FOUND)
        self.enableWidgets()

    def onResetClicked(self, event):
        currentProfileFiles = self._lbxProfileFiles.GetStrings()
        resetProfileFiles = Profile.resetProfiles(currentProfileFiles)
        self._lbxProfileFiles.Clear()
        for file in resetProfileFiles:
            self._lbxProfileFiles.Append(file)
        self.enableWidgets()

    def onUpClicked(self, event):
        selectedIx = self._lbxProfileFiles.GetSelections()[0]
        value = self._lbxProfileFiles.GetString(selectedIx)
        self._lbxProfileFiles.Delete(selectedIx)
        self._lbxProfileFiles.Insert(value, selectedIx - 1)
        self._lbxProfileFiles.SetSelection(wx.NOT_FOUND)
        self._lbxProfileFiles.SetSelection(selectedIx - 1)
        self.enableWidgets()

    def onDownClicked(self, event):
        selectedIx = self._lbxProfileFiles.GetSelections()[0]
        value = self._lbxProfileFiles.GetString(selectedIx)
        self._lbxProfileFiles.Delete(selectedIx)
        self._lbxProfileFiles.Insert(value, selectedIx + 1)
        self._lbxProfileFiles.SetSelection(wx.NOT_FOUND)
        self._lbxProfileFiles.SetSelection(selectedIx + 1)
        self.enableWidgets()

    def onGetClicked(self, event):
        wildcard = APP_NAME+" profile files (*"+PROFILE_FILE_EXT+")|*"+PROFILE_FILE_EXT+"|" \
                   "XML files (*.xml)|*.xml|" \
                   "All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open profile file",
                            os.getcwd(), "", wildcard,
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                getWanted = ans[0]
                getWanted = Utils.environmentalise(getWanted)
                if getWanted not in self._lbxProfileFiles.GetStrings():
                    self._lbxProfileFiles.Append(getWanted)
                    self.enableWidgets()

    def onOkClicked(self, event):
        #update config and reload profile (or do in options?)
        profileFiles = self._lbxProfileFiles.GetStrings()
        profileFilesStr = Config.PATH_SEPARATOR.join(profileFiles)
        Config.setValue('Profile/Profile Files', profileFilesStr)
        self.EndModal(wx.ID_OK)

    def onCancelClicked(self, event):
        # Restore dlg profile files to that of config
        self.setProfileFiles()
        self.EndModal(wx.ID_CANCEL)

    def onClose(self, event):
        # Restore dlg profile files to that of config
        self.setProfileFiles()
        self.EndModal(wx.ID_CANCEL)
        return True
