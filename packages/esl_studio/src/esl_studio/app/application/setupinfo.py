#! /usr/bin/python

import sys
from enum import Enum
import shutil

from .. import utils as Utils
from .module import Module

class SetupExecCommand(Enum):
    INTERPRET = 1
    TRANSLATE = 2
    CUSTOM = 3

class SetupTranslationLang(Enum):
    CPP = 1
    FORTRAN = 2

class SetupInfoData(object):
    def __init__(self):
        self.generateOnly = False
        self.viewCode = False
        self.runWithSEC = True
        self.execCommand = SetupExecCommand.INTERPRET
        self.translation = SetupTranslationLang.CPP
        self.single = False
        self.x32bit = False
        self.gcc = False
        self.addnlLinkObjs = ""
        self.customRunCommand = ""
        self.esl_sec_specification = ""

    def copy(self, data):
        self.generateOnly = data.generateOnly
        self.viewCode = data.viewCode
        self.runWithSEC = data.runWithSEC
        self.execCommand = data.execCommand
        self.translation = data.translation
        self.single = data.single
        self.x32bit = data.x32bit
        self.gcc = data.gcc
        self.addnlLinkObjs = data.addnlLinkObjs
        self.customRunCommand = data.customRunCommand
        self.esl_sec_specification = data.esl_sec_specification

    def get_esl_sec_specification(self):
        eslSecXmlStr = self.esl_sec_specification
        eslSecXmlStr = eslSecXmlStr.replace("{![CDATA[", "<![CDATA[")
        eslSecXmlStr = eslSecXmlStr.replace("]]}", "]]>")
        return eslSecXmlStr

    def set_esl_sec_specification(self, eslSecXmlStr):
        eslSecXmlStr = eslSecXmlStr.replace("<![CDATA[", "{![CDATA[")
        eslSecXmlStr = eslSecXmlStr.replace("]]>", "]]}")
        self.esl_sec_specification = eslSecXmlStr

    def buildCommand(self, justCompile=False):
        command = ""
        esl = SetupInfo.esl()
        if esl:
            if self.generateOnly or justCompile:
                # Lets try compile
                command = esl + " -c {AppBase} -noprompt"
            else:
                if self.execCommand == SetupExecCommand.INTERPRET:
                    command = esl + " -c {AppBase} -noprompt"
                elif self.execCommand == SetupExecCommand.TRANSLATE:
                    extra = ""
                    if self.translation != SetupTranslationLang.FORTRAN:
                        if self.single: extra += " -single"
                    if self.x32bit: extra += " -32bit"
                    if self.translation != SetupTranslationLang.FORTRAN:
                        if self.gcc and sys.platform == 'win32':
                            extra += " -gcc"
                    trans = "cc"
                    if self.translation == SetupTranslationLang.FORTRAN: trans = "f"
                    command = (esl + " -c {AppBase} -noprompt && " +
                        esl + " -t"+trans+" {AppBase} && " +
                        esl + " -"+trans+" {AppBase}"+extra+" && " +
                        esl + " -"+trans+"l {AppBase}"+extra)
                    if self.addnlLinkObjs:
                        command += self.addnlLinkObjs
        return command

    def runCommand(self):
        command = ""
        if not self.generateOnly:
            esl = SetupInfo.esl()
            if esl:
                gui = ""
                if self.runWithSEC:
                    gui = " -gui"
                if self.execCommand == SetupExecCommand.INTERPRET:
                    command = esl + " -i {AppBase}" + gui
                elif self.execCommand == SetupExecCommand.TRANSLATE:
                    command = esl + " -x {AppBase}" + gui
                elif self.execCommand == SetupExecCommand.CUSTOM:
                    command = self.customRunCommand
        return command

    def __str__(self):
        result = ("<SetupInfoData "+
            #TEMP
            str(self.generateOnly)+"|"+
            str(self.viewCode)+"|"+
            str(self.runWithSEC)+"|"+
            str(self.execCommand)+"|"+
            str(self.translation)+"|"+
            str(self.single)+"|"+
            str(self.x32bit)+"|"+
            str(self.gcc)+"|"+
            str(self.addnlLinkObjs)+"|"+
            str(self.customRunCommand)+"|"+
            str(self.esl_sec_specification) + ">")
        return result

class SetupInfo(Module):

    _esl_command = "esl"
    if sys.platform == "win32":
        _esl_command += ".bat"
    _esl = ""

    def __init__(self, application, moduleId):
        Module.__init__(self, application, moduleId, 'setup-info')
        self._application = application
        self._data = SetupInfoData()

    def data(self):
        return self._data

    def setData(self, data):
        self._data = data

    def load(self):
        setupView = self._application.frame().viewManager().setupView()
        self._data = SetupInfoData()
        setupXmlElement = self._application.xml().getXmlElementByName("setup", False)
        if setupXmlElement:
            attribute = setupXmlElement.getAttribute("generate-only")
            if attribute: self._data.generateOnly = (attribute == "true")
            attribute = setupXmlElement.getAttribute("view-code")
            if attribute: self._data.viewCode = (attribute == "true")
            attribute = setupXmlElement.getAttribute("run-with-sec")
            if attribute: self._data.runWithSEC = (attribute != "false")
            xmlElement = setupXmlElement.getXmlElementByName("execution", False)
            if xmlElement:
                attribute = xmlElement.getAttribute("command")
                if attribute:
                    if attribute == "compile-translate-link-execute":
                        self._data.execCommand = SetupExecCommand.TRANSLATE
                    elif attribute == "custom":
                        self._data.execCommand = SetupExecCommand.CUSTOM
                attribute = xmlElement.getAttribute("translation")
                if attribute:
                    if attribute == "fortran":
                        self._data.translation = SetupTranslationLang.FORTRAN
            xmlElement = setupXmlElement.getXmlElementByName("extra-options", False)
            if xmlElement:
                attribute = xmlElement.getAttribute("single")
                if attribute: self._data.single = (attribute == "true")
                attribute = xmlElement.getAttribute("x32bit")
                if attribute: self._data.x32bit = (attribute == "true")
                attribute = xmlElement.getAttribute("gcc")
                if attribute: self._data.gcc = (attribute == "true")
            xmlElement = setupXmlElement.getXmlElementByName("addnl-link-objs", False)
            if xmlElement:
                self._data.addnlLinkObjs = xmlElement.getContent()
            xmlElement = setupXmlElement.getXmlElementByName("custom-run-command", False)
            if xmlElement:
                self._data.customRunCommand = xmlElement.getContent()
            xmlElement = setupXmlElement.getXmlElementByName("esl-sec-specification", False)
            if xmlElement:
                self._data.esl_sec_specification = xmlElement.getContent()

        setupView.resetSetupView(self._data)

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ""
        options = ""
        if self._data.generateOnly:
            options += " generate-only=\"true\""
        if self._data.viewCode:
            options += " view-code=\"true\""
        if not self._data.runWithSEC:
            options += " run-with-sec=\"false\""
        execution = ""
        esl_sec_specification = ""
        if self._data.execCommand == SetupExecCommand.CUSTOM:
            execution += ind2 + "<execution command=\"custom\"/>"+nl
            execution += ind2 + "<custom-run-command><![CDATA[" + self._data.customRunCommand + "]]></custom-run-command>" + nl
        elif self._data.execCommand == SetupExecCommand.TRANSLATE:
            execution += ind2 + "<execution command=\"compile-translate-link-execute\""
            if self._data.execCommand == SetupTranslationLang.FORTRAN:
                execution += " translation=\"fortran\""
            execution += "/>"+nl
            extraOptions = ""
            if self._data.single:
                extraOptions += " single=\"true\""
            if self._data.x32bit:
                extraOptions += " x32bit=\"true\""
            if self._data.gcc:
                extraOptions += " gcc=\"true\""
            if extraOptions:
                execution += ind2 + "<extra-options"+extraOptions+"/>"+nl
            if self._data.addnlLinkObjs:
                execution += ind2 + "<addnl-link-objs><![CDATA["+self._data.addnlLinkObjs+"]]></addnl-link-objs>"+nl
        if self._data.esl_sec_specification:
            esl_sec_specification = ind2 + "<esl-sec-specification>\n"
            esl_sec_specification += ind2 + ind + "<![CDATA["+self._data.esl_sec_specification+"]]>\n"
            esl_sec_specification += ind2 + "</esl-sec-specification>"+nl
        if options or execution or esl_sec_specification:
            result = ind + "<setup" + options
            if execution or esl_sec_specification:
                result += ">"+nl
                result += execution
                result += esl_sec_specification
                result += ind + "</setup>"+nl
            else:
                result += "/>"+nl
        return result

    @staticmethod
    def setup(control):
        if shutil.which(SetupInfo._esl_command) != None:
            SetupInfo._esl = SetupInfo._esl_command
        else:
            msg = "Cannot find the \""+SetupInfo._esl_command+"\" command\n"
            control.appendMessage(msg)

    @staticmethod
    def esl():
        return SetupInfo._esl
