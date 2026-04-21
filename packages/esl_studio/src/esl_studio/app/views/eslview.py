#! /usr/bin/python

import os
import re
import sys

import wx
import wx.stc as stc

from .view import View
from .stc import Stc
from ..propertieschangeevent import PropertiesChangeEvent
from ..application.setupinfo import SetupInfo
from . validationview import ValidationView

class EslView(View, Stc): #wx.TextCtrl):
    def __init__(self, parent):
        Stc.__init__(self, parent)
        View.__init__(self, parent, 'page')
        self._showingContextMenu = False
        self.Hide()
        self.registerExtraEvents()

    def registerExtraEvents(self):
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, self.showEslViewContextMenu)
        self.Bind(stc.EVT_STC_MODIFIED, self.OnModified)

    def setText(self, text, extn='.esl'):
        self.setStcText(text, extn)

    def OnKillFocus(self, focusEvent):
        if not self.readOnly:
            if not self._showingContextMenu:
                self.updateEsl()
            else:
                self._showingContextMenu = False
        focusEvent.Skip()

    def OnLeaveWindow(self, mouse_event):
        if not self.readOnly:
            if not self._showingContextMenu:
                self.updateEsl()
                pass
            else:
                self._showingContextMenu = False
            mouse_event.Skip()
        pass

    def getModule(self):
        module = None
        isModule = getattr(self, "moduleId", False)
        if isModule:
            moduleId = self.moduleId()
            frame = wx.GetApp().frame()
            application = frame.application()
            module = application.getModuleById(moduleId)
        return module

    def showEslViewContextMenu(self, event):
        isModule = getattr(self, "moduleId", False)
        if isModule and not self.readOnly:
            self._showingContextMenu = True
        self.showContextMenu(event)

    def updateEsl(self):
        if not self.inModalDlg:
            module = self.getModule()
            if module:
                frame = wx.GetApp().frame()
                eslText = self.GetText()
                oldEslText = module.eslText()
                if eslText != oldEslText:
                    propertiesControl = frame.control().propertiesControl()
                    # update the actual property
                    propertiesControl.setCodeProperty(module.moduleId(), 'ESL', eslText, change=False)
                    # emulate a property change
                    propertieschange_event = PropertiesChangeEvent(
                        'module-property',
                        module.moduleId(),
                        'ESL',
                        eslText,
                        oldEslText)
                    valid = propertiesControl.onPropertiesChange(propertieschange_event,
                        suppressSelectionChange=True)
                    if not valid:
                        self.setText(oldEslText)

    def OnModified(self, styledTextEvent):
        modificationType = styledTextEvent.GetModificationType()
        if modificationType & stc.STC_MOD_INSERTTEXT or modificationType & stc.STC_MOD_DELETETEXT:
            #modified = self.IsModified()
            uncommitted = False
            invalid = False
            module = self.getModule()
            if module:
                eslText = self.GetText()
                oldEslText = module.eslText()
                uncommitted = eslText != oldEslText
                invalid = not module.valid()
            #print("EslView.OnModified - modified="+str(modified)+" uncommitted="+str(uncommitted))
            caption = self.caption()
            marked = caption.startswith("* ") or caption.startswith("! ")
            if marked:
                caption = caption[2:]
            if uncommitted:
                caption = "* "+caption
            elif invalid:
                caption = "! "+caption
            self.set_caption(caption)

    def updateView(self, module=None):
        #style = self.GetCaretStyle()
        #if style == stc.STC_CARETSTYLE_INVISIBLE:
        #    style = stc.STC_CARETSTYLE_LINE
        #    self.SetCaretStyle(style)
        #pos = self.GetInsertionPoint()
        #self.SetInsertionPoint(pos)
        #self.SetCurrentPos(pos)
        #self.EnsureCaretVisible()
        self.SetFocus()
        pass

    def doShowCodeChecks(self, conditionalPaneAlreadyShowing=False):
        if not self.inModalDlg:
            module = self.getModule()
            if module and module.moduleType() == "code":
                viewName = "code_check_"+str(module.moduleId())
                pane = self._frame.viewManager().getView(viewName)
                if pane is None:
                    if not conditionalPaneAlreadyShowing:
                        pane = ValidationView(self, "pane", module)
                        self._frame.viewManager().addPane(pane, viewName)
                elif conditionalPaneAlreadyShowing:
                    paneShowing = self._frame.viewManager().viewIsShowing(viewName)
                    if not paneShowing:
                        pane = None
                if pane is not None:
                    parseMessages = module.parseMessages()
                    msg = "Code check messages not available"
                    if parseMessages is not None:
                        if not parseMessages:
                            msg = module.identification(showSubType=True) + " has no code check messages"
                        else:
                            msg = module.identification(showSubType=True) + " code check messages:\n"
                            msg += parseMessages
                    #dlg = wx.MessageDialog(self, msg, "Code checks")
                    #ans = self.showModalDlg(dlg)
                    caption = module.identification(showSubType=True) + " Code Check"
                    self._frame.viewManager().setPaneCaption(pane, caption)
                    self._frame.auiManager().Update()
                    pane.setText(msg)
                    self._frame.viewManager().showView(viewName)

    def runESLCompiler(self):
        if not self.inModalDlg:
            module = self.getModule()
            if module and module.moduleType() == "code":
                # Use a temp created ESL file - even for code-type 'file'
                eslText = self.GetText()
                if eslText:
                    filebase = "code_"+str(module.moduleId())+"_"+str(os.getpid())
                    eslfile = filebase+".esl"
                    f = None
                    try:
                        f = open(eslfile, "w")
                    except Exception:
                        msg = "Cannot write ESL file \"" + eslfile + "\" on directory \""+os.getcwd()+"\"\n"
                        self._control.appendMessage(msg)
                    if f and not f.closed:
                        f.write(eslText)
                        f.close()
                        # invoke the ESL Compiler to create the lst file
                        esl = SetupInfo.esl()
                        if esl:
                            cmdStr = esl + " -c "+filebase+" -noprompt -lst"
                            retcode, lines = self._control.frame().commands().execute(cmdStr) # synchronised
                            self.showESLCompilerResults(filebase, retcode, lines)
                        else:
                            msg = "Cannot find the ESL command"
                            self.openESLCompilerResultsText(msg)

    def openESLCompilerResultsText(self, text):
        module = self.getModule()
        viewName = "code_comp_"+str(module.moduleId())
        pane = self._frame.viewManager().getView(viewName)
        caption = module.identification(showSubType=True) + " Code Compilation"
        if pane is None:
            pane = ValidationView(self, "pane", module)
            self._frame.viewManager().addPane(pane, viewName)
        self._frame.viewManager().setPaneCaption(pane, caption)
        self._frame.auiManager().Update()
        pane.setText(text)
        self._frame.viewManager().showView(viewName)

    def hideESLCompilerResultsText(self):
        module = self.getModule()
        viewName = "code_comp_"+str(module.moduleId())
        pane = self._frame.viewManager().getView(viewName)
        if pane is not None:
            self._frame.viewManager().showView(viewName, showing=False)

    def showESLCompilerResults(self, filebase, retcode, lines):
        module = self.getModule()
        lstfile = filebase + ".lst"
        listing = ""
        msgs = ""
        f = None
        try:
            f = open(lstfile, "r")
        except Exception:
            msg = "Cannot read ESL Compiler listing file \"" + lstfile + "\"\n"
            self._control.appendMessage(msg)
        if f and not f.closed:
            listing = f.read()
            f.close()
        if listing:
            msgs = self.scanCompilerResults(listing)
            if msgs:
                results = module.identification(showSubType=True) + " ESL Compiler messages:\n"
                results += msgs
            else:
                results = module.identification(showSubType=True) + " ESL Compiler has no messages"
        else:
            results = "ESL Compiler return code=" + str(retcode) + " output:\n"
            results += lines
        results += "\n"
        #dlg = wx.MessageDialog(self, results, "Compiler results")
        #ans = self.showModalDlg(dlg)
        # remove any of these files
        if os.path.exists(filebase+".esl"):
            os.remove(filebase+".esl")
        if os.path.exists(filebase+".hcd"):
            os.remove(filebase+".hcd")
        if os.path.exists(filebase+".lst"):
            os.remove(filebase+".lst")
        # show in pane
        self.openESLCompilerResultsText(results)

    def scanCompilerResults(self, results:str) -> str:
        regexOptions = re.DOTALL# | re.MULTILINE #
        msgs = ""
        #starsMatches = re.finditer(r"^\*\*\*\*\s+", results, regexOptions)
        compilerMsgPattern = r"\n\*\*\*\* ?([^\n]*)\n"  # line 1 group 1 - blank, or name or column-indicator
        compilerMsgPattern += r"\*\*\*\* (ERROR|WARNING)( Line )?(\d+)?\/?([^\n]*)\n"  # line 2 group 2 - ERROR|WARNING, group 4 - outermost line#, group 5 - inclusion line#(s)
        compilerMsgPattern += r"\*\*\*\* ?([^\n]*)\n"  # line 3 group 6 - blank or actual-msg
        msgMatches = re.finditer(compilerMsgPattern, results, regexOptions)
        for msgMatch in msgMatches:
            line = -1
            column = -1
            name = ""
            nameOrColumnIndicator = msgMatch[1]
            if nameOrColumnIndicator:
                if nameOrColumnIndicator.strip() == "!":
                    column = len(nameOrColumnIndicator) - 9    # to locate cursor in STC (0 for cursor at beginning of line, 1 for *after* first char - i.e. before 2nd)
                else:
                    name = nameOrColumnIndicator
            msgType = msgMatch[2]
            lineStr = msgMatch[4]
            if lineStr:
                line = int(lineStr)
            inclusionLines = msgMatch[5]
            msgStr = msgMatch[6]

            # if valid msg all features set (other than column)
            if msgType != "" and line != -1 and msgStr != "":
                # prune out "no keyword eg STUDY"
                if msgStr.find("no keyword eg STUDY") == -1:
                    #if column < 0:
                    #    column = 0 # to locate cursor at beginning of line
                    msgs += msgType+": "
                    if name:
                        msgs += name + " - "
                    msgs += msgStr+" at line "+str(line)
                    if not inclusionLines and column >= 0:
                        msgs += ":"+str(column)
                    if inclusionLines:
                        msgs += " (inclusion line(s) "+inclusionLines+")"
                    msgs += "\n"
        return msgs
