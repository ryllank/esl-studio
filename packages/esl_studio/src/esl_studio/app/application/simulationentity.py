#! /usr/bin/python

from collections import OrderedDict
import copy

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..esl import esl
from .attribute import Attribute
from .port import Port, PortConnectorSeparator

class SimulationEntity(object):

    _exemplars = {}     # A dict (on type) of defined Simulation Entities that have been created ?{for the application|in the ESL-Studio session}? - default

    def __init__(self, parent, type = "", objectId = ""):
        self._parent = parent # a DiagramInfo
        self._application = None
        if parent:
            self._application = parent.parent().application() # for convenience
        self._type = type
        self._specialType = None
        self._objectId = objectId
        self._entityDefnXmlElement = None
        self._prefix = ""
        self._summary = ""
        self._help = ""
        self._view = ""
        self._description = ""
        self._show_description = "false"
        self._attributes = OrderedDict()
        self._ports = OrderedDict()
        self._entityModelType = "ESL" # default is ESL template - currently also have identified "special", "display", "info" and #### TODO reconsider when sort out preloads: ESL-submodel & file-submodel
        self._includeList = []
        if type:
            exemplar = SimulationEntity._exemplars.get(type)
            if exemplar is not None:
                self.copyFrom(exemplar, parent)
                self._objectId = objectId
            else:
                entities = self._parent._parent._application._frame.control().entities()
                self._entityDefnXmlElement = entities.getEntityDefnXmlElement(self._type)
                if self._entityDefnXmlElement:
                    prefix = self._entityDefnXmlElement.getAttribute('prefix')
                    if prefix: self._prefix = prefix
                    summaryXmlElement = self._entityDefnXmlElement.getXmlElementByName('summary')
                    if summaryXmlElement: self._summary = summaryXmlElement.getContent()
                    helpXmlElement = self._entityDefnXmlElement.getXmlElementByName('help')
                    if helpXmlElement:
                        help = helpXmlElement.getAttribute("src")
                        if help: self._help = help
                    viewXmlElement = self._entityDefnXmlElement.getXmlElementByName('view')
                    if viewXmlElement:
                        view = viewXmlElement.getAttribute("src")
                        if view: self._view = view
                    entityModelXmlElement = self._entityDefnXmlElement.getXmlElementByName("model")
                    if entityModelXmlElement:
                        val = entityModelXmlElement.getAttribute("type")
                        if val is not None: self._entityModelType = val
                        if self._entityModelType == "ESL":
                            generateXmlElement = entityModelXmlElement.getXmlElementByName("generate", False)
                            if generateXmlElement:
                                includeXmlElement = generateXmlElement.getXmlElementByName("include", False)
                                if includeXmlElement:
                                    includeStr = includeXmlElement.getContent()
                                    self._includeList = includeStr.split()

                    self.initPortsNAttributes(entities)

                    # Note: Cannot set exemplar here as entity may not have been fully set here (in constructor) yet - so use setExemplar after in Application.makeSimulationEntity
                else:
                    msg = 'No entity definition for type "'+self._type+'" found\n'
                    self._application.frame().control().appendMessage(msg, 0)
                    self._type = ''

    def __str__(self):
        return "<"+self.identification()+">"

    def setExemplar(self):
        type = self._type
        if type:
            exemplar = SimulationEntity._exemplars.get(type)
            if exemplar is None:
                exemplar = self.detachedCopy(self._parent)
                exemplar._objectId = ''
                for attribute in exemplar._attributes.values():
                    attribute.set_argument(None)
                for port in exemplar._ports.values():
                    port._assignedAttributes = []
                    port.set_argument(None)
                SimulationEntity._exemplars[type] = exemplar

    def parent(self): return self._parent
    def type(self): return self._type
    def specialType(self): return self._specialType
    def setSpecialType(self, specialType): self._specialType = specialType
    def summary(self): return self._summary
    def help(self): return self._help
    def view(self): return self._view
    def objectId(self): return self._objectId
    def entityDefnXmlElement(self): return self._entityDefnXmlElement
    def description(self): return self._description
    def prefix(self): return self._prefix
    def set_description(self, value): self._description = value
    def show_description(self): return self._show_description
    def set_show_description(self, value): self._show_description = value
    def attributes(self):
        result = self._attributes
        return result
    def entityModelType(self): return self._entityModelType
    def includeList(self): return self._includeList

    def identification(self):
        result = self.type() + PortConnectorSeparator + str(self._objectId)
        return result

    def isSubmodelCall(self):
        result = self._specialType == "Submodel Call"
        return result

    def isSegmentCall(self):
        result = self._specialType == "Segment Call"
        return result

    def isFunctionCall(self):
        result = self._specialType == "Function Call"
        return result

    def isCall(self):
        result = self._specialType == "Submodel Call" or self._specialType == "Segment Call" or self._specialType == "Function Call"
        return result

    def isInputArgument(self):
        result = self._specialType == "Input Argument"
        return result

    def isOutputArgument(self):
        result = self._specialType == "Output Argument"
        return result

    def isCodeInsert(self):
        result = self._specialType == "Code Insert"
        return result

    def isConstantInput(self):
        result = self._specialType == "Constant Input"
        return result

    def isArgument(self):
        result = self._specialType == "Input Argument" or self._specialType == "Output Argument"
        return result

    def detachedCopy(self, parent):
        """ Copies from self to make a new SimulationEntity (or super class of it) with a new parent (may be None) """
        newEnt = self.__class__(parent)
        newEnt.copyFrom(self, parent)
        return newEnt

    def copyFrom(self, otherSimulationEntity, parent):
        """ Copies from otherSimulationEntity into the self except for parent which it updates (may set it None).
            It makes clones of the otherSimulationEntity's attributes and ports for its-self. """
        self._parent = parent # a DiagramInfo
        self._application = None
        if parent: self._application = parent.parent().application() # for convenience
        self._type = otherSimulationEntity._type
        self._specialType = otherSimulationEntity._specialType
        self._objectId = otherSimulationEntity._objectId
        self._entityDefnXmlElement = otherSimulationEntity._entityDefnXmlElement
        self._prefix = otherSimulationEntity._prefix
        self._summary = otherSimulationEntity._summary
        self._help = otherSimulationEntity._help
        self._view = otherSimulationEntity._view
        self._description = otherSimulationEntity._description
        self._show_description = otherSimulationEntity._show_description
        clonedAttributes = OrderedDict()
        for key, value in otherSimulationEntity._attributes.items():
            value = value.detachedCopy(self)
            clonedAttributes[key] = value
        self._attributes = clonedAttributes
        clonedPorts = OrderedDict()
        for key, value in otherSimulationEntity._ports.items():
            value = value.detachedCopy(self)
            clonedPorts[key] = value
        self._ports = clonedPorts
        self._entityModelType = otherSimulationEntity._entityModelType
        self._includeList = otherSimulationEntity._includeList

    def initPortsNAttributes(self, entities):
        attdict = entities.getAttributesDict(self._type)  # dict for tag of Attribute
        for atttag in attdict:
            attribute = copy.copy(attdict[atttag])
            self._attributes[atttag] = attribute
            attribute.set_parent(self)
        portdict = entities.getPortsDict(self._type)
        for portid in portdict:
            port = copy.copy(portdict[portid])
            self._ports[portid] = port
            port.set_parent(self)

    def ports(self):
        result = self._ports    # Note: Even for Submodel Calls maintain the simulationentity ports (update preserving assignables when interface changes
        return result

    def resetPorts(self):
        self._ports = OrderedDict()

    def loadAttributes(self, entityDescrXmlElement, suppressAddName=False):  # Override this in any special types of simulation entity which do special handling when loading attributes.
        # Load attributes (including for Calls).
        if self._type:
            entities = self._parent._parent._application._frame.control().entities()
            attdict = entities.getAttributesDict(self._type)  # dict for tag of Attribute
            for atttag in attdict:
                attribute = copy.copy(attdict[atttag])
                attribute.set_parent(self)
                self._attributes[atttag] = attribute
        attXmlList = entityDescrXmlElement.getXmlElementListByName("attribute", False)
        for attXmlElement in attXmlList:
            tempatt = Attribute(self)
            tempatt.clearAssignables()
            tempatt.load(attXmlElement, suppressAddName=suppressAddName, suppressSetDefaultsForDatatype=True)
            atttag = tempatt.tag()
            if atttag and atttag in self._attributes:
                att = self._attributes[atttag]
                att.copyAssignables(tempatt)
            elif self.isCall():
                if atttag: self._attributes[atttag] = tempatt

    def load(self, entityDescrXmlElement, suppressAddName=False):
        self._type = entityDescrXmlElement.getAttribute("type")
        self._objectId = entityDescrXmlElement.getAttribute("id")
        val = entityDescrXmlElement.getAttribute("description")
        if val is not None: self._description = val
        val = entityDescrXmlElement.getAttribute("show-description")
        if val is not None: self._show_description = val
        if self._type:
            self.loadAttributes(entityDescrXmlElement, suppressAddName)
            entities = self._parent._parent._application._frame.control().entities()
            # Load ports
            portdict = entities.getPortsDict(self._type)
            for portid in portdict:
                port = copy.copy(portdict[portid])
                port.set_parent(self)
                self._ports[portid] = port
        # Load ports (including for Calls and Code Inserts).
        portXmlList = entityDescrXmlElement.getXmlElementListByName("port", False)
        for portXmlElement in portXmlList:
            tempport = Port(self)
            tempport.load(portXmlElement, suppressAddName=suppressAddName)
            portid = tempport.id()
            if self.isCall() or self.isCodeInsert():
                self._ports[portid] = tempport
            else:
                if portid and portid in self._ports:
                    port = self._ports[portid]
                    port.copyAssignables(tempport)

    def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False): # Override this in any special types of simulation entity which have to add additional XML attributes text.
        xmlAttributeText = ""
        return xmlAttributeText

    def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False): # Override this in any special types of simulation entity which have to add additional XML contents text.
        xmlContentsText = ""
        return xmlContentsText

    def saveAttributes(self, indent=None, level=0, saveDefaults=False, exemplar=None): # Override this in any special types of simulation entity which do special handling when saving attributes.
        attributes = ""
        for atttag in self._attributes:
            att = self._attributes[atttag]
            exemplarAttribute = None
            if exemplar and len(exemplar._attributes) > 0:
                exemplarAttribute = exemplar._attributes.get(atttag)
            attributes += att.save(indent, level + 1, saveDefaults, exemplarAttribute=exemplarAttribute)
        return attributes

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        exemplar = None
        if not saveDefaults:
            exemplar = SimulationEntity._exemplars.get(self._type)
        attributes = self.saveAttributes(indent=indent, level=level, saveDefaults=saveDefaults, exemplar=exemplar)
        ports = ''
        hasDynamicPorts = False
        if self.isCall() or self.isCodeInsert():
            hasDynamicPorts = True
        for portid in self._ports:
            port = self._ports[portid]
            exemplarPort = None
            if exemplar and len(exemplar._ports) > 0:
                exemplarPort = exemplar._ports.get(portid)
            ports += port.save(indent, level + 1, saveDefaults, savePortWithId=hasDynamicPorts, exemplarPort=exemplarPort)
        result = ind + '<entity id="' + str(self._objectId) + '" type="' + self._type + '"'
        if saveDefaults or (exemplar and self._description != exemplar._description):
            result += ' description="' + xut.entitise(self._description) + '"'
        if saveDefaults or (exemplar and self._show_description != exemplar._show_description):
            if self._show_description == "true":
                result += ' show-description="true"'
            else:
                result += ' show-description="false"'
        specialXmlAttributes = self.specialSaveXmlAttributes(indent, level, saveDefaults)
        result += specialXmlAttributes
        specialXmlContents = self.specialSaveXmlContents(indent, level, saveDefaults)
        if specialXmlContents or attributes or ports or saveDefaults:
            result += '>' + nl
            result += specialXmlContents
            result += attributes
            result += ports
            result += ind + '</entity>' + nl
        else:
            result += '/>' + nl
        return result

    def updateEntityFromDiagramChange(self, diagramChangeUpdateXmlElement):
        # updateXmlElement passed from diagram's change_objects event
        # Look for a port sign change
        portUpdatedXmlList = diagramChangeUpdateXmlElement.getXmlElementListByName("port", False)
        for portUpdatedXmlElement in portUpdatedXmlList:
            portId = portUpdatedXmlElement.getAttribute("id")
            port = self._ports.get(portId)
            if port:
                sign = portUpdatedXmlElement.getAttribute("sign")
                if sign:
                    port.set_sign(sign)

    def updateEntity(self, updateXmlElement):  # Override this (and incorporate it) in any special types of simulation entity that have entity properties.
        # updateXmlElement passed from diagram's change_objects event (via application-data)
        # Handle properties common to all simulation entities.
        val = updateXmlElement.getAttribute("description")
        if val:
            self.set_description(val)
        val = updateXmlElement.getAttribute("show-description")
        if val:
            self.set_show_description(val)
        # Handle any port changes in assignables: eslname sign description show-id show-tag show-eslname show-description [not id designation]
        portUpdatedXmlList = updateXmlElement.getXmlElementListByName("port", True)
        for portUpdatedXmlElement in portUpdatedXmlList:
            tempport = Port(self)
            tempport.load(portUpdatedXmlElement, suppressAddName=True)
            portid = tempport.id()
            if portid and portid in self._ports:
                port = self._ports[portid]
                port.copyAssignables(tempport)

        # Handle any attribute changes in assignables: source value eslname show-tag show-eslname show-description show-source show-value [not tag?]
        attributeUpdatedXmlList = updateXmlElement.getXmlElementListByName("attribute", True)
        for attributeUpdatedXmlElement in attributeUpdatedXmlList:
            tempatt = Attribute(self)
            tempatt.clearAssignables()
            tempatt.load(attributeUpdatedXmlElement, suppressAddName=True, suppressSetDefaultsForDatatype=True)
            atttag = tempatt.tag()
            if atttag and atttag in self._attributes:
                att = self._attributes[atttag]
                att.copyAssignables(tempatt)
                variableOrPort = att.getVariableFromSource()
                att.linkAttributeWithVariableOrPort(variableOrPort)

    def makeEslName(self, tag):
        prefix = 'E'
        if self._prefix: prefix = self._prefix
        intObjectId = int(self._objectId)
        objectIdStr = format(intObjectId, '04d')
        result = prefix + '_' + objectIdStr
        if tag:
            result += '_' + tag
        return result

    def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue): # Override this in any special types of simulation entity that have entity properties that need validating.
        valid = True
        rejection = ''
        updatedPropertyValue = None
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateEntityProperty(self, propertyTag, newValue, suppress_action=False): # Override this (and incorporate it) in any special types of simulation entity that have entity properties.
        # Property common to all simulation entities.
        refreshProperty = False
        if propertyTag == 'description':
            self.set_description(newValue)
        elif propertyTag == 'annotations':
            if 'Description' in newValue:
                self.set_show_description("true")
            else:
                self.set_show_description("false")
        return refreshProperty

    def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue) \
            -> (bool, str, str, str, str, str, str):         # Override this in any special types of simulation entity that have entity properties that need validating.
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, val_oldValue:str, val_newValue:str, updatedPropertyValue:str """
        # Attribute validation common to all simulation entities.
        valid = True
        rejection = ''
        updatedPropertyValue = None
        module = self.parent().parent()
        dummyAttribute = attribute.detachedCopy(attribute.parent())
        dummyAttribute.loadData(newValue, suppressAddName=True)
        if attribute.description():
            val_item += "." + attribute.description() # This (misnomer - should have been 'name') wont change by property change
        if attribute.eslname() != dummyAttribute.eslname():
            val_oldValue = attribute.eslname()
            val_newValue = dummyAttribute.eslname()
            val_item += ".ESL Name"
            if val_newValue:  # can unset attribute eslname
                errTxt = esl.ValidateName(val_newValue, silent=True)
                if errTxt:
                    rejection = 'not a valid ESL name - ' + errTxt
                    valid = False
                elif module.eslnameIsInModule(val_newValue):
                    rejection = 'name is already in use in ' + module.identification()
                    valid = False
            if rejection:
                val_item += ".ESL Name"
                val_oldValue = attribute.shortAttributeValueText(showName=True, showValue=False)
                val_newValue = dummyAttribute.shortAttributeValueText(showName=True, showValue=False)
        elif valid:
            if attribute.datatype().upper() in esl.EslTypeNames or attribute.datatype() == "ESLValue": # value should be an ESLValue
                valid, rejection, val_type, val_item, updatedESLValue = attribute.eslValue().validateESLValuePropertyChange(
                    dummyAttribute._eslValue, val_type, val_item)
                if valid:
                    if updatedESLValue is not None:
                        updatedValue = updatedESLValue.datatype()
                        if updatedValue != dummyAttribute.datatype():
                            dummyAttribute.set_datatype(updatedValue)
                        updatedValue = updatedESLValue.dimensions()
                        if updatedValue != dummyAttribute.dimensions():
                            dummyAttribute.set_dimensions(updatedValue)
                        updatedValue = updatedESLValue.valueStr()
                        if updatedValue != dummyAttribute.valueStr():
                            dummyAttribute.set_valueStr(updatedValue)
                        updatedPropertyValue = dummyAttribute.save(saveDefaults=True)
                if rejection:
                    val_item += ".Value"
                    val_oldValue = attribute.shortAttributeValueText(showName=True, showValue=True)
                    val_newValue = dummyAttribute.shortAttributeValueText(showName=True, showValue=True)
            pass
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False) -> bool: # Override this (and incorporate it) in any special types of simulation entity that have attribute properties.
        updateEntityPropertiesView = False
        oldName = tempOldAttribute.eslname()
        newName = attribute.eslname()
        if newName != oldName:
            module = self.parent().parent()
            if oldName:
                module.blockNames().delete(oldName)
            if newName:
                module.blockNames().add(newName, attribute)  # add eslname though not a variable
        return updateEntityPropertiesView

    def getAttribute(self, attributeTag):
        attribute = self._attributes.get(attributeTag)
        return attribute

    def validateEntityLinks(self, entityPortsConnectionsDict={}, portResolveDimensionsDict={}) -> (bool, str):   # Override this in any special types of simulation entity that need linkages validating.
        """ returns: valid:bool, rejection:str """
        valid = True
        rejection = ''
        return valid, rejection

    def entityResolvePortDimensions(self, port, entityPortsConnectionsDict={}, portResolveDimensionsDict={}) -> str:  # Override this in any special types of simulation entity that can (sometimes) resolve port dimensions
        """ returns: portDimensions:str """
        dimensions = None
        return dimensions
