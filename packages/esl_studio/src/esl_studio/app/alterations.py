#! /usr/bin/python

import os

import wx

import esl_diagram.xmlutil as xut

from . import utils as Utils

FldSep = "\x1F" # <US> unit separator - These should not appear in any alteration text.
AltSep = "\x1E" # <RS> record separator

class Alteration(object):
    def __init__(self, moduleId, secondary):
        self._alterationStack = None
        self._moduleId = moduleId
        self._secondary = secondary
        self._secondaryStack = []

    def set_alterationStack(self, alterationStack):
        self._alterationStack = alterationStack

    def undo(self):
        if len(self._secondaryStack):
            for i in range(len(self._secondaryStack) - 1, -1, -1): # do backwards
                self._secondaryStack[i].undo()

    def redo(self):
        for i in range(len(self._secondaryStack)):  # do forewards
            self._secondaryStack[i].redo()

    def setMainPage(self, no_change=False):
        page = None
        frame = wx.GetApp().frame()
        moduleId = self._moduleId
        if moduleId:
            if isinstance(self, PropertyAlteration) and self.category == "simulationparameter":
                module = frame.application().getModuleById(moduleId)
                page = frame.viewManager().simulationParametersView()
                page.set_moduleName(module.eslname())
            else:
                page = frame.viewManager().mainView().getCanvasByModuleId(moduleId)
            if page:
                if not no_change:
                    page_index = frame.viewManager().mainView().GetPageIndex(page)
                    if page_index >= 0:
                        frame.viewManager().mainView().SetSelection(page_index) #ChangeSelection is not in wxPython (wouldn't fire event unlike SetSelection)
        return page

    def serialise(self):
        data = ""
        if len(self._secondaryStack):
            for alteration in self._secondaryStack:
                data += AltSep + alteration.serialise()
        return data

class PropertyAlteration(Alteration):

    def __init__(self, moduleId, category, propertyId, propertyTag, oldValue, newValue):
        Alteration.__init__(self, moduleId, False) # all property changes are primary
        self.category = category
        self.propertyId = propertyId
        self.propertyTag = propertyTag
        self.oldValue = oldValue
        self.newValue = newValue

    def undo(self):
        reason = "undo"
        super(PropertyAlteration, self).undo()
        self.setMainPage()
        propertiesControl = self._alterationStack.control().propertiesControl()
        propertiesControl.doPropertyChange(self.category,
            self.propertyId, self.propertyTag,
            self.oldValue, self.newValue, self.oldValue, suppress_action=True, alterationReason=reason)

    def redo(self):
        reason = "redo"
        self.setMainPage()
        propertiesControl = self._alterationStack.control().propertiesControl()
        propertiesControl.doPropertyChange(self.category,
            self.propertyId, self.propertyTag,
            self.newValue, self.oldValue, self.newValue, suppress_action=True, alterationReason=reason)
        super(PropertyAlteration, self).redo()

    def __str__(self):
        return ('PropertyAlteration ' + str(self.category) + '/' + str(self.propertyId) + ' ' +
                str(self.propertyTag) + '(' + str(self.oldValue) + '):' + str(self.newValue))

    def serialise(self):
        data = "PropertyAlteration"+FldSep+str(self._moduleId)+FldSep+str(self.category)+FldSep+str(self.propertyId)+FldSep+str(self.propertyTag)+FldSep+str(self.oldValue)+FldSep+str(self.newValue)
        data += super(PropertyAlteration, self).serialise()
        return data

class CanvasAlteration(Alteration):

    def __init__(self, moduleId, secondary, eventType, eventXmlElement, undoDeleteApplicationData=None, undoUpdateApplicationData=None, redoInsertApplicationData=None):
        Alteration.__init__(self, moduleId, secondary)
        self.eventType = eventType
        self.eventXmlElement = eventXmlElement
        self.undoDeleteApplicationData = undoDeleteApplicationData
        self.undoUpdateApplicationData = undoUpdateApplicationData
        self.redoInsertApplicationData = redoInsertApplicationData

    def __str__(self):
        return 'CanvasAlteration ' + str(self.eventType) + '/' + self.eventXmlElement.xml()

    def serialise(self):
        data = "CanvasAlteration"+FldSep+str(self._moduleId)+FldSep+str(self._secondary)+FldSep+str(self.eventType)+FldSep+self.eventXmlElement.xml() + FldSep
        if self.undoDeleteApplicationData:
            data += self.undoDeleteApplicationData.xml()
        data += FldSep
        if self.undoUpdateApplicationData:
            data += self.undoUpdateApplicationData.xml()
        data += FldSep
        if self.redoInsertApplicationData:
            data += self.redoInsertApplicationData.xml()
        data += super(CanvasAlteration, self).serialise()
        return data

    def undo(self, reject=False):
        reason = "undo"
        if reject:
            reason = "reject"
        super(CanvasAlteration, self).undo()
        page = self.setMainPage(self._secondary)
        raise_event = ''
        if reject:
            reason = 'reject'
            raise_event = ' raise-event="false"'
        if self.eventType == 'changed_objects':
            application_data = '<application-data alteration="'+reason+'" type="' + self.eventType # needs a quote
            if self._secondary:
                application_data += '" secondary="true" raise-event="false' # leave off a quote
            if reason == 'undo' and (self.undoDeleteApplicationData or self.undoUpdateApplicationData):
                application_data += '">'
                if self.undoDeleteApplicationData:
                    application_data += '<undo-deleted>' + self.undoDeleteApplicationData.xml() + '</undo-deleted>'
                if self.undoUpdateApplicationData:
                    application_data += '<undo-updated>' + self.undoUpdateApplicationData.xml() + '</undo-updated>'
                application_data += "</application-data>"
            else:
                application_data += '"/>'

            # delete objects that were inserted
            deleteObjectsXmlElement = self.eventXmlElement.getXmlElementByName("inserted")
            if deleteObjectsXmlElement:
                objects = deleteObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    deleteObjectsXmlElement = reverseObjects(objects)

            # insert objects that were deleted
            insertObjectsXmlElement = self.eventXmlElement.getXmlElementByName("deleted")
            if insertObjectsXmlElement:
                objects = insertObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    insertObjectsXmlElement = reverseObjects(objects)

            # update objects that were update to their state previous to update
            updateObjectsXmlElement = self.eventXmlElement.getXmlElementByName("pre-updated")
            if updateObjectsXmlElement:
                objects = updateObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    updateObjectsXmlElement = reverseObjects(objects)
                    setEntitiesClearAnnotations(updateObjectsXmlElement)

            # select objects that were selected prior to change
            selectObjectsXmlElement = self.eventXmlElement.getXmlElementByName("prior-selected")
            if selectObjectsXmlElement:
                objects = selectObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    selectObjectsXmlElement = reverseObjects(objects)

            actionName = 'AlterationObjects'
            actionContent = ''
            if deleteObjectsXmlElement:
                actionContent += '<delete>'+deleteObjectsXmlElement.xml()+'</delete>'
            if insertObjectsXmlElement:
                actionContent += '<insert>' + insertObjectsXmlElement.xml() + '</insert>'
            if updateObjectsXmlElement:
                actionContent += '<update>' + updateObjectsXmlElement.xml() + '</update>'
            if selectObjectsXmlElement:
                actionContent += '<select>' + selectObjectsXmlElement.xml() + '</select>'
            action = '<action name="'+actionName+'"'+raise_event+'>' + actionContent + application_data+'</action>'
            page.Action(action)

    def redo(self):
        page = self.setMainPage(self._secondary)
        reason = "redo"
        if self.eventType == 'changed_objects':
            application_data = '<application-data alteration="'+reason+'" type="' + self.eventType
            if self._secondary: application_data += '" secondary="true" raise-event="false'
            if self.redoInsertApplicationData:
                application_data += '">'
                application_data += '<redo-inserted>' + self.redoInsertApplicationData.xml() + '</redo-inserted>'
                application_data += "</application-data>"
            else:
                application_data += '"/>'

            # re-delete objects that were deleted
            deleteObjectsXmlElement = self.eventXmlElement.getXmlElementByName("deleted")
            if deleteObjectsXmlElement:
                objects = deleteObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    deleteObjectsXmlElement = objects

            # re-insert objects that were inserted
            insertObjectsXmlElement = self.eventXmlElement.getXmlElementByName("inserted")
            if insertObjectsXmlElement:
                objects = insertObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    insertObjectsXmlElement = objects

            # re-update objects as they were updated
            updateObjectsXmlElement = self.eventXmlElement.getXmlElementByName("updated")
            if updateObjectsXmlElement:
                objects = updateObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    updateObjectsXmlElement = objects
                    setEntitiesClearAnnotations(updateObjectsXmlElement)

            # select objects as they were selected
            selectObjectsXmlElement = self.eventXmlElement.getXmlElementByName("selected")
            if selectObjectsXmlElement:
                objects = selectObjectsXmlElement.getXmlElementByName("objects")
                if objects:
                    selectObjectsXmlElement = objects

            actionName = 'AlterationObjects'
            actionContent = ''
            if deleteObjectsXmlElement:
                actionContent += '<delete>'+deleteObjectsXmlElement.xml()+'</delete>'
            if insertObjectsXmlElement:
                actionContent += '<insert>' + insertObjectsXmlElement.xml() + '</insert>'
            if updateObjectsXmlElement:
                actionContent += '<update>' + updateObjectsXmlElement.xml() + '</update>'
            if selectObjectsXmlElement:
                actionContent += '<select>' + selectObjectsXmlElement.xml() + '</select>'
            action = '<action name="'+actionName+'">' + actionContent + application_data+'</action>'
            page.Action(action)
        super(CanvasAlteration, self).redo()

def reverseObjects(objectsXml):
    resultXml = objectsXml.copy()
    children = resultXml.getChildren()
    if len(children) > 1:
        children.reverse()
        for child in children:
            twin = child.copy()
            resultXml.removeChild(child)
            resultXml.appendChild(twin)
    return resultXml

def setEntitiesClearAnnotations(objectsXml):
    children = objectsXml.getChildren()
    for childXml in children:
        if childXml.name() == "entity":
            childXml.setAttribute("clear-annotations", "true")

class ModuleAlteration(Alteration):

    def __init__(self, moduleId, category, subType, variableId, data):
        Alteration.__init__(self, moduleId, False) # all module changes are primary
        self.category = category
        self.subType = subType
        self.variableId = variableId
        self.data = data

    def undo(self):
        reason = "undo"
        super(ModuleAlteration, self).undo()
        modulesControl = self._alterationStack.control().modulesControl()
        category = self.category
        if category == 'add-model':
            category = 'remove-model'
        elif category == 'remove-model':
            category = 'add-model'
        elif category == 'add-submodel':
            category = 'remove-submodel'
        elif category == 'remove-submodel':
            category = 'add-submodel'
        elif category == 'add-segment':
            category = 'remove-segment'
        elif category == 'remove-segment':
            category = 'add-segment'
        elif category == 'add-package':
            category = 'remove-package'
        elif category == 'remove-package':
            category = 'add-package'
        elif category == 'add-code':
            category = 'remove-code'
        elif category == 'remove-code':
            category = 'add-code'
        elif category == 'add-package-variable':
            category = 'remove-package-variable'
        elif category == 'remove-package-variable':
            category = 'add-package-variable'
        elif category == 'add-parameter':
            category = 'remove-parameter'
        elif category == 'remove-parameter':
            category = 'add-parameter'
        done, newModuleId, newVariableId = modulesControl.doModuleChange(
            category, self._moduleId, self.subType, self.variableId, self.data, alterationReason=reason)
        if done:
            if newModuleId != 0 and newModuleId != self._moduleId:
                self._moduleId = newModuleId
            if newVariableId != 0 and newVariableId != self.variableId:
                self.variableId = newVariableId

    def redo(self):
        reason = "redo"
        modulesControl = self._alterationStack.control().modulesControl()
        done, newModuleId, newVariableId = modulesControl.doModuleChange(
            self.category, self._moduleId, self.subType, self.variableId, self.data, alterationReason=reason)
        if done:
            if newModuleId != 0 and newModuleId != self._moduleId:
                self._moduleId = newModuleId
            if newVariableId != 0 and newVariableId != self.variableId:
                self.variableId = newVariableId
        super(ModuleAlteration, self).redo()

    def __str__(self):
        return ('ModuleAlteration ' + str(self.category) + '/' + str(self._moduleId) + ' '
                + '/' + str(self.subType) + ' '+ '/' + str(self.variableId) + ' '
                + str(self.data))

    def serialise(self):
        data = "ModuleAlteration"+FldSep+str(self._moduleId)+FldSep+str(self.category)+FldSep+str(self.subType)+FldSep+str(self.variableId)+FldSep+str(self.data)
        data += super(ModuleAlteration, self).serialise()
        return data

class AlterationStack(object):
    def __init__(self, control):
        self._control = control
        self._alterations = []
        self._position = 0
        self._recordReplay = None
        self._recordingFile = ""
        self._playBackRecords = []
        self._playBackInterval = 0
        self._timer = None
        self.clear()

    def control(self): return self._control

    def setup(self):
        pass

    def clear(self):
        self._alterations = []
        self._position = 0
        if self._recordReplay == "recording":
            self.recordAlteration("clear", "")

    def add(self, alteration):
        alteration.set_alterationStack(self)
        if not alteration._secondary:
            if len(self._alterations) != self._position:
                self._alterations = self._alterations[0:self._position]
            self._alterations.append(alteration)
            self._position = len(self._alterations)
            self._control.enableDisableUndoRedo()
            msg = 'AlterationStack.add n='+str(len(self._alterations))+' pos='+str(self._position)+' '+str(alteration)+'\n'
            self._control.appendMessage(msg, 1)
        else:
            if len(self._alterations) == 0 or len(self._alterations) != self._position:
                raise Exception('Error adding secondary alteration')
            else:
                primaryAlteration = self._alterations[len(self._alterations) - 1]
                primaryAlteration._secondaryStack.append(alteration)
        if self._recordReplay == "recording":
            self.recordAlteration("add", alteration)

    def state(self):
        if len(self._alterations) == 0: result = 'empty'
        elif self._position == len(self._alterations): result = 'end'
        elif self._position == 0: result = 'beginning'
        else: result = 'between'
        return result

    def undo(self):
        alteration = None
        if self._position > 0:
            self._position -= 1
            alteration = self._alterations[self._position]
            if alteration:
                alteration.undo()
                msg = 'AlterationStack.undo n='+str(len(self._alterations))+' pos='+str(self._position)+' '+str(alteration)+'\n'
                self._control.appendMessage(msg, 1)
                if self._recordReplay == "recording":
                    self.recordAlteration("undo", alteration)
        if alteration is None:
            wx.Bell()

    def redo(self):
        alteration = None
        if self._position < len(self._alterations):
            alteration = self._alterations[self._position]
            self._position += 1
            if alteration:
                alteration.redo()
                msg = 'AlterationStack.redo n='+str(len(self._alterations))+' pos='+str(self._position)+' '+str(alteration)+'\n'
                self._control.appendMessage(msg, 1)
                if self._recordReplay == "recording":
                    self.recordAlteration("redo", alteration)
        if alteration is None:
            wx.Bell()

    def saveAlterationsStack(self, saveFile):
        self._recordingFile = saveFile
        if os.path.exists(self._recordingFile):
            os.remove(self._recordingFile)
        for alteration in self._alterations:
            self.recordAlteration("add", alteration)

    def recordAlterationsToFile(self, recordingFile, append):
        self._recordReplay = "recording"
        self._recordingFile = recordingFile
        if not append and os.path.exists(self._recordingFile):
            os.remove(self._recordingFile)

    def stopRecordingOrReplayingAlterations(self):
        self._recordReplay = None

    def playAlterationsFromFile(self, recordingFile, interval):
        self._playBackRecords = []
        self._playBackInterval = interval
        if not recordingFile and self._recordingFile:
            recordingFile = self._recordingFile
        f = open(recordingFile, "r")
        if f:
            self._playBackRecords = f.readlines()
            f.close()
            self._recordReplay = "replaying"
            self.playBack()

    def playBack(self): #interval m-secs
        if self._recordReplay == "replaying":
            if len(self._playBackRecords) > 0:
                record = self._playBackRecords.pop(0)
                if record[len(record)-1] == "\n":
                    record = record[0:-1]
                mode, alterationStr = record.split(":", 1)
                alterationStr = Utils.unescapeText(alterationStr)
                if self._playBackInterval == 0:
                    self.playAlteration(mode, alterationStr)
                else:
                    if not self._timer:
                        self._timer = PlayBackTimer(self)
                    self._timer.invoke(self._playBackInterval, mode, alterationStr)
                pass
            else:
                self._recordReplay = None
        pass

    def recordAlteration(self, mode, alteration):
        if self._recordingFile:
            if mode == "clear":
                self.stopRecordingOrReplayingAlterations()
            else:
                if not isinstance(alteration, str):
                    alteration = alteration.serialise()
                alteration = Utils.escapeText(alteration)
                f = open(self._recordingFile, "a")
                if f:
                    record = mode+":"+alteration+"\n"
                    f.write(record)
                    f.close()

    def playAlteration(self, mode, alterationStr):
        # Reconstruct alteration from str
        alteration = self.reconstructAlteration(alterationStr)
        if mode == "add" or mode == "redo":
            alteration.redo()
        elif mode == "undo":
            alteration.undo()
        self.playBack()

    def reconstructAlteration(self, alterationStr):
        topAlteration = None
        alts = alterationStr.split(AltSep)
        for alt in alts:
            alteration = None
            elms = alt.split(FldSep)
            if elms[0] == "PropertyAlteration":
                alteration = PropertyAlteration(int(elms[1]), elms[2], elms[3], elms[4], elms[5], elms[6])
            elif elms[0] == "CanvasAlteration":
                secondary = elms[2] == "True"
                undoDeleteApplicationData = None
                if elms[4]:
                    undoDeleteApplicationData = xut.XmlElement(elms[5])
                undoUpdateApplicationData = None
                if elms[5]:
                    undoUpdateApplicationData = xut.XmlElement(elms[6])
                redoInsertApplicationData = None
                if elms[6]:
                    redoInsertApplicationData = xut.XmlElement(elms[7])
                alteration = CanvasAlteration(int(elms[1]), secondary, elms[3], xut.XmlElement(elms[4]), undoDeleteApplicationData, undoUpdateApplicationData, redoInsertApplicationData)
            elif elms[0] == "ModuleAlteration":
                alteration = ModuleAlteration(int(elms[1]), elms[2], elms[3], int(elms[4]), elms[5])
            if alteration:
                alteration.set_alterationStack(self)
            if not topAlteration:
                topAlteration = alteration
            else:
                topAlteration._secondaryStack.append(alteration)
        return topAlteration

class PlayBackTimer(wx.Timer):
    def __init__(self, alterationStack):
        wx.Timer.__init__(self)
        self._alterationStack = alterationStack

    def invoke(self, interval, mode, alterationStr):
        self._mode = mode
        self._alterationStr = alterationStr
        self.StartOnce(interval)

    def Notify(self):
        self._alterationStack.playAlteration(self._mode, self._alterationStr)
