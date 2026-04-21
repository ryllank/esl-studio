#! /usr/bin/python
import os
import sys
import traceback

import wx

from esl_studio.app.general import APP_NAME, APP_TITLE, APP_VENDOR, APPLICATION_VERSION_STRING
from esl_studio.app.config import Config
from esl_studio.app.configupdate import ConfigUpdate
import esl_studio.app.utils as Utils
import esl_studio.app.auihandler as aui
from esl_studio.app.utils import setEnvironment, isFrozen, disEnvVarPath
from esl_studio.app.frame import Frame

class App(wx.App):
    def OnInit(self):
        self.SetAppName(APP_NAME)
        self.SetVendorName(APP_VENDOR)
        caption = APP_TITLE + ' v' + APPLICATION_VERSION_STRING
        canContinue = setEnvironment()
        self._frame = None
        Config.setup()
        if not canContinue:
            title = APP_NAME + " v" + APPLICATION_VERSION_STRING + " Error"
            wx.MessageBox("Failed to set environment for esl-studio - check installation or ESLSTUDIODIR environment variable if specified", title)
        else:
            self._options = {}
            self._parameters = []
            self._cmdLineMsgs = []
            canContinue = self.checkCmdLineOptions()
        if canContinue:
            options = wx.GetApp().options()
            configFile = options.get('config')
            if configFile:
                if os.path.isfile(disEnvVarPath(configFile)):
                    Config.retainSettings()
                    Config.loadConfigFile(configFile)
                else:
                    del options['config']
                    configFile = None
            if not configFile:
                ConfigUpdate.checkForUpdatedSystemConfig()
            # AUI set in options for "next" start - which is this start.
            agwaui = Config.getBool("Advanced/AGWAUI")
            wxaui = Config.getBool("Advanced/WXAUI")
            # Commmand line options - overrides options set for "next" start.
            # Do this before first load auihandler
            cmd_agwaui = options.get('agwaui')
            cmd_wxaui = options.get('wxaui')
            if cmd_wxaui is not None:
                agwaui = cmd_agwaui
            if cmd_wxaui is not None:
                wxaui = cmd_wxaui
            if not agwaui and not wxaui:
                agwaui = True
            if agwaui:
                aui.SetUseAUI(aui.AUI_AGW)
            elif wxaui:
                aui.SetUseAUI(aui.AUI_WX)
            try:
                self._frame = Frame(None, -1, caption)
                self._frame.setup()
            except Exception as e:
                if isFrozen():
                    try:
                        import pyi_splash
                        pyi_splash.close()
                    except:
                        pass
                if wx.IsBusy():
                    wx.EndBusyCursor()
                text = "Exception (initialising): " + str(e)
                text += '\n' + traceback.format_exc()
                print(text)
                title = APP_NAME + " v" + APPLICATION_VERSION_STRING + " Exception (initialising)"
                wx.MessageBox(text, title)
                Utils.bleep()
                canContinue = False
        return canContinue

    def frame(self): return self._frame

    def options(self): return self._options
    def parameters(self): return self._parameters
    def cmdLineMsgs(self): return self._cmdLineMsgs

    def checkCmdLineOptions(self):
        canContinue = True
        self._cmdLineMsgs = []
        options = True
        argc = len(sys.argv) #self.argc
        argv = sys.argv #self.argv
        i = 1
        while i < argc:
            arg = argv[i]
            if options and arg[0] == '-' or (sys.platform == 'win32' and arg[0] == '/'):
                arg = arg[1:]
                if arg[0] == '-':
                    arg = arg[1:]
                origArg = arg
                arg = arg.lower()
                if arg == 'h' or arg == '?' or arg == 'help':
                    self.showUsage()
                    canContinue = False
                elif arg == 'r' or arg == 'reset':
                    self._options['reset'] = True
                elif arg == 'w' or arg == 'wxaui':
                    self._options['agwaui'] = False
                    self._options['wxaui'] = True
                elif arg == 'a' or arg == 'agwaui':
                    self._options['agwaui'] = True
                    self._options['wxaui'] = False
                elif arg == 'c' or arg == 'config':
                    opt = ""
                    if i < argc - 1:
                        i += 1
                        opt = argv[i]
                        if opt == '=':
                            if i < argc - 1:
                                i += 1
                                opt = argv[i]
                    if opt:
                        if opt[0] == '-' or (sys.platform == 'win32' and opt[0] == '/'):
                            i -= 1
                            opt = ""
                        else:
                            self._options['config'] = opt
                    if not opt:
                        self._cmdLineMsgs.append("no config-file given after config option")
                    else:
                        if not os.path.isfile(disEnvVarPath(opt)):
                            self._cmdLineMsgs.append("config-file \""+opt+"\" not a valid file")
                elif arg.startswith('c=') or arg.startswith('config='):
                    eqIx = arg.index("=")
                    opt = origArg[eqIx+1:]
                    if opt:
                        self._options['config'] = opt
                        if not os.path.isfile(disEnvVarPath(opt)):
                            self._cmdLineMsgs.append("config-file \""+opt+"\" not a valid file")
                    else:
                        self._cmdLineMsgs.append("no config-file given after config= option")
                else:
                    self._cmdLineMsgs.append("unrecognised argument \""+origArg+"\"")
            else:
                options = False
                self._parameters.append(arg)
                if len(self._parameters) == 1:
                    if not os.path.isfile(disEnvVarPath(arg)):
                        self._cmdLineMsgs.append("parameter esl-studio-file \"" + arg + "\" not a valid file")
                else:
                    self._cmdLineMsgs.append("unrecognised parameter "+str(len(self._parameters))+" \""+arg+"\"")
            i += 1
        return canContinue

    def showUsage(self):
        if isFrozen():
            try:
                import pyi_splash
                pyi_splash.close()
            except: pass
        title = APP_NAME + " v"+APPLICATION_VERSION_STRING+" Usage"
        msg = "esl_studio [(-r |--reset)(-a |--agwaui)(-w |--wxaui)(-c |--config [=] config-file)] [esl-studio-file]"
        msg += "\n-r - reset view layout and profiles"
        msg += "\n-a - use full Advanced User Interface (wxPython)"
        msg += "\n-w - use basic Advanced User Interface (wxWidgets)"
        msg += "\n-c - initially load config-file in place of user's settings"
        msg += "\n     (user's original settings retained when exit)"
        wx.MessageBox(msg, title)

def OnExceptionInMainLoop(exc_type, exc_value, exc_traceback):
    if wx.IsBusy():
        wx.EndBusyCursor()
    msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    wx.GetApp()._frame.control().appendMessage(msg)
    Utils.bleep()

def main():
    try:
        app = App()
        sys.excepthook = OnExceptionInMainLoop
        app.MainLoop()
    except Exception as e:
        if wx.IsBusy():
            wx.EndBusyCursor()
        if isFrozen():
            try:
                import pyi_splash
                pyi_splash.close()
            except: pass
        text = "Exception (main): " + str(e)
        text += '\n' + traceback.format_exc()
        #?traceback.format_exc()
        #if self._frame and self._frame.viewManager() and self._frame.viewManager().messagesView():
        #    self._frame.viewManager().messagesView().appendText(text)
        #else:
        #    throw(e)
        print(text)
        title = APP_NAME + " v" + APPLICATION_VERSION_STRING + " Exception (main)"
        Utils.bleep()
        wx.MessageBox(text, title)
        raise

if __name__ == '__main__':
    main()
