#! /usr/bin/python

import os.path
from collections import OrderedDict

import wx

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..config import Config
from .modelbase import ModelBase
from .applicationtypes import CALLABLECODESUBPROGRAMTYPES
from .codesubprogram import CodeSubprogram
from ..esl import parseesl, esl

class Code(ModelBase):

    def __init__(self, application, moduleId):
        ModelBase.__init__(self, application, moduleId, 'code')
        self._application = application
        self._parseEsl = parseesl.ParseEsl()
        self._codeType = ""  # "ESL" or "file"
        self._eslText = ""
        self._filepath = ""
        self._subprogramParseObjects = None
        self._codeSubprograms = OrderedDict()
        self._libraryList = []
        self._calledSubprogramNames = []

    def codeType(self):
        return self._codeType
    def set_codeType(self, codeType):
        self._codeType = codeType
    def eslText(self):
        return self._eslText
    def set_eslText(self, eslText):
        if self._codeType == 'ESL':
            self._eslText = eslText
    def file(self):
        return self._filepath
    def set_file(self, filepath):
        if self._codeType == 'file':
            self._filepath = filepath
            self._eslText = ''
    def valid(self):
        valid = len(self._parseEsl.messages()) == 0
        return valid
    def subprogramParseObjects(self):
        return self._subprogramParseObjects
    def codeSubprograms(self):
        return self._codeSubprograms
    def libraryList(self):
        return self._libraryList
    def importedPackageNames(self):
        return self._parseEsl.importedPackageNames()
    def calledSubprogramNames(self):            #### TODO in future - calls from Code (not builtins, not subprograms declared in the Code - so missed libs or application subprograms)
        return self._calledSubprogramNames
    def hasSubprogramCalls(self):
        hasCalls = False
        for sub in list(self._codeSubprograms.values()):
            if sub.hasSubprogramCalls():
                hasCalls = True
                break
        return hasCalls
    def hasPackageVariableInUse(self):
        inUse = False
        for sub in list(self._codeSubprograms.values()):
            if sub.hasVariableInUse():
                inUse = True
                break
        return inUse
    def parseMessages(self):
        return self._parseEsl.messagesString()

    def identification(self, showSubType=False):
        identification = "Code"
        if showSubType:
            if self._codeType == 'file':
                identification += " (File"
                if self._filepath:
                    identification += " "+os.path.splitext(os.path.basename(self._filepath))[0]
                identification += ")"
            elif self._codeType == 'ESL':
                identification += " (ESL"
                if self._subprogramParseObjects and len(self._subprogramParseObjects) > 0:
                    identification += " "+self._subprogramParseObjects[-1].name
                identification += ")"
        return identification

    def load(self, codeXmlElement, preload=False):
        loadedCode = False
        if not preload:
            val = codeXmlElement.getAttribute("type")
            if val: self._codeType = val
        val = codeXmlElement.getAttribute("description")
        if val: self._description = val
        addDetached = not Config.getBool('Application/Open Code Pages')
        propertyValue = ""
        if self._codeType == "ESL":
            eslXmlElement = codeXmlElement.getXmlElementByName("ESL")
            if eslXmlElement:
                propertyValue = eslXmlElement.getContent()
        elif self._codeType == "file":
            fileXmlElement = codeXmlElement.getXmlElementByName("file")
            if fileXmlElement:
                propertyValue = fileXmlElement.getAttribute("path")

        if self._codeType == "ESL" or self._codeType == "file": # same as propertyTypes
            updated = self.updateCodeSubprograms(self._codeType, propertyValue, noSubprogramCallUpdates=True, noLibraryReport=True) # this does the add to application, or if failed shows messaged
            if updated:
                #### TODO - maybe should check if there is a name clash with a preloaded subprogram
                if not preload:     #### TODO handle preloads somewhere somehow
                    tabname = self._application.moduleViewTabname(self)
                    page = self._application.frame().viewManager().mainView().addCodePage(tabname, addDetached)
                    page.set_moduleId(self._moduleId)
                    if self._codeType == "ESL":
                        page.setText(self._eslText)
                        page.setReadOnly(False)
                        page.setAllowCommitESL(True)
                    elif self._codeType == "file" and self._filepath:
                        page.LoadFile(self._filepath)

                if not self.valid():
                    msg = "Import "+self.identification(showSubType=True) + " has code check message(s):\n"
                    msg += self.parseMessages() + "\n"
                    application = self._application
                    if not application:  # Note: preloaded code/submodels have no application
                        application = wx.GetApp().frame().application()
                    control = None
                    if application:
                        control = application.frame().control()
                    control.appendMessage(msg)

                loadedCode = True
        return loadedCode

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ind + '<code'
        result += ' type="' + self._codeType + '"'
        if self._description or saveDefaults:
            result += ' description="' + xut.entitise(self._description) + '"'
        result += '>' + nl
        if self._codeType == "ESL":
            result += ind2 + '<ESL>' + nl + ind2 + ind + '<![CDATA[' + str(self._eslText) + ']]>' + nl + ind2 + '</ESL>' + nl
        elif self._codeType == "file":
            result += ind2 + '<file path="' + str(self._filepath) + '"/>' + nl
        result += ind + '</code>' + nl
        return result

    def updateCodeSubprograms(self, propertyTag, propertyValue, noSubprogramCallUpdates=False, noLibraryReport=False, suppress_action=False, alterationReason=None):
        updated = True
        application = self._application
        if not application:       # Note: preloaded code/submodels have no application
            application = wx.GetApp().frame().application()
        control = None
        if application:
            control = application.frame().control()

        validateCodeResults  = self.validateCodeSubprograms(propertyTag, propertyValue, askForReplacing=False, alterationReason=alterationReason)
        rejection = validateCodeResults[0]
        updatedPropertyValue = validateCodeResults[1]
        updatedOldPropertyValue = validateCodeResults[2]
        eslText = validateCodeResults[3]
        fileValue = validateCodeResults[4]
        if not eslText:
            self._subprogramParseObjects = None
        newSubprogramParseObjects = validateCodeResults[5]
        newCodeSubprograms = validateCodeResults[6]
        replacingNames = validateCodeResults[7]
        commonNames = validateCodeResults[8]
        additionalNames = validateCodeResults[9]
        obsoleteNames = validateCodeResults[10]
        argumentsChangedNames = validateCodeResults[11]
        if propertyTag == "file":
            self.set_file(fileValue)
        self._eslText = eslText

        if not rejection:
            self._subprogramParseObjects = newSubprogramParseObjects
            oldCodeSubprograms = self._codeSubprograms
            self._codeSubprograms = newCodeSubprograms

            for name in commonNames:
                application.blockNames().delete(name)
                application.blockNames().add(name, self._codeSubprograms[name])

            for name, oldName in replacingNames.items():
                application.blockNames().delete(oldName)
                application.blockNames().add(name, self._codeSubprograms[name])

            for name in additionalNames:
                application.blockNames().add(name, self._codeSubprograms[name])
                #### TODO else preloaded code ?

            for name in obsoleteNames:
                application.blockNames().delete(name)

            previousLibraryList = self._libraryList
            self._libraryList = self._parseEsl.libraryList().copy()

            if not noLibraryReport and control: #### TODO see if have to handle preloaded code
                for lib in self._libraryList:
                    if lib not in previousLibraryList:
                        libName = Utils.libraryBaseName(lib)
                        libItem = application.blockNames().get(libName)
                        if libItem:
                            libItemType = ""
                            if isinstance(libItem, CodeSubprogram):
                                libItemType = libItem.subprogramType()
                            else:
                                libItemType = libItem.moduleType()
                            msg = ""
                            if libItemType == "submodel":
                                msg = "Submodel "
                            elif libItemType == "segment" or libItemType == "external-segment":
                                msg = "Segment "
                            else:
                                msg = "Name "
                            if msg:
                                msg += libName + " in \"--LIBRARY\" statement is in the application"
                                control.appendMessage(msg)

                newToOldSubprogramNames = {}
                for subprogramName in commonNames:
                    for sub in list(oldCodeSubprograms.values()):
                        if subprogramName.upper() == sub.eslname().upper():
                            newToOldSubprogramNames[subprogramName] = sub.eslname() # retain old case
                            break
                for subprogramName in replacingNames.keys():
                    newToOldSubprogramNames[subprogramName] = replacingNames.get(subprogramName)
                for subprogramName, oldSubprogramName in newToOldSubprogramNames.items():
                    subprogram = self.getSubprogramByName(subprogramName)
                    if subprogram.subprogramType() in CALLABLECODESUBPROGRAMTYPES:
                        oldSubprogram = None
                        for sub in list(oldCodeSubprograms.values()):
                            if oldSubprogramName.upper() == sub.eslname().upper():
                                oldSubprogram = sub
                                break
                        if oldSubprogram:
                            calls = oldSubprogram.subprogramCalls().copy()
                            for call in calls:
                                call.doSubprogramCallSubprogramPropertyChange(subprogramName, suppress_action=suppress_action)

                for oldSubprogram in oldCodeSubprograms.values():
                    calls = oldSubprogram.subprogramCalls().copy()
                    for call in calls:
                        call.unlinkSubprogramCallWithSubprogram()

                application.frame().viewManager().applicationView().addCodeSubprograms(None, self.moduleId(), self)

        else:
            updated = False
            if control:
                msg = "Cannot import "+self.identification(showSubType=True)+":\n"
                msg += rejection
                if not self.valid():
                    msg += "with code check message(s):\n"
                    msg += self.parseMessages() + "\n"
                control.appendMessage(msg)

        return updated

    def getSubmodelByName(self, eslname):
        submodel = None
        for sub in list(self._codeSubprograms.values()):
            if sub.subprogramType() == "submodel":
                if sub.eslname().upper() == eslname.upper():
                    submodel = sub
                    break
        return submodel

    def getFunctionByName(self, eslname):
        function = None
        for sub in list(self._codeSubprograms.values()):
            if sub.returnType():
                if sub.eslname().upper() == eslname.upper():
                    function = sub
                    break
        return function

    def getSubprogramByName(self, eslname):
        subprogram = None
        for sub in list(self._codeSubprograms.values()):
            if sub.eslname().upper() == eslname.upper():
                subprogram = sub
                break
        return subprogram

    def getSegmentByName(self, eslname):
        segment = None
        for sub in list(self._codeSubprograms.values()):
            if sub.subprogramType() == "segment":
                if sub.eslname().upper() == eslname.upper():
                    segment = sub
                    break
        return segment

    def findSubprogram(self, subprogramName):
        page = self._application.frame().viewManager().mainView().getCodeViewByModuleId(self._moduleId)
        subprogram = self.getSubprogramByName(subprogramName)
        if subprogram:
            pos = subprogram.position()
            if pos >= 0:
                line = page.LineFromPosition(pos)
                page.GotoLine(line)

    def validateCodeSubprograms(self, propertyTag, propertyValue, askForReplacing=False, alterationReason=None):
        # validateCodeResults tuple:
        rejection = ""                      # 0 rejection txt (poss multiline) if Code cannot be imported (or loaded) into application
        updatedPropertyValue = None         # 1
        updatedOldPropertyValue = None      # 2 for use by undo
        eslText = ""                        # 3
        fileValue = ""                      # 4
        newSubprogramParseObjects = []      # 5
        newCodeSubprograms = OrderedDict()  # 6
        replacingNames = OrderedDict()      # 7
        commonNames = []                    # 8
        additionalNames = []                # 9
        obsoleteNames = []                  # 10
        argumentsChangedNames = []          # 11

        valueXml = xut.xmlElement(propertyValue)
        updateInfo = None
        if valueXml:
            value = valueXml.getContent()
            updateInfo = valueXml.getAttribute("update-info")
        else:
            value = propertyValue

        oldValue = ""
        if propertyTag == "ESL":
            oldValue = self._eslText
            eslText = value
        elif propertyTag == "file":
            oldValue = self._filepath
            fileValue = value
            if fileValue:
                filepath = Utils.eslFile(fileValue)
                f = None
                try:
                    f = open(filepath, 'r')
                except Exception:
                    pass
                if f:
                    eslText = f.read()
                    f.close()
                if not f:
                    rejection += "File error: Cannot find (or read) ESL file \"" + fileValue + "\"\n"

        application = self._application
        if not application:
            application = wx.GetApp().frame().application()

        errTxt = ""
        if not rejection:
            self._parseEsl.parseEsl(eslText, fileValue)
            newSubprogramParseObjects = self._parseEsl.subprogramParseObjects()

            errTxt = ""
            for subprogramParseObject in newSubprogramParseObjects:
                codeSubprogram = CodeSubprogram(self, subprogramParseObject)
                name = codeSubprogram.eslname()
                if newCodeSubprograms.get(name):
                    rejection += "duplicate name \""+name+"\"\n"
                else:
                    newCodeSubprograms[codeSubprogram.eslname()] = codeSubprogram
                    errTxt = codeSubprogram.errors()  #### any extra errors *after* parsing - due to incorporation
                    if errTxt:
                        rejection += errTxt + "\n"
            oldNames = self._codeSubprograms.keys()
            oldNamesUpper = list(map(lambda item: item.upper(), oldNames))
            newNames = newCodeSubprograms.keys()
            newNamesUpper = list(map(lambda item: item.upper(), newNames))
            for name in newNames:
                if name.upper() in oldNamesUpper:
                    commonNames.append(name)
                else:
                    additionalNames.append(name)
            for name in oldNames:
                if name.upper() not in newNamesUpper:
                    obsoleteNames.append(name)

        # Reject if any obsoleteNames are for packages that are used AND have variables in use.
        if not rejection:
            for name in obsoleteNames:
                currentSubprogram = self._codeSubprograms.get(name)
                if currentSubprogram.subprogramType() == "package":
                    if currentSubprogram.hasVariableInUse():
                        rejection += "cannot remove package \""+name+"\" as has variable(s) in use\n"

        if not rejection:
            if askForReplacing:
                # Look and ask about replacing old (called) subprograms with new ones - by index - all or none.
                rejection, replacingNames = self.askForReplacingCalledSubprogram(newSubprogramParseObjects, obsoleteNames, additionalNames)
            elif updateInfo is not None:
                namePairs = updateInfo.split("|") # newName:oldName
                for namePair in namePairs:
                    names = namePair.split(":")
                    replacingNames[names[0]] = names[1] # newName:oldName

        # even if rejection continue looking for additional rejections
        for newName, oldName in replacingNames.items():
            additionalNames.remove(newName)
            obsoleteNames.remove(oldName)

        # - by eslname find any subprograms in current set that are *not* in this new lot (to be removed) - obsoleteNames
        # if callable and have calls - this is an error
        for name in obsoleteNames:
            currentSubprogram = self._codeSubprograms.get(name)
            if currentSubprogram.hasSubprogramCalls():
                rejection += "cannot remove subprogram \""+name+"\" as has calls\n"
        # else will be removed after this - do we need to do something (at least remove from application)
        # - by eslname find any subprograms in new set that are *not* in current lot (to be added) - additionalNames
        # if name isin use in the application - this is an error
        for name in additionalNames:
            errTxt = esl.ValidateName(name, silent=True)
            if errTxt:
                rejection += "cannot add invalid named subprogram " + errTxt + "\n"
            elif application.blockNames().isin(name):
                rejection += "cannot add subprogram \"" + name + "\" as name is already in the application\n"
            elif application.checkIsinFullLibraryList(name):
                rejection = "cannot add subprogram \"" + name + "\" as name is in use as a library submodel\n"
        # else will be added after this - do we need to do something (at least add in to application)
        # - by eslname find matching new and current subprograms (to be updated) - commonNames
        # if changed subprogramType ????? - is this an error - if callable and has calls yes
        # else should be OK
        # for callable and has calls - see if changed arguments
        # if has changed will need to update calls (of appropriate type)
        oldNames = commonNames + list(replacingNames.values())
        newNames = commonNames + list(replacingNames.keys())
        for i in range(len(oldNames)):
            oldName = oldNames[i]
            newName = newNames[i]
            currentSubprogram = self.getSubprogramByName(oldName)
            if currentSubprogram.hasSubprogramCalls():
                newSubprogram = newCodeSubprograms.get(newName)
                currentSubtype = currentSubprogram.subprogramType()
                newSubtype = newSubprogram.subprogramType()
                if currentSubtype != newSubtype and (currentSubtype == 'submodel' or newSubtype == 'submodel'): # change between submodel and some type of segment
                    rejection += "called subprogram \"" + newName + "\" invalid change of type\n"
                else:
                    if newSubprogram.argumentParseObjects() != currentSubprogram.argumentParseObjects():
                        argumentsChangedNames.append(newName)

        if not rejection:
            if not updateInfo:
                if len(replacingNames) > 0:
                    updateInfo = ""
                    undoUpdateInfo = ""
                    for newName, oldName in replacingNames.items():
                        if updateInfo: updateInfo += "|"
                        if undoUpdateInfo: undoUpdateInfo += "|"
                        updateInfo += newName + ":" + oldName
                        undoUpdateInfo += oldName + ":" + newName
                    updatedPropertyValue = "<update-code property=\""+propertyTag+"\" update-info=\""+updateInfo+"\"><![CDATA["+propertyValue+"]]></update-code>"
                    updatedOldPropertyValue = "<update-code property=\""+propertyTag+"\" update-info=\""+undoUpdateInfo+"\"><![CDATA["+oldValue+"]]></update-code>"

        return rejection, updatedPropertyValue, updatedOldPropertyValue, eslText, fileValue, newSubprogramParseObjects, newCodeSubprograms, replacingNames, commonNames, additionalNames, obsoleteNames, argumentsChangedNames

    def askForReplacingCalledSubprogram(self, newSubprogramParseObjects, obsoleteNames, additionalNames):
        rejection = ""
        replacingNames = OrderedDict()

        replacementOldNames = []
        possibleReplacementOldNames = []
        possibleReplacingNames = OrderedDict()
        for name in obsoleteNames:
            currentSubprogram = self._codeSubprograms.get(name)
            if currentSubprogram.subprogramType() in CALLABLECODESUBPROGRAMTYPES and currentSubprogram.hasSubprogramCalls():
                replacementOldNames.append(name)
                possibleReplacementOldNames.append(name)
        for name in possibleReplacementOldNames:
            ix = -1
            for i in range(len(self._subprogramParseObjects)):
                if self._subprogramParseObjects[i].name == name:
                    ix = i
                    break
            if ix >= 0:
                if ix < len(newSubprogramParseObjects):
                    oldName = self._subprogramParseObjects[ix].name
                    newName = newSubprogramParseObjects[ix].name
                    if newName in additionalNames:
                        newSubType = newSubprogramParseObjects[ix].subprogramType()
                        oldSubType = self._subprogramParseObjects[ix].subprogramType()
                        if newSubType == oldSubType or (newSubType == 'submodel' or oldSubType == 'submodel'): # compatible subtypes
                            #### TODO collect all possible replacements so they could be selected - Later (in appropriate dlg box that lets you choose)
                            possibleReplacingNames[newName] = oldName
                            replacementOldNames.remove(oldName)
        # See if any old (called) subprograms have no possibleReplacingNames - in which case an appropriate rejection can be given - we have no acceptable choice
        for name in replacementOldNames:
            rejection += "there are no valid possible replacements for \""+ name +"\"\n"
        if len(possibleReplacingNames) > 0:
            msg = ""
            if len(possibleReplacingNames) == 1:
                msg += "Do you want to rename the subprogram - which has call(s) - as follows:"
            else:
                msg += "Do you want to rename the all the subprograms - which have call(s) - as follows:"
            for newName, oldName in possibleReplacingNames.items():
                nCalls = len(self._codeSubprograms[oldName].subprogramCalls())
                msg += "\n" + oldName + " to " + newName + " - has " + str(nCalls) + " call(s)"
            #### TODO Later - have a dlg box that lets you choose where there are multiple possible replacements for a called obsolete one.
            dlg = wx.MessageDialog(wx.GetApp().frame(),
                                   msg,
                                   "Replace called subprograms",
                                   wx.YES_NO | wx.ICON_INFORMATION)
            page = self._application.frame().viewManager().mainView().getCodeViewByModuleId(self._moduleId)
            ans = page.showModalDlg(dlg)
            if ans == wx.ID_YES:
                replacingNames = possibleReplacingNames
        return rejection, replacingNames
