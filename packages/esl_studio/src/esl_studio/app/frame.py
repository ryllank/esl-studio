#! /usr/bin/python

import sys
import os

import wx
import wx.adv

from . import utils as Utils
from .config import Config
from .profile import Profile
from . import auihandler as aui

from .filedroptarget import FileDropTarget
from .application.application import Application
from .viewmanager import ViewManager
from .control import Control
from .commands import Commands
from .printing import Printing
from .applicationhistory import ApplicationHistory


#ID_ViewElements = wx.ID_HIGHEST + 1

#ID_Test = wx.ID_HIGHEST + 101

class Frame(wx.Frame):
    def __init__(self, parent, ID, title):
        self._parent = parent
        self._title = title
        wx.BeginBusyCursor()
        x, y, width, height, maximised = Config.getSettings(self)
        self._splash = None

        style = wx.DEFAULT_FRAME_STYLE
        if maximised:
            style |= wx.MAXIMIZE # doesnt seem to work (any more) for windows when isFrozen (i.e. via PyInstaller) - see before Show in setup
        self._wxFrame = wx.Frame.__init__(self, parent, -1, title,
                                          (x, y), (width, height),
                                          style)

        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame, self)

        self._auimgr = aui.AuiManager(None)

        # tell AuiManager to manage this frame
        self._auimgr.SetManagedWindow(self)

        self.CreateStatusBar()
        statusBar = self.GetStatusBar()
        if statusBar:
            statusBar.SetStatusText("Loading")

        self._application = Application(self)
        self._viewManager = ViewManager(self)
        self._control = Control(self)
        self._commands = Commands(self)
        self._printing = Printing(self)
        self._applicationHistory = ApplicationHistory(self)

        if not Utils.isFrozen() and Config.getBool('General/Splash'):
            self.showSplash()

        wx.EndBusyCursor()

    def showSplash(self):
        file = Utils.resourceFile("splash.png")
        if file:
            image = wx.Image(file)
            bitmap = wx.Bitmap(image)
            self._splash = wx.adv.SplashScreen(bitmap,
                                        wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                                        6000, None, -1, wx.DefaultPosition, wx.DefaultSize,
                                        wx.SIMPLE_BORDER | wx.STAY_ON_TOP)
            wx.Yield()

    def setup(self):
        wx.BeginBusyCursor()
        startupMsg = ""
        cmdLineMsgs = wx.GetApp().cmdLineMsgs()
        if cmdLineMsgs:
            if len(cmdLineMsgs) == 1:
                startupMsg += "Command line error: "+cmdLineMsgs[0]+"\n"
            elif len(cmdLineMsgs) > 1:
                startupMsg += "Command line errors:\n"
                for msg in cmdLineMsgs:
                    startupMsg += "- "+msg+"\n"

        parameters = wx.GetApp().parameters()
        if len(parameters) == 0:    # Don't set cwd to last one if have got a parameter (an eslstudio file).
            cwd = Config.getString("Settings/cwd")
            if cwd:
                if os.path.isdir(cwd):
                    os.chdir(cwd)
                else:
                    startupMsg += "Last working directory \""+cwd+"\" not found\n"

        self._viewManager.MakeStdPanes()
        self._viewManager.CreateMenuBar()

        if startupMsg:
            self.control().appendMessage(startupMsg)

        reset_layout = Config.getBool("Views/Reset Layout")
        if reset_layout:
            # Clear the options reset layout after reading it
            Config.setBool("Views/Reset Layout", False)
        cmd_reset = wx.GetApp().options().get('reset')
        if cmd_reset is not None:
            reset_layout = cmd_reset # cmd reset overrides reset from last config
        perspective = ""
        if not reset_layout:
            using_AGW_AUI = aui.UseAUI() == aui.AUI_AGW
            perspective = Config.getPerspective(self, using_AGW_AUI)
        try:
            self._auimgr.LoadPerspective(perspective)
        except:
            pass
        # Else - Leave default perspective (to reset the layout).
        if cmd_reset: # Also reset on command line means Profile Files.
            currentProfileFiles = Config.getValue('Profile/Profile Files')
            currentProfileFiles = currentProfileFiles.split(Config.PATH_SEPARATOR)
            resetProfileFiles = Profile.resetProfiles(currentProfileFiles)
            resetProfileFiles = Config.PATH_SEPARATOR.join(resetProfileFiles)
            Config.setValue('Profile/Profile Files', resetProfileFiles)

        self._control.setup()

        self._auimgr.Update()

        if sys.platform == 'win32' and Config.getValue("Settings/maximised") and Utils.isFrozen() and not self.IsMaximized():
            #print("-Frame.setup explicit Maximize for win32 and isFrozen")
            self.Maximize(True)

        self.Show(True)

        ##if self._splash: self._splash.Close()
        self._control.setStatusText("")
        self._fileDropTarget = FileDropTarget(self)
        self.SetDropTarget(self._fileDropTarget)
        wx.EndBusyCursor()
        self._applicationHistory.setup()
        initialFile = ""
        if len(parameters) > 0:
            initialFile = parameters[0]
        else:
            if Config.getBool("General/Open Last Application"):
                initialFile = Config.getValue("Settings/application")
        if initialFile:
            self._application.loadFromFile(initialFile)
        else:
            self._application.newApplication()
        if self._splash: self._splash.Close()
        if Utils.isFrozen():
            try:
                import pyi_splash
                pyi_splash.close()
            except: pass

    def auiManager(self): return self._auimgr
    def viewManager(self): return self._viewManager
    def control(self): return self._control
    def commands(self): return self._commands
    def application(self): return self._application
    def printing(self): return self._printing
    def applicationHistory(self): return self._applicationHistory

    def OnCloseFrame(self, close_event):
        cancelled = False
        if self._control.mode() == "browsing":
            flags = wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
            msg = 'In ' + self._control.mode() + ' mode - do you really want to close the application\n'
            dlg = wx.MessageDialog(self, msg,
                                   "Close Application", flags)
            ans = dlg.ShowModal()
            if ans != wx.ID_YES:
                cancelled = True
        if not cancelled:
            if self._application.changed():
                noCancel = not close_event.CanVeto()
                cancelled = self._commands.askToSaveApplication(noCancel)
            if not cancelled:
                saveSettings = True
                cmd_configFile = wx.GetApp().options().get('config')
                if cmd_configFile:
                    saveSettings = False
                using_AGW_AUI = aui.UseAUI() == aui.AUI_AGW
                Config.closeDown(saveSettings, self, using_AGW_AUI)
                self._auimgr.UnInit()
                self.Destroy()
