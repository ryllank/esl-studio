#! /usr/bin/python

import os
import sys
import tempfile
import shutil
import traceback

import wx
import wx.adv

import esl_diagram.xmlutil as xut

from . import utils as Utils
from .general import APP_NAME, APP_FILE_EXT, APP_WEBSITE, APPLICATION_VERSION_STRING
from .config import Config
from .application.codesubprogram import CodeSubprogram
from .dlg.aboutdlg import AboutDlg
from .dlg.optionsdlg import OptionsDlg
from .dlg.zoomdlg import ZoomDlg
from .views.stc import Stc

class CommandDefn(object):

    def __init__(self, name, commandId, procedure, commandXmlElement):
        self.name = name # used to identify the command
        self.commandId = commandId
        self.procedure = procedure # identifies procedure - name of method in this class
        self.commandXmlElement = commandXmlElement

class Commands(object):

    TagAttributeProfileDict = {"command":"name"}
    CheckESLUpdates_options = ""  # option-string that may be added to checkeslupdates command.

    def __init__(self, frame):
        self._frame = frame
        self._control = self._frame.control()
        self._application = self._frame.application()
        self._process = None
        self._commandsXmlProfile = xut.XmlElement("<commands-profile/>")
        self.clear()
        self._textEditorOpenCmd = ""

    def clear(self):
        self.commandDefnByName = {}
        self.commandDefnByCommandId = {}
        self._commandId = wx.ID_HIGHEST + 1
        self._commandId += 200  # safety margin
        self._commandsXmlProfile = xut.XmlElement("<commands-profile/>")
        self._runCommandStack = []
        self._runCommandStackPosn = -1

    def loadFromFile(self, filepath):
        if os.path.exists(filepath):
            xmlElement, error = xut.xmlElementFromFile(filepath)
            if xmlElement:
                self.loadFromXml(xmlElement)

    def loadFromString(self, strng):
        xmlElement = xut.xmlElement(strng)
        if xmlElement:
            self.loadFromXml(xmlElement)

    def loadFromXml(self, xmlElement):
        if xmlElement.name() == "commands": commandsXmlElement = xmlElement
        else: commandsXmlElement = xmlElement.getXmlElementByName( "commands", True)
        if commandsXmlElement:
            commandXmlList = commandsXmlElement.getXmlElementListByName("command", False)
            if commandXmlList:
                for commandXmlElement in commandXmlList:
                    self._commandsXmlProfile.replaceOrAppendChild(commandXmlElement, Commands.TagAttributeProfileDict)

    def installProfile(self):
        commandXmlList = self._commandsXmlProfile.getChildren()
        if commandXmlList:
            for commandXmlElement in commandXmlList:
                name = commandXmlElement.getAttribute("name")
                procedure = commandXmlElement.getAttribute("procedure")
                if (name and procedure and
                    procedure in self.__class__.__dict__):
                    commandDefn = CommandDefn(name, self._commandId, procedure, commandXmlElement)
                    self.commandDefnByName[name] = commandDefn
                    self.commandDefnByCommandId[self._commandId] = commandDefn
                    self._commandId += 1

    def invokeCommand(self, commandevent):
        commandId = commandevent.GetId()
        commandDefn = self.commandDefnByCommandId[commandId]
        if commandDefn:
            modeOk = False
            if self._control.mode() == "editing":
                modeOk = True
            elif self._control.mode() == "browsing":
                browsable = commandDefn.commandXmlElement.getAttribute("browse")
                if browsable and browsable == "true":
                    modeOk = True
            if modeOk:
                procedure = self.commandDefnByCommandId[commandId].procedure
                if isinstance(procedure, str):
                    proc = self.__class__.__dict__.get(procedure)
                    if proc:
                        proc(self, commandevent)
            else:
                commandName = commandDefn.commandXmlElement.getAttribute("name")
                msg = 'Command ' + commandName + ' not available in ' + self._control.mode() + ' mode\n'
                self._control.appendMessage(msg)

    def executeCommand(self, commandName, commandData=None):
        commandDefn = self.commandDefnByName.get(commandName)
        if commandDefn:
            modeOk = False
            if self._control.mode() == "editing":
                modeOk = True
            elif self._control.mode() == "browsing":
                browsable = commandDefn.commandXmlElement.getAttribute("browse")
                if browsable and browsable == "true":
                    modeOk = True
            if modeOk:
                procedure = commandDefn.procedure
                if isinstance(procedure, str):
                    proc = self.__class__.__dict__.get(procedure)
                    if proc:
                        proc(self, None, commandData)
            else:
                commandName = commandDefn.commandXmlElement.getAttribute("name")
                msg = 'Command ' + commandName + ' not available in ' + self._control.mode() + ' mode\n'
                self._control.appendMessage(msg)

    def NotImplemented(self, commandevent=None, commanddata=None):
        text = "NotImplemented invoked with no commandevent"
        if commandevent:
            commandId = commandevent.GetId()
            command = "Unknown command"
            if commandId:
                command = self.commandDefnByCommandId[commandId].name
            text = "NotImplemented invoked for command '" + str(command) + "' id=" + str(commandId)
        wx.MessageBox(text)


    def askToSaveApplication(self, noCancel = False):
        cancelled = False
        flags = wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
        if not noCancel: flags |= wx.CANCEL
        dlg = wx.MessageDialog(self._frame,
                               "Application has changed - do you want to save it",
                               "Application changed", flags)
        ans = dlg.ShowModal()
        if ans == wx.ID_YES:
            if not self._application.filepath():
                saved = self.SaveApplicationAs(None)
                if not saved: cancelled = True
            else:
                self._application.saveApplication()
        elif ans == wx.ID_CANCEL: cancelled = True
        return cancelled

    def refreshApplication(self, appFilePath, reloadingProfile=False):
        wx.BeginBusyCursor()
        self._frame.viewManager().resetMainview()
        self._frame.viewManager().resetPanes()
        self._frame.viewManager().applicationView().clear()
        self._control.checkAllToggleViewItems()
        self._control.alterationStack().clear()
        self._control.enableDisableUndoRedo()
        self._control.propertiesControl().clearPropertyPage()
        if appFilePath:
            valid = self._application.loadFromFile(appFilePath, reloadingProfile)
            if not valid:
                appFilePath = ""
        if not appFilePath:
            self._application.newApplication()
        self._frame.viewManager().mainView().Refresh()
        wx.EndBusyCursor()

    def reloadProfile(self):
        cancelled = False
        if self._application.changed():
            cancelled = self.askToSaveApplication()
        if not cancelled:
            appFilePath = self._application.filepath()
            self._control.setProfile()
            self.refreshApplication(appFilePath, reloadingProfile=True)

    def NewApplication(self, commandevent=None, commanddata=None):
        cancelled = False
        if self._application.changed():
            cancelled = self.askToSaveApplication()
        if not cancelled:
            self.refreshApplication('')

    def OpenApplication(self, commandevent=None, commanddata=None):
        cancelled = False
        if self._application.changed():
            cancelled = self.askToSaveApplication()
        if not cancelled:
            wildcard = APP_NAME+" application files (*"+APP_FILE_EXT+")|*"+APP_FILE_EXT+"|"\
                       "XML files (*.xml)|*.xml|" \
                       "All files (*.*)|*.*"
            dlg = wx.FileDialog(self._frame, "Open application file",
                                os.getcwd(), "", wildcard,
                                style = wx.FD_OPEN | wx.FD_CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                ans = dlg.GetPaths()
                if ans and len(ans) == 1:
                    self.refreshApplication(ans[0])

    def dropFiles(self, filenames):
        if len(filenames) > 1:
            self._control.appendMessage("Can only drop a single application file\n")
        else:
            cancelled = False
            if self._application.changed():
                cancelled = self.askToSaveApplication()
            if not cancelled:
                self.refreshApplication(filenames[0])

    def SaveApplication(self, commandevent=None, commanddata=None):
        saved = True
        if self._application.filepath():
            self._application.saveApplication()
            self._control.alterationStack().clear()
            self._control.enableDisableUndoRedo()
        else:
            saved = self.SaveApplicationAs(commandevent)
        return saved

    def SaveApplicationAs(self, commandevent=None, commanddata=None):
        saved = False
        wildcard = APP_NAME+" application files (*"+APP_FILE_EXT+")|*"+APP_FILE_EXT+"|"\
                   "XML files (*.xml)|*.xml|" \
                   "All files (*.*)|*.*"
        dlg = wx.FileDialog(self._frame, "Save application file",
                    os.getcwd(), "", wildcard,
                    style = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                self._application.saveToFile(ans[0])
                self._frame.applicationHistory().addToHistory(ans[0])
                saved = True
                self._control.alterationStack().clear()
                self._control.enableDisableUndoRedo()
        return saved

    def ImportFromISE(self, commandevent=None, commanddata=None):
        if sys.platform != "win32":
            wx.MessageBox("Import from ESL-ISE is only available on Windows")
        else:
            xise_path = "xise.exe"
            if shutil.which(xise_path) == None:
                esldir = os.environ.get('ESLDIR')
                if esldir:
                    xise_path = os.path.join(esldir, 'ise', 'bin', xise_path)
                    if not os.path.exists(xise_path):
                        xise_path = None
                        self._control.appendMessage("Cannot find xise.exe program\n")
            if xise_path:
                wildcard = "ESL-ISE files (*.ise)|*.ise|" \
                           "All files (*.*)|*.*"
                dlg = wx.FileDialog(self._frame, "Open ESL-ISE file to import",
                                    os.getcwd(), "", wildcard,
                                    style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
                if dlg.ShowModal() == wx.ID_OK:
                    ans = dlg.GetPaths()
                    if ans and len(ans) == 1:
                        ise_file = ans[0]
                        ise_studio_file = ise_file + ".eslstudio"
                        if os.path.exists(ise_studio_file):
                            msg = "Import file \"" +ise_studio_file + "\" exists\nDo you want to overwrite it\n"
                            dlg = wx.MessageDialog(self._frame,
                                                   msg,
                                                   "Import file exists",
                                                   wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
                            ans = dlg.ShowModal()
                            if ans == wx.ID_OK:
                                os.remove(ise_studio_file)
                            else:
                                ise_studio_file = ""
                        if ise_studio_file:
                            cmd = xise_path + " \"" + ise_file + "\" \"" + ise_studio_file + "\""
                            retcode, lines = self.execute(cmd)
                            if retcode != 0:
                                self.showCommandOutput(cmd, retcode, lines)
                            if not os.path.exists(ise_studio_file):
                                self._control.appendMessage(
                                    "Failed to create import file \"" + ise_studio_file + "\"\n")
                            else:
                                cancelled = False
                                if self._application.changed():
                                    cancelled = self.askToSaveApplication()
                                if not cancelled:
                                    self.refreshApplication(ise_studio_file)

    def PrintSaveDiagram(self, commandevent=None, commanddata=None):
        return self._frame.printing().PrintSaveDiagram()

    def PageSetup(self, commandevent=None, commanddata=None):
        return self._frame.printing().PageSetup()

    def PrintPreview(self, commandevent=None, commanddata=None):
        return self._frame.printing().PrintPreview()

    def PrintView(self, commandevent=None, commanddata=None):
        return self._frame.printing().PrintView()

    def PrintDiagram(self, commandevent=None, commanddata=None):
        return self._frame.printing().PrintDiagram()

    def SaveDiagram(self, commandevent=None, commanddata=None):
        return self._frame.printing().SaveDiagram()

    def PrintText(self, commandevent=None, commanddata=None):
        return self._frame.printing().PrintText()

    def ViewSourceFile(self, commandevent=None, commanddata=None):
        wildcard = "ESL files (*.esl)|*.esl|"\
                   "ESL-Studio and related files (*.eslstudio etc)|*.eslstudio;;*.eslprofile;*.sec;*.dsp|"
        if sys.platform == 'win32':
            wildcard += "All files (*.*)|*.*"
        else:
            wildcard += "All files (*)|*"
        dlg = wx.FileDialog(self._frame, "Open source (text) file for viewing",
                            os.getcwd(), "", wildcard,
                            style = wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                filepath = ans[0]
                exists = os.path.exists(filepath)
                textPage = self.viewTextFilePage(filepath, allowNewFile=not exists)
                if textPage: # No long restrict editing to esl files - textPage.style() == Stc.Style.ESL:
                    textPage.setAllowToggleEdit(True)
                    textPage.setAllowSave(True)

    def OpenTextEditor(self, commandevent=None, commanddata=None):
        self.openTextEditor()

    def viewTextFilePage(self, filepath, allowNewFile=False):
        ok = True
        textPage = None
        file = None
        msg = ""
        mode = 'r'
        if allowNewFile:
            mode = 'a' # actually use append rather than 't' truncate
        try:
            file = open(filepath, mode)
        except Exception:
            ok = False
            msg = 'Failed to open text file "' + filepath + '"\n'
        if ok and file and not file.closed:
            if not allowNewFile:
                try:
                    text = file.read()
                except Exception:
                    ok = False
                    msg = 'Failed to read text file "' + filepath + '"\n'
        if file and not file.closed:
            file.close()
        if not ok and msg:
            self._control.appendMessage(msg)
        if ok:
            tabname = os.path.basename(filepath)
            textPage = self._frame.viewManager().mainView().addViewTextPage(tabname)
            ok = textPage.LoadFile(filepath)
            if ok:
                pageindex = self._frame.viewManager().mainView().GetPageIndex(textPage)
                self._frame.viewManager().mainView().SetSelection(pageindex)
                self._control.propertiesControl().clearPropertyPage()
            else:
                self._frame.viewManager().mainView().detachPage(textPage)
        if not ok:
            textPage = None
        if textPage:
            textPage.setReadOnly(not allowNewFile)
            textPage.setAllowRunESLDirect(textPage.style() == Stc.Style.ESL)
        return textPage

    def openView(self, viewSrc):
        viewFile = Utils.eslFile(viewSrc)
        if viewFile:
            self.viewEslFilePage(viewFile)
        else:
            msg = 'Failed to find view file "' + viewSrc +'"\n'
            self._control.appendMessage(msg)

    def viewEslFilePage(self, filepath):
        tabname = os.path.basename(filepath)
        textPage = self._frame.viewManager().mainView().addViewEslPage(tabname, filepath)
        pageindex = self._frame.viewManager().mainView().GetPageIndex(textPage)
        self._frame.viewManager().mainView().SetSelection(pageindex)
        self._frame.viewManager().applicationView().selectItem(None)
        self._control.propertiesControl().clearPropertyPage()

    def ExitApp(self, event):
        self._frame.Close(True)

    def Undo(self, commandevent=None, commanddata=None):
        self._control.alterationStack().undo()
        self._control.enableDisableUndoRedo()

    def Redo(self, commandevent=None, commanddata=None):
        self._control.alterationStack().redo()
        self._control.enableDisableUndoRedo()

    def CanvasAction(self, commandevent=None, commanddata=None):
        commandId = commandevent.GetId()
        commandDefn = self.commandDefnByCommandId[commandId]
        if commandDefn:
            infoXmlElement = commandDefn.commandXmlElement.getXmlElementByName("info")
            if infoXmlElement:
                action = infoXmlElement.getAttribute("action")
                if action:
                    page = self._control.currentCanvas()
                    if page:
                        actionStr = '<action name="'+action+'">'
                        actionStr += infoXmlElement.xml()
                        actionStr += '</action>'
                        page.Action(actionStr)

    def ToggleView(self, commandevent=None, commanddata=None):
        commandId = commandevent.GetId()
        commandDefn = self.commandDefnByCommandId[commandId]
        if commandDefn:
            infoXmlElement = commandDefn.commandXmlElement.getXmlElementByName("info")
            if infoXmlElement:
                viewname = infoXmlElement.getAttribute("viewname")
                if viewname:
                    showing = self._frame.viewManager().toggleView(viewname)
                    self._frame.viewManager().menubar().checkItem(commandId, showing)
                    self._frame.viewManager().toolbar().toggleItem(commandId, showing)

    def ClearMessages(self, commandevent=None, commanddata=None):
        self._control.clearMessages()

    def ZoomDialog(self, commandevent=None, commanddata=None):
        page = self._control.currentCanvas()
        if page:
            initScale = 100*page.GetScale()
            dlg = ZoomDlg.Instance(self._frame, initScale)
            #dlg = wx.TextEntryDialog(self._frame, "Set canvas zoom factor (%)")
            if dlg.ShowModal() == wx.ID_OK:
                ans = dlg.GetValue()
                if ans:
                    #scale = float(ans) / 100
                    #page.SetScale(scale)
                    actionStr = '<action name="Set Scale">'
                    actionStr += '<info to="'+str(ans)+'"/>'
                    actionStr += '</action>'
                    page.Action(actionStr)
        else:
            wx.MessageBox("No canvas selected to zoom")

    def ZoomAll(self, commandevent=None, commanddata=None):
        page = self._control.currentCanvas()
        if page:
            actionStr = '<action name="Set Scale">'
            actionStr += '<info to="all"/>'
            actionStr += '</action>'
            page.Action(actionStr)
        else:
            wx.MessageBox("No canvas selected to zoom")

    def ZoomSelected(self, commandevent=None, commanddata=None):
        page = self._control.currentCanvas()
        if page:
            actionStr = '<action name="Set Scale">'
            actionStr += '<info to="selected"/>'
            actionStr += '</action>'
            page.Action(actionStr)
        else:
            wx.MessageBox("No canvas selected to zoom")

    def ShowOptions(self, commandevent):
        dlg = OptionsDlg.Instance(self._frame)
        if dlg.ShowModal() == wx.ID_OK:
            # Update the config data with (changed) values from the dlg
            dlg.updateConfig()
            # Diagram options may have changed
            blockDiagramPropertyOptions = Config.getBlockDiagramPropertyOptions()
            self._frame.viewManager().mainView().setupModelCanvases(None, blockDiagramPropertyOptions)
            self._frame.viewManager().mainView().setupSubprogramCanvases(None, blockDiagramPropertyOptions)
            canvas = self._control.currentCanvas()
            if canvas:
                canvas.Refresh()
        else:
            dlg.resetFromConfig()

    def InsertModelDiagram(self, commandevent=None, commanddata=None):
        valid = self._control.modulesControl().addModel('model')

    def InsertSubmodelDiagram(self, commandevent=None, commanddata=None):
        valid = self._control.modulesControl().addSubmodel('')

    def InsertSegmentDiagram(self, commandevent=None, commanddata=None):
        valid = self._control.modulesControl().addSegment('segment')

    def InsertESLCodeSubprograms(self, commandevent=None, commanddata=None):
        valid = self._control.modulesControl().addCode('ESL')

    def InsertFileCodeSubprograms(self, commandevent=None, commanddata=None):
        valid = self._control.modulesControl().addCode('file')

    def InsertPackage(self, commandevent=None, commanddata=None):
        valid = self._control.modulesControl().addPackage()

    def RunSimulation(self, commandevent=None, commanddata=None):
        try:
            valid = self._control.simulationControl().runSimulation()
        except:
            msg = "Run Simulation exception:\n" + traceback.format_exc()
            self._control.appendMessage(msg)
            Utils.bleep()

    def LaunchESLSEC(self, commandevent=None, commanddata=None):
        valid = self._control.simulationControl().launchESLSEC()

    def LaunchESLDisplays(self, commandevent=None, commanddata=None):
        valid = self._control.simulationControl().launchESLDisplays()

    def execute(self, cmd, getoutput=True, synchronise=True, callback=None, input=None):
        self._process = wx.Process()
        sync = wx.EXEC_SYNC ^ wx.EXEC_NODISABLE
        if not synchronise:
            sync = wx.EXEC_ASYNC
        if getoutput or input:
            self._process.Redirect()
        if callback:
            self._process.Bind(wx.EVT_END_PROCESS, callback)
        result = wx.Execute(cmd, sync, self._process)
        if input:
            input_stream = self._process.GetOutputStream()
            if input_stream:
                input_bytes = bytes(input, "utf-8")
                res = input_stream.Write(input_bytes, len(input_bytes))
                input_stream.close()
        lines = ''
        if getoutput and synchronise:
            lines = self.getCommandOutput()
        if synchronise or callback is None:
            self._process = None
        return result, lines

    def getCommandOutput(self):
        lines = ''
        if self._process:
            if self._process.IsInputAvailable:
                output = self._process.GetInputStream()
                if output:
                    if output.CanRead:
                        #lines = output.readlines(100)
                        while not output.Eof():
                            s = output.readline()
                            if not output.Eof():
                                if isinstance(s, bytes):
                                    lines += bytes.decode(s)
                                else:
                                    lines += str(s)
            if self._process.IsErrorAvailable:
                error = self._process.GetErrorStream()
                if error:
                    if error.CanRead:
                        # lines = output.readlines(100)
                        while not error.Eof():
                            s = error.readline()
                            if not error.Eof():
                                if isinstance(s, bytes):
                                    lines += bytes.decode(s)
                                else:
                                    lines += str(s)
            self._process = None
        return lines

    def showCommandOutput(self, cmd, retcode, lines):
        msg = 'Command "' + cmd + '" retcode=' + str(retcode) + ':\n'
        self._control.appendMessage(msg)
        self._control.appendMessage(lines)
        self._control.appendMessage('\n')

    def openTextEditor(self, filepath=''):
        synchronise = False  # if True edit is modal
        if not synchronise and self._textEditorOpenCmd:
            wx.MessageBox('Text editor already opened by ESL-Studio for command "' + self._textEditorOpenCmd + '"', 'Text Editor')
        else:
            textEditor = Config.getString('General/Text Editor')
            if textEditor:
                cmd = textEditor
                if '%s' in textEditor:
                    cmd = textEditor.replace('%s', filepath)
                elif filepath:
                    cmd = textEditor + ' ' + filepath
                if not synchronise:
                    self._textEditorOpenCmd = cmd
                retcode, lines = self.execute(cmd, getoutput=False, synchronise=synchronise, callback=self.checkOpenTextEditor)
                if synchronise and retcode != 0:
                    wx.MessageBox('Failed to invoke text editor command "'+cmd+'"', 'Text Editor')
            else:
                wx.MessageBox('No external Text Editor set in options/preferences', 'Text Editor')

    def checkOpenTextEditor(self, e):
        retcode = e.GetExitCode()
        if retcode != 0:
            wx.MessageBox('Failed to launch text editor command "' + self._textEditorOpenCmd + '"', 'Text Editor')
        self._textEditorOpenCmd = ""

    def textEditString(self, text=''):
        result = text
        textEditor = Config.getString('General/Text Editor')
        if textEditor:
            #wx.FileName. CreateTempFileName - cant find
            tmpFile, tmpName = tempfile.mkstemp(prefix='eslstudio', text=True)
            os.write(tmpFile, text)
            os.close(tmpFile)
            self.openTextEditor(tmpName)
            file = open(tmpName, 'r')
            if file:
                result = file.read()
                file.close()
        return result

    def ShowHelp(self, commandevent=None, commanddata=None):
        helpfile = APP_WEBSITE # default to ESL Software's homepage at present
        commandId = commandevent.GetId()
        commandDefn = self.commandDefnByCommandId[commandId]
        if commandDefn:
            infoXmlElement = commandDefn.commandXmlElement.getXmlElementByName("info")
            if infoXmlElement:
                help = infoXmlElement.getAttribute("help")
                if help:
                    helpfile = help
        Utils.openUrl(helpfile)

    def CheckESLStudioUpdates(self, commandevent=None, commanddata=None):
        msg = self._checkeslupdates(True)
        if msg:
            wx.MessageBox(msg)

    def CheckESLUpdates(self, commandevent=None, commanddata=None):
        msg = self._checkeslupdates(False)
        if msg:
            wx.MessageBox(msg)

    def _checkeslupdates(self, eslStudio=False):
        msg = ""
        cmd = "checkeslupdates"
        if sys.platform == "win32": cmd += ".exe"
        if shutil.which(cmd) is None:
            msg = "Cannot find the checkeslupdates program - check ESL installed"
        else:
            if eslStudio:
                cmd += " --product ESL-Studio --version "
                version = APPLICATION_VERSION_STRING
                if version.count(".") == 2:
                    version += ".0"
                cmd += version
            if Commands.CheckESLUpdates_options:
                cmd += " " + Commands.CheckESLUpdates_options
            pass
            retcode, lines = self.execute(cmd)
            msg = lines
        return msg

    def ShowAboutBox(self, commandevent=None, commanddata=None):
        dlg = AboutDlg.Instance(self._frame)
        dlg.ShowModal()

    def ShowSubprogram(self, commandevent=None, commanddata=None):
        page = self._control.currentCanvas()
        if page and commanddata:
            xmlElement = xut.xmlElement(commanddata)
            if xmlElement:
                if xmlElement.name() != 'objects':
                    xmlElement = xmlElement.getXmlElementByName("objects", True)
                if xmlElement:
                    callXmlElement = xmlElement.getXmlElementByName('entity')
                    if callXmlElement:
                        objectId = callXmlElement.getAttribute('id')
                        if objectId:
                            callEntity = self._application.getEntityForCanvasObjectIds(
                                page.canvasId(), objectId)
                            if callEntity and callEntity.isCall():
                                subprogramName = callEntity.getSubprogramName()
                                if subprogramName:
                                    subprogram = self._application.blockNames().get(subprogramName)
                                    if subprogram:
                                        moduleId = 0
                                        if isinstance(subprogram, CodeSubprogram):
                                            moduleId = subprogram.code().moduleId()
                                        else:
                                            moduleId = subprogram.moduleId()
                                        if moduleId:
                                            page = self._frame.viewManager().mainView().getModuleViewByModuleId(moduleId)
                                            if page:
                                                pageIndex = self._frame.viewManager().mainView().GetPageIndex(page)
                                                if pageIndex:
                                                    self._frame.viewManager().mainView().SetSelection(pageIndex)
                                                    if isinstance(subprogram, CodeSubprogram):
                                                        subprogram.code().findSubprogram(subprogramName)

    def ClearApplicationHistory(self, commandevent=None, commanddata=None):
        self._frame.applicationHistory().clearHistory()

    def RunCommand(self, commandevent=None, commanddata=None):
        #self._mainView.ShowWindowMenu()
        msg = "Give external command to run"
        if sys.platform == 'win32':
            msg += "\nuse cmd /c prior to internal (DOS) cmds"
        msg += "\nuse \"eval \" or \"exec \" prefix for python"
        msg += "\nuse \"async \" prefix for asynchronous launch"
        msg += "\nfor async commands use \"<<< \" followed by any input (characters) to the command"
        caption = "Run Command"
        dlg = wx.TextEntryDialog(self._frame, msg, caption)
        self._runCommandStackPosn = -1
        txtCtl = None
        for win in dlg.Children:
            if isinstance(win, wx.TextCtrl):
                txtCtl = win
                break
        if txtCtl:
            txtCtl.Bind(wx.EVT_KEY_DOWN, self.RunCommandOnKeyDown)
        dlg.ShowModal()
        cmd = dlg.GetValue()
        if cmd:
            self._runCommandStack.insert(0, cmd)
            synchronise = True
            if cmd.strip().find('eval ') == 0:
                cmd = cmd.replace('eval ', '', 1)
                retcode = 0
                try:
                    lines = str(eval(cmd))
                except Exception as e:
                    lines = "Exception: " + str(e)
            elif cmd.strip().find('exec ') == 0:
                cmd = cmd.replace('exec ', '', 1)
                retcode = 0
                try:
                    lines = str(exec(cmd))
                except Exception as e:
                    lines = "Exception: " + str(e)
            else:
                if cmd.strip().find('async ') == 0:
                    cmd = cmd.replace('async ', '', 1)
                    synchronise = False
                input_string = None
                if not synchronise:
                    input_pos = cmd.find("<<<")
                    if input_pos != -1:
                        input_string = cmd[input_pos+3:]
                        cmd = cmd[:input_pos]
                if synchronise:
                    retcode, lines = self.execute(cmd, synchronise=synchronise, callback=self.RunCommandCallback, input=input_string)
                else:
                    retcode, lines = self.execute(cmd, synchronise=synchronise, callback=self.RunCommandCallback, input=input_string)
                    msg = 'Launched command "' + self._runCommandStack[0] + '"\n'
                    self._control.appendMessage(msg)
            if synchronise:
                self.showCommandOutput(cmd, retcode, lines)

    def RunCommandCallback(self, e):
        msg = 'RunCommand "' + self._runCommandStack[0] + '" exitCode:'+str(e.GetExitCode())
        if self._process:
            lines = self.getCommandOutput()
            msg += '\n' + lines
        self._control.appendMessage(msg)

    def RunCommandOnKeyDown(self, evt):
        keyCode = evt.GetKeyCode()
        modifiers = evt.GetModifiers()
        if keyCode == wx.WXK_UP or keyCode == wx.WXK_DOWN:
            recalledCommand = ""
            lenStack = len(self._runCommandStack)
            if lenStack > 0:
                if modifiers == 0:
                    if keyCode == wx.WXK_UP: # go back into past cmds (increase stack pointer)
                        if self._runCommandStackPosn < lenStack - 1:
                            self._runCommandStackPosn += 1
                            recalledCommand = self._runCommandStack[self._runCommandStackPosn]
                    elif keyCode == wx.WXK_DOWN:
                        if self._runCommandStackPosn > 0:
                            self._runCommandStackPosn -= 1
                            recalledCommand = self._runCommandStack[self._runCommandStackPosn]
            if recalledCommand:
                dlg = evt.GetEventObject()
                dlg.SetValue(recalledCommand)
        else:
            evt.Skip(True)

    #def Test1(self, commandevent=None, commanddata=None):
    #    #self._mainView.ShowWindowMenu()
    #    page = self._control.currentCanvas()
    #    if page:
    #        dlg = wx.TextEntryDialog(self._frame, "Give Canvas Action XML string")
    #        dlg.ShowModal()
    #        ans = dlg.GetValue()
    #        if ans:
    #            page.Action(ans)

    def SaveAlterationsStack(self, commandevent=None, commanddata=None):
        wildcard = "Alt files (*.alt)|*.alt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self._frame, "Save current Undo/Redo stack to file",
                            os.getcwd(), "", wildcard,
                            style = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            if file:
                self._control.alterationStack().saveAlterationsStack(file)

    def RecordAlterations(self, commandevent=None, commanddata=None):
        wildcard = "Alt files (*.alt)|*.alt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self._frame, "Record alterations to file",
                            os.getcwd(), "", wildcard,
                            style = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            ans = dlg.GetPaths()
            if ans and len(ans) == 1:
                self._control.alterationStack().recordAlterationsToFile(ans[0], append=False) # Currently never append

    def StopRecordingOrReplayAlterations(self, commandevent=None, commanddata=None):
        self._control.alterationStack().stopRecordingOrReplayingAlterations()

    def PlayAlterations(self, commandevent=None, commanddata=None):
        wildcard = "Alt files (*.alt)|*.alt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self._frame, "Play recorded alterations from file",
                            os.getcwd(), "", wildcard,
                            style = wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            if file:
                interval = 1000
                interval = wx.GetNumberFromUser("Give play-back interval (milli-secs)", "", "", interval, 0, 10000)
                if interval != -1:
                    self._control.alterationStack().playAlterationsFromFile(file, interval)
