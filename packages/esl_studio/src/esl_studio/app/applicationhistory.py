#! /usr/bin/python

import os.path
import wx

from .config import Config

NoRecentApplications = "No Recent Applications"
ApplicationHistoryMaxFiles = 10

class ApplicationHistory():
    def __init__(self, frame):
        self._fileHistory = wx.FileHistory(ApplicationHistoryMaxFiles)
        self._frame = frame
        self._mode = "editing"

    def setup(self):
        maxCount = self._fileHistory.GetMaxFiles()
        self._frame.Bind(wx.EVT_MENU_RANGE, self.onFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE1+maxCount-1)
        #self._frame.Bind(wx.EVT_WINDOW_DESTROY, self.cleanup) -- is this necessary
        self.loadHistory()
        pass

    def clear(self): # in Control.clearForProfiles in setProfile
        menuList = self._fileHistory.GetMenus()
        for menu in menuList:
            self._fileHistory.RemoveMenu(menu)

    #def cleanup(self):
        # A little extra cleanup is required for the FileHistory control <<< so says the demo - but is it?
        #del self._fileHistory
        #self.menu.Destroy() -- ? all useMenus via .GetMenus() ?

    def useMenu(self, menu):
        self._fileHistory.UseMenu(menu)

    def mode(self):
        return self._mode
    def setMode(self, mode):
        self._mode = mode

    def onFileHistory(self, evt):
        if self._mode != "browsing":
            fileNum = evt.GetId() - wx.ID_FILE1
            appFilePath = self._fileHistory.GetHistoryFile(fileNum)
            if appFilePath != NoRecentApplications:
                if os.path.exists(appFilePath):
                    cancelled = False
                    commands = self._frame.commands()
                    if self._frame.application().changed():
                        cancelled = commands.askToSaveApplication()
                    if not cancelled:
                        commands.refreshApplication(appFilePath)
                else:
                    self.askToRemove(appFilePath)
        else:
            msg = 'Application History  not available in ' + self._mode + ' mode\n'
            self._frame.control().appendMessage(msg)

    def addToHistory(self, path):
        if self._fileHistory.GetCount() > 0 and self._fileHistory.GetHistoryFile(0) == NoRecentApplications:
            self._fileHistory.RemoveFileFromHistory(0)
        self._fileHistory.AddFileToHistory(path)

    def clearHistory(self):
        nr = self._fileHistory.GetCount()
        for i in range(nr - 1, -1, -1):
            self._fileHistory.RemoveFileFromHistory(i)
        self._fileHistory.AddFileToHistory(NoRecentApplications)

    def loadHistory(self):
        historyStr = Config.getValue("Settings/history")
        if not historyStr:
            self._fileHistory.AddFileToHistory(NoRecentApplications)
        else:
            history = historyStr.split(Config.PATH_SEPARATOR)
            for appFilePath in history:
                self._fileHistory.AddFileToHistory(appFilePath)

    def getHistory(self):
        history = []
        nr = self._fileHistory.GetCount()
        for i in range(nr):
            appFilePath = self._fileHistory.GetHistoryFile(i)
            if appFilePath != NoRecentApplications:
                history.append(appFilePath)
        return history

    def askToRemove(self, appFilePath):
        msg = "Application \"" + appFilePath + "\" not found\n"
        if msg:
            msg += "Do you want to remove it from the history"
            dlg = wx.MessageDialog(self._frame,
                                   msg,
                                   "Application not found",
                                   wx.YES_NO | wx.ICON_INFORMATION)
            ans = dlg.ShowModal()
            if ans == wx.ID_YES:
                nr = self._fileHistory.GetCount()
                for i in range(nr):
                    if self._fileHistory.GetHistoryFile(i) == appFilePath:
                        self._fileHistory.RemoveFileFromHistory(i)
                        break
                if self._fileHistory.GetCount() == 0:
                    self._fileHistory.AddFileToHistory(NoRecentApplications)
