#! /usr/bin/python

import os
import sys
import shutil

import wx

import esl_diagram.xmlutil as xut

from .application.setupinfo import SetupExecCommand, SetupTranslationLang
from .application.displaydefinition import DisplayDefinition
from .application.simulationparameters import ApplicationAlgoValues, ApplicationDefaultSimulationParameters
from .application.setupinfo import SetupInfo
from .esl import parseesl

ESL_SEC_PATH = "esl_sec"
if sys.platform == "win32": ESL_SEC_PATH += ".exe"
ESL_DISPLAYS_PATH = "esl_displays"
if sys.platform == "win32": ESL_DISPLAYS_PATH += ".exe"

class SimulationControl(object):
    def __init__(self, control):
        self._parseEsl = parseesl.ParseEsl()
        self._control = control
        self._gotESLSEC = False
        self._gotESLDisplays = False
        self._simulationDirectory = ""
        self._secSpecFile = ""
        self._secPriorSpecXmlStr = ""
        self._displayIconDisplays = []
        self._process = None
        self._appBase = ""

    def gotESLSEC(self):
        return self._gotESLSEC

    def gotESLDisplays(self):
        return self._gotESLDisplays

    def setup(self):
        self._frame = self._control.frame()
        self._application = self._frame.application()
        self._commands = self._frame.commands()
        self._checkExternalSEC()

    def runSimulation(self):
        self._appBase = ""
        setupData = self._application.setupInfo().data()
        runDirect = not setupData.runWithSEC or not self._gotESLSEC
        esl, errMsg = self._control.generate().GenerateESL(runDirect)
        if esl:
            appFilepath = self._application.filepath()
            writeFile = True
            saveApp = False
            saved = False
            if self._application.changed():
                saveApp = True
            msg = ""
            if saveApp:
                msg += "Application has changed - will be saved\n"
            if msg:
                msg += "Do you want to continue"
                dlg = wx.MessageDialog(self._frame,
                                       msg,
                                       "Run Simulation",
                                       wx.YES_NO | wx.ICON_INFORMATION)
                ans = dlg.ShowModal()
                if ans != wx.ID_YES:
                    writeFile = False
                    saveApp = False
            if saveApp:
                saved = self._commands.SaveApplication()
            if (not saveApp or saved) and writeFile:
                appFilepath = self._application.filepath()
                if appFilepath:
                    self._appBase = os.path.splitext(os.path.basename(appFilepath))[0]
                    sanitisedAppBase = self._appBase.replace(".", "_")
                    sanitisedAppBase = sanitisedAppBase.replace(" ", "_")
                    if sanitisedAppBase != self._appBase:
                        msg = "Changed base-name for generated ESL file from that of application (dots and spaces replaced) to \""+sanitisedAppBase+".esl\"\n"
                        self._control.appendMessage(msg)
                        self._appBase = sanitisedAppBase
                        if os.path.exists(sanitisedAppBase+".eslstudio"):
                            msg += "Note: There is another application with this base-name\n"
                            msg += "Do you want to continue"
                            dlg = wx.MessageDialog(self._frame,
                                                   msg,
                                                   "Run Simulation",
                                                   wx.YES_NO | wx.ICON_INFORMATION)
                            ans = dlg.ShowModal()
                            if ans != wx.ID_YES:
                                self._appBase = ""
                    if self._appBase:
                        eslFilepath = self._appBase + ".esl"
                        f = None
                        try:
                            f = open(eslFilepath, "w")
                        except Exception:
                            msg = "Cannot write to file \"" + eslFilepath +"\"\n"
                            self._control.appendMessage(msg)
                        if f and not f.closed:
                            f.write(esl)
                            f.close()
                            if setupData.viewCode:
                                self._commands.viewEslFilePage(eslFilepath)
                            retcode = 0
                            if retcode == 0:
                                cmd = setupData.buildCommand(justCompile=not runDirect)
                                if cmd:
                                    cmd = self._commandSubstitutions(cmd)
                                    cmdList = cmd.split("&&")
                                    for cmdStr in cmdList:
                                        cmdStr = cmdStr.strip()
                                        if cmdStr and retcode == 0:
                                            retcode, lines = self._commands.execute(cmdStr)
                                            self._commands.showCommandOutput(cmdStr, retcode, lines)
                                else:
                                    msg = "no build command"
                                    if not SetupInfo.esl():
                                        msg += " - \"esl\" command not found"
                                    msg += "\n"
                                    self._control.appendMessage(msg)

                            if not setupData.generateOnly and retcode == 0:
                                cmd = setupData.runCommand()
                                if cmd:
                                    cmd = self._commandSubstitutions(cmd)
                                    if runDirect:
                                        hasReadIn = self._parseEsl.hasReadStatement(esl)
                                        if hasReadIn:
                                            msg = "Generated simulation contains direct input - cannot run directly from ESL-Studio.\n"
                                            msg += "Run from command line or specify to run with ESL-SEC (Simulation/Setup).\n"
                                            self._control.appendMessage(msg)
                                        else:
                                            synchronise = False
                                            self._control.setMode("browsing")
                                            input = "Quit\n"  # input is there to exit from Interact if the ESL simulation run has a runtime error - the newline is needed in Windows
                                            retcode, lines = self._commands.execute(cmd, synchronise=synchronise,
                                                                                    callback=self._postExecuteDirect, input=input)
                                    else:
                                        self._invokeESL_SEC()
                                        pass
        elif errMsg:
            self._control.appendMessage(errMsg)

    def _postExecuteDirect(self, e):
        retcode = e.GetExitCode()
        lines = self._commands.getCommandOutput()
        self._commands.showCommandOutput("", retcode, lines)
        self._control.setMode("editing")
        pass

    def _commandSubstitutions(self, cmd):
        subst = "{AppBase}"
        value = self._appBase
        cmd = cmd.replace(subst, value)
        return cmd

    def _checkExternalSEC(self):
        self._gotESLSEC = shutil.which(ESL_SEC_PATH) != None
        self._gotESLDisplays = shutil.which(ESL_DISPLAYS_PATH) != None
        if not self._gotESLSEC or not self._gotESLDisplays:
            msg = "Cannot find the"
            if not self._gotESLSEC and self._gotESLDisplays:
                msg += " ESL-SEC program\n"
            elif self._gotESLSEC and not self._gotESLDisplays:
                msg += " ESL-Displays program\n"
            else:
                msg += " ESL-SEC and ESL-Displays programs\n"
            self._control.appendMessage(msg)

    def _invokeESL_SEC(self):  # Modal for current model
        setupData = self._application.setupInfo().data()

        # Do we have a previous sec spec file saved
        savedSpecXmlStr = setupData.get_esl_sec_specification()
        generatedSpecXmlStr = self.generateSpecification(savedSpecXmlStr, setupData)
        self._secPriorSpecXmlStr = generatedSpecXmlStr

        # Will need a unique name temp file on current directory
        self._simulationDirectory = os.getcwd()
        self._secSpecFile = self._appBase + "-" + str(os.getpid()) + ".sec"

        f = None
        try:
            f = open(self._secSpecFile, "w")
        except Exception:
            msg = "Cannot write to file \"" + self._secSpecFile + "\"\n"
            self._control.appendMessage(msg)
        if f and not f.closed:
            f.write('<?xml version="1.0"?>\n' + generatedSpecXmlStr + "\n")
            f.close()

        cmdStr = ESL_SEC_PATH
        cmdStr += " -f " + self._secSpecFile
        #sync = wx.EXEC_SYNC | wx.EXEC_NODISABLE # works (seemingly) - but later causes block
        sync = wx.EXEC_ASYNC
        self._control.setMode("browsing")
        if sync == wx.EXEC_ASYNC:
            self._process = wx.Process()
            self._process.Bind(wx.EVT_END_PROCESS, self._postExecuteESLSEC)
            result = wx.Execute(cmdStr, sync, self._process)
        else:
            result = wx.Execute(cmdStr, sync)
            self._postExecuteESLSEC()
        pass

    def _postExecuteESLSEC(self, e=None):
        status = 0
        if e: status = e.GetExitCode()
        os.chdir(self._simulationDirectory) # ensure working directory as it was when started simulation.
        # Read in/load the spec file.
        specDoc = xut.XmlElement()
        specDoc.loadFromFile(self._secSpecFile)
        os.unlink(self._secSpecFile)
        # See if spec file changed at all (i.e. was saved when closed ESL-SEC).
        specXmlStr = specDoc.xml("\t")
        if specXmlStr != self._secPriorSpecXmlStr:
            updatedSpecXmlStr = self.updateApplication(self._secPriorSpecXmlStr, specXmlStr)
            self._application.setupInfo().data().set_esl_sec_specification(updatedSpecXmlStr)
            self._commands.SaveApplication()
        self._control.setMode("editing")
        self._process = None
        pass

    def launchESLSEC(self): # Detached process for any simulation
        if self._gotESLSEC:
            wx.Execute(ESL_SEC_PATH)
        else:
            self._control.appendMessage("ESL-SEC not available")
        pass

    def launchESLDisplays(self):  # Detached process
        if self._gotESLDisplays:
            wx.Execute(ESL_DISPLAYS_PATH)
        else:
            self._control.appendMessage("ESL-Displays not available")
        pass

##################### should these be in a separate module

    def generateSpecification(self, savedSpecXmlStr, setupData):
        if savedSpecXmlStr == "":
            savedSpecXmlStr = "<sec-specification/>\n"

        specXmlDoc = xut.XmlElement(savedSpecXmlStr)

        self.setupXml(specXmlDoc, setupData)
        ####self.simParametersXml(specXmlDoc)   #### TODO no longer do this - or do we?
        self.displaysXml(specXmlDoc)

        generatedSpecXmlStr = specXmlDoc.xml("\t")
        return generatedSpecXmlStr

    def setupXml(self, specXmlDoc, setupData):
        specXmlDoc.removeNamedChild("setup")
        setupStr = self.generateSetup(setupData)
        if setupStr:
            doc = xut.XmlElement(setupStr)
            specXmlDoc.prependChild(doc)

    def generateSetup(self, setupData):
        xmlStr = ""
        simulation = self._appBase
        if setupData.execCommand != SetupExecCommand.CUSTOM:
            simulation += ".esl"
        xmlStr += "\t<setup>\n\t\t<simulation-file><![CDATA["+simulation+"]]></simulation-file>\n"
        executeCommand = ""
        langStr = ""
        extraStr = ""
        includeStr = setupData.addnlLinkObjs
        customRunCommand = ""
        if setupData.execCommand == SetupExecCommand.TRANSLATE:
            executeCommand = "compile-translate-link-execute"
            if setupData.translation == SetupTranslationLang.CPP:
                langStr = "cplusplus"
            elif setupData.translation == SetupTranslationLang.FORTRAN:
                langStr = "fortran"
            if setupData.translation == SetupTranslationLang.CPP and setupData.single:
                extraStr += " single=\"true\""
            if setupData.x32bit:
                extraStr += " x32bit=\"true\""
            if setupData.translation == SetupTranslationLang.CPP and setupData.gcc:
                extraStr += " gcc=\"true\""
        elif setupData.execCommand == SetupExecCommand.CUSTOM:
            executeCommand = "custom"
            customRunCommand = setupData.customRunCommand
        if executeCommand:
            xmlStr += "\t\t<execution command=\"" + executeCommand
            if setupData.execCommand == SetupExecCommand.TRANSLATE and langStr:
                xmlStr += "\" translation=\"" + langStr
            xmlStr += "\"/>\n"
        if setupData.execCommand == SetupExecCommand.TRANSLATE:
            if includeStr:
                xmlStr += "\t\t<addnl-link-objs>\n\t\t\t<![CDATA["+includeStr+"]]>\n\t\t</addnl-link-objs>\n"
            if extraStr:
                xmlStr += "\t\t<extra-options" + extraStr + "/>\n"
        if setupData.execCommand == SetupExecCommand.CUSTOM and customRunCommand:
            xmlStr += "\t\t<custom-run-command>\n\t\t\t<![CDATA[" + customRunCommand + "]]>\n\t\t</custom-run-command>\n"
        xmlStr += "\t</setup>\n"
        return xmlStr

    """def simParametersXml(self, specXmlDoc):                      #### TODO
        specXmlDoc.removeNamedChild("simulation-parameters")
        parametersStr = self.generateSimulationParameters()
        if parametersStr:
            doc = xut.XmlElement(parametersStr)
            setupElement = specXmlDoc.getXmlElementByName("setup")
            specXmlDoc.insertChildAfter(doc, setupElement)"""

    """def generateSimulationParameters(self):                      #### TODO
        xmlStr = ""
        simPars = self._application.simulationParameters()
        for simPar in list(simPars.parameters().values()):
            simParTag = simPar.eslname()
            different = True
            defaultValue = simPars.defaultValue(simParTag)
            if simPar.valueStr() == defaultValue:
                different = False
            elif (ApplicationDefaultSimulationParameters[simParTag][0] == 'Real' and
                  float(simPar.valueStr()) == float(defaultValue)):
                different = False
            if different:
                value = simPar.valueStr()
                if simParTag == "ALGO":
                    value = ApplicationAlgoValues[value]
                xmlStr += "\t\t<parameter eslname=\"" + simParTag + "\" value=\"" + value + "\"/>\n"
        if xmlStr:
            xmlStr = "\t<simulation-parameters>\n" + xmlStr + "  </simulation-parameters>\n"
        return xmlStr"""

    def displaysXml(self, specXmlDoc):
        displayDefinitionsStr = ""
        displayDefinitionsNode = specXmlDoc.getXmlElementByName("display-definitions")
        if displayDefinitionsNode:
            displaysList = displayDefinitionsNode.getChildren().copy()
            for display in displaysList:
                if display.getAttribute("display-icon"):
                    displayDefinitionsNode.removeChildElement(display)
            displayDefinitionsStr = displayDefinitionsNode.xml()
        iconDisplaysStr = self.generateIconDisplays()
        if iconDisplaysStr:
            if not displayDefinitionsNode:
                displayDefinitionsStr = iconDisplaysStr
            else:
                iconDisplaysNode = xut.XmlElement(iconDisplaysStr)
                for xmlElement in iconDisplaysNode.getChildren():
                    displayDefinitionsNode.appendChild(xmlElement)
                displayDefinitionsStr = displayDefinitionsNode.xml()
        specXmlDoc.removeNamedChild("display-definitions")
        if displayDefinitionsStr:
            displayDefinitionsNode = xut.XmlElement(displayDefinitionsStr)
            specXmlDoc.appendChild(displayDefinitionsNode)
        pass

    def updateApplication(self, priorSpecXmlStr, specXmlStr):
        specXmlDoc = xut.XmlElement(specXmlStr)
        priorXmlDoc = xut.XmlElement(priorSpecXmlStr)

        specSimPars = ""
        priorSimPars = ""
        if specXmlDoc.getXmlElementByName("simulation-parameters"): specSimPars = specXmlDoc.getXmlElementByName("simulation-parameters").xml()
        if priorXmlDoc.getXmlElementByName("simulation-parameters"): priorSimPars = priorXmlDoc.getXmlElementByName("simulation-parameters").xml()
        if specSimPars != priorSimPars:
            self.updateSimulationParameters(specXmlDoc)

        specDispDefs = ""
        priorDispDefs = ""
        if specXmlDoc.getXmlElementByName("display-definitions"): specDispDefs = specXmlDoc.getXmlElementByName("display-definitions").xml()
        if priorXmlDoc.getXmlElementByName("display-definitions"): priorDispDefs = priorXmlDoc.getXmlElementByName("display-definitions").xml()
        if specDispDefs != priorDispDefs:
            self.updateIconDisplays(specXmlDoc)

        # Remove any icon displays in XML to be saved at this stage.
        displayDefinitionsNode = specXmlDoc.getXmlElementByName("display-definitions")
        if displayDefinitionsNode:
            displaysList = displayDefinitionsNode.getChildren().copy()
            for display in displaysList:
                if display.getAttribute("display-icon"):
                    displayDefinitionsNode.removeChild(display)
            if len(displayDefinitionsNode.getChildren()) == 0:
                specXmlDoc.removeNamedChild("display-definitions")

        # Remove setup and simulation parameters.
        specXmlDoc.removeNamedChild("setup")
        specXmlDoc.removeNamedChild("simulation-parameters")

        updatedSpecXmlStr = ""
        if len(specXmlDoc.getChildren()) > 0:
            updatedSpecXmlStr = specXmlDoc.xml("\t")
        return updatedSpecXmlStr

    def updateSimulationParameters(self, specXmlDoc):
        simulationparametersview = self._frame.viewManager().simulationParametersView()
        simParsNode = specXmlDoc.getXmlElementByName("simulation-parameters")
        ####simPars = self._application.simulationParameters()      #### TODO consider what (& how) to handle saved sim pars
        """for simPar in list(simPars.parameters().values()):
            simParTag = simPar.eslname()
            value = simPars.defaultValue(simParTag)
            xmlElement = simParsNode.findXmlElementWithAttribute("parameter", "eslname", simParTag)
            if xmlElement:
                value = xmlElement.getAttribute("value")
                if simParTag == "ALGO":
                    for key in ApplicationAlgoValues:
                        if value == ApplicationAlgoValues[key]:
                            value = key
                            break
            simPar.set_valueStr(value)
            #### TODO something - now that simParTag will have to cope with a specific module
            #### that may include raising a message saying cant do the application update
            simulationparametersview.updateSimulationParameters(simParTag, value) # we have to synchronise the view"""

    def generateIconDisplays(self):
        iconDisplaysStr = ""
        self._displayIconDisplays = []
        diagramModules = list(self._application.models().values()) + list(self._application.submodels().values()) + list(self._application.segments().values())
        for subprogram in diagramModules:
            diagramInfo = subprogram.diagramInfo()
            if diagramInfo:
                for display in list(diagramInfo.displayDefinitions().values()):
                    if display.display == DisplayDefinition.Display_values[0] or display.display == DisplayDefinition.Display_values[2]:
                        self._displayIconDisplays.append(display)
        for i in range(len(self._displayIconDisplays)):
            display = self._displayIconDisplays[i]
            appModule = display.parent().parent()
            genModule = self._control.generate().genModules().get(appModule)
            genDiagramInfo = genModule.genDiagramInfo()
            variableRefs = genDiagramInfo.getDisplayVariableRefs(display)
            if len(variableRefs):
                iconDisplaysStr += display.saveForSEC(i + 1, variableRefs)
        if iconDisplaysStr:
            iconDisplaysStr = "<display-definitions>" + iconDisplaysStr + "</display-definitions>"
        return iconDisplaysStr

    def updateIconDisplays(self, specXmlDoc):
        displayDefinitionsNode = specXmlDoc.getXmlElementByName("display-definitions")
        if displayDefinitionsNode:
            displaysXmlList = displayDefinitionsNode.getChildren()
            for displayXml in displaysXmlList:
                displayIcon = displayXml.getAttribute("display-icon")
                if displayIcon:
                    display = self._displayIconDisplays[int(displayIcon) - 1]
                    display.updateFromSEC(displayXml)
