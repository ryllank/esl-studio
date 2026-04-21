#! /usr/bin/python

from .callentity import CallEntity
from .submodel import Submodel
from .codesubprogram import CodeSubprogram

class SubmodelCall(CallEntity):

    def __init__(self, parent, type="", objectId=""):
        CallEntity.__init__(self, parent, type, objectId)

    def load(self, entityDescrXmlElement, suppressAddName=False):
        super(SubmodelCall, self).load(entityDescrXmlElement, suppressAddName)
        val = entityDescrXmlElement.getAttribute("submodel")
        if val is not None:
            self._subprogramName = val

    def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False):
        xmlAttributeText = super(SubmodelCall, self).specialSaveXmlAttributes(indent, level, saveDefaults)
        subprogram = self.subprogram()
        if subprogram or saveDefaults:
            subprogramName = ''
            if subprogram:
                subprogramName = subprogram.eslname()
            xmlAttributeText += ' submodel="' + subprogramName + '"'
        return xmlAttributeText

    #def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False):  : # Has no contents.

    def checkValidToLoad(self): #valid, msg
        valid = True
        msg = ""
        subprogram = self._subprogram
        if subprogram:
            isPreloaded = subprogram.application() is None
            if not subprogram.valid():
                msg = 'Cannot create submodel call as '
                if isPreloaded: msg += 'preloaded '
                msg += 'submodel is not valid\n'
                self.unlinkSubprogramCallWithSubprogram()
                valid = False

            if isPreloaded and len(subprogram.subprogramCalls()) == 1:      #### TODO why is this 1 - not using hasSubprogramCalls()
                if self._parent.application().blockNames().isin(subprogram.eslname()):
                    msg = 'Cannot create submodel call for preloaded submodel as submodel name "'+\
                        subprogram.eslname()+'" is already being used\n'
                    self.unlinkSubprogramCallWithSubprogram()
                    valid = False
        return valid, msg

    def updateEntity(self, updateXmlElement):
        val = updateXmlElement.getAttribute("submodel")
        if val:
            subprogram = self._application.getSubmodelByName(val) # Should be valid (comes after paste or redo)
            currentSubprogram = self.subprogram()
            if subprogram is not None and subprogram != currentSubprogram:
                self.linkSubprogramCallWithSubprogram(subprogram)
                self._ports = subprogram.getPorts()
                for port in list(self._ports.values()): port.set_parent(self)
                self._attributes = self._subprogram.getAttributes()
                for attribute in list(self._attributes.values()): attribute.set_parent(self)
        val = updateXmlElement.getAttribute("show-subprogram")
        if val is not None:
            self._show_subprogram = val
        super(SubmodelCall, self).updateEntity(updateXmlElement)

    def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue):
        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
            super(SubmodelCall, self).validateEntityPropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)
        if valid:
            if propertyTag == 'submodel':
                val_item = "Submodel"
                if newValue != '':
                    subName = newValue
                    if newValue[-1] == "*":
                        subName = subName[:-1]
                    subprogram = self._application.blockNames().get(subName)
                    if subprogram is None:
                        valid = False
                        rejection = 'no subprogram of that name in the application'
                    elif subprogram.subprogramBaseType() == "code" and subprogram.subprogramType() != "submodel":
                        valid = False
                        rejection = 'application subprogram of that name is not a submodel'
                    elif subprogram.subprogramBaseType() == "diagram" and subprogram.moduleType() != "submodel":
                        valid = False
                        rejection = 'application subprogram with that name is not a submodel'
                    elif not subprogram.valid():
                        valid = False
                        rejection = 'submodel is invalid'
                    elif newValue[-1] == "*":
                        valid = False
                        rejection = 'submodel is marked invalid'
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateEntityProperty(self, propertyTag, newValue, suppress_action=False):
        refreshProperty = super(SubmodelCall, self).updateEntityProperty(propertyTag, newValue, suppress_action=suppress_action)
        if propertyTag == 'submodel':
            self.doSubprogramCallSubprogramPropertyChange(newValue, suppress_action=suppress_action)
            refreshProperty = True
        elif propertyTag == 'annotations':
            if 'Submodel' in newValue:
                self.set_show_subprogram("true")
            else:
                self.set_show_subprogram("false")
        return refreshProperty

    # def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, tempNewAttribute, val_type, val_item, val_oldValue, val_newValue): # No attribute property validation

    # def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False): # No attribute property update
