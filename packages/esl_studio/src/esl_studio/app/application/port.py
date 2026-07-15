#! /usr/bin/python

import re
import inspect

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..esl import esl
from .module import Module
from .eslvalue import ESLValue
from ..esl.parseesl import ParseEsl, DimensionalityParseObject
from . import diagramactions as dgAction

PortIoDesignations = {  # for a designation - its 'kind' and 'direction'
    'input': ['ESL-value', 'input'],
    'output': ['ESL-value', 'output'],
    'natural-input': ['natural', 'input'],
    'natural-output': ['natural', 'output']
}

PortConnectorSeparator = '-'

class PortResolveDimensionsData:
    def __init__(self, data_id, resolvedState:str="", resolvedDimensions:str=None,
                 resolvedDimensionality:DimensionalityParseObject=None,
                 entityPortDependencies:list[str]=None, connectedPorts:list[str]=[], resolvedRejectMsg:str=""):
        self.data_id:str = data_id
        self.resolvedState:str = resolvedState
        self.resolvedDimensions:str = resolvedDimensions
        self.resolvedDimensionality:DimensionalityParseObject = resolvedDimensionality
        self.entityPortDependencies:list[str] = entityPortDependencies
        self.connectedPorts:list[str] = connectedPorts
        self.resolvedRejectMsg:str = resolvedRejectMsg

    def __str__(self):
        result = ("<"+self.data_id+"|"+self.resolvedState+":"+str(self.resolvedDimensions)+"|"+
                  str(self.resolvedDimensionality)+"|"+
                  str(self.entityPortDependencies)+"!"+
                  str(self.connectedPorts))
        if self.resolvedRejectMsg:
            result += "?"+self.resolvedRejectMsg
        result += ">"
        return result

class Port(object):
    PortDefaults = None
    ScalarFixDimensions = ["SCALAR", "-", "NOT", "NONE"]
    ConflictedDimensions = "CONFLICTED"
    ErrorDimensions = "ERROR"
    ResolvedStates = ["defined", "fixed", "resolved"]
    GenericOrResolvedStates = ["generic"] + ResolvedStates
    BadResolvedStates = ["conflicted", "error"]
    def __init__(self, parent, id="", datatype="", designation="", description="",
                 tag="", eslname="", dimensions="", initialValue=""):
        self._parent = parent
        self._id = id
        self._designation = designation
        self._kind = ""
        self._direction = ""
        if self._designation:
            ioInfo = PortIoDesignations.get(self._designation)
            if ioInfo:
                self._kind = ioInfo[0]
                self._direction = ioInfo[1]
        self._description = description
        self._tag = tag
        self._eslname = eslname
        self._eslValue = ESLValue(self, datatype, dimensions, initialValue)
        self._sign = ""
        self._fixDimensions = ""
        self._assignedAttributes = []
        self._show_id = "false"
        self._show_tag = "false"
        self._show_eslname = "false"
        self._show_description = "false"
        self._show_initialValue = "false"
        self._argument = None  # Holds ArgumentEntity for a diagram subprogram (not saved/loaded nor copied).

    def __str__(self):
        result = "<"+self.parent().identification() + "." + self.id()
        if self._eslname:
            result += ":" + self.eslname()
        result += ">"
        return result

    def parent(self): return self._parent
    def id(self): return self._id
    def kind(self): return self._kind
    def designation(self): return self._designation
    def direction(self): return self._direction
    def description(self): return self._description
    def tag(self): return self._tag
    def eslname(self): return self._eslname
    def datatype(self):
        return self._eslValue.datatype()
    def dimensions(self):
        return self._eslValue.dimensions()
    def eslValue(self):
        return self._eslValue
    def initialValueStr(self):
        return self._eslValue.valueStr()
    def getInitialisationValue(self, generateDefaultValue=False):
        return self._eslValue.getInitialisationValue(generateDefaultValue=generateDefaultValue)
    def sign(self): return self._sign
    def fixDimensions(self): return self._fixDimensions
    def show_id(self): return self._show_id
    def show_tag(self): return self._show_tag
    def show_eslname(self): return self._show_eslname
    def show_description(self): return self._show_description
    def show_initialValue(self): return self._show_initialValue

    def entityPortId(self):
        entityPortId = ""
        if self._parent:
            entityPortId = str(self._parent.objectId())+PortConnectorSeparator+str(self.id())
        return entityPortId

    def assignedAttributes(self): return self._assignedAttributes

    def set_description(self, value): self._description = value
    def set_eslname(self, value): self._eslname = value
    def set_sign(self, sign): self._sign = sign
    def set_fixDimensions(self, fixDimensions):
        self._fixDimensions = fixDimensions
    def set_datatype(self, datatype):
        self._eslValue.set_datatype(datatype)
    def set_dimensions(self, dimensions):
        self._eslValue.set_dimensions(dimensions)
    def set_initialValueStr(self, initialValueStr):
        self._eslValue.set_valueStr(initialValueStr)

    def set_show_id(self, value): self._show_id = value
    def set_show_tag(self, value): self._show_tag = value
    def set_show_eslname(self, value): self._show_eslname = value
    def set_show_description(self, value): self._show_description = value
    def set_show_initialValue(self, value): self._show_initialValue = value
    def argument(self): return self._argument
    def set_argument(self, value): self._argument = value

    def detachedCopy(self, parent):
        """ Copies from self to make a new Port with a new parent (may be None) """
        newPort = Port(parent)
        newPort.copyFrom(self, parent)
        return newPort

    def copyFrom(self, otherPort, parent):
        """ Copies from otherPort into the self except for parent which it updates (may set it None) """
        self._parent = parent
        self._id = otherPort._id
        self._designation = otherPort._designation
        self._kind = otherPort._kind
        self._direction = otherPort._direction
        self._tag = otherPort._tag
        self._description = otherPort._description
        self._eslname = otherPort._eslname
        self._eslValue.copyFrom(otherPort._eslValue, self)
        self._sign = otherPort._sign
        self._fixDimensions = otherPort._fixDimensions
        self._assignedAttributes = otherPort._assignedAttributes
        self._show_id = otherPort._show_id
        self._show_tag = otherPort._show_tag
        self._show_eslname = otherPort._show_eslname
        self._show_description = otherPort._show_description
        self._show_initialValue = otherPort._show_initialValue
        self._argument = otherPort._argument

    def copyAssignables(self, otherport):
        if otherport.datatype(): self.set_datatype(otherport.datatype())
        if otherport.dimensions(): self.set_dimensions(otherport.dimensions())
        otherEslValueSaveStr = otherport._eslValue.saveStr()
        if otherEslValueSaveStr != ESLValue.DefaultEslValueSaveStr:
            self._eslValue.loadStr(otherEslValueSaveStr, checkValidity=False)
        if otherport._eslname: self._eslname = otherport._eslname
        if otherport._description: self._description = otherport._description
        if otherport._sign: self._sign = otherport._sign
        if otherport._fixDimensions: self._fixDimensions = otherport._fixDimensions
        if otherport._show_id: self._show_id = otherport._show_id
        if otherport._show_tag: self._show_tag = otherport._show_tag
        if otherport._show_eslname: self._show_eslname = otherport._show_eslname
        if otherport._show_description: self._show_description = otherport._show_description
        if otherport._show_initialValue: self._show_initialValue = otherport._show_initialValue

    def set_parent(self, parent):
        self._parent = parent

    def load(self, portXmlElement, suppressAddName=False):
        val = portXmlElement.getAttribute("id")
        if val: self._id = val
        val = portXmlElement.getAttribute("type")
        if val is not None:
            self._eslValue.set_datatype(val)
        val = portXmlElement.getAttribute("dimensions")
        if val is not None:
            self._eslValue.set_dimensions(val)
        val = portXmlElement.name() # from model io - designation (input or output or ...)
        if val is None or val == "port":
            val = portXmlElement.getAttribute("designation")
            if val is None:
                val = portXmlElement.getAttribute("direction")
        if val is not None:
            self._designation = val
            ioInfo = PortIoDesignations.get(self._designation)
            if ioInfo:
                self._kind = ioInfo[0]
                self._direction = ioInfo[1]
        val = portXmlElement.getAttribute("description")
        if val is not None: self._description = val
        val = portXmlElement.getAttribute("tag")
        if val is not None: self._tag = val
        val = portXmlElement.getAttribute("eslname")
        if val is not None:
            self._eslname = val
            if self._eslname and not suppressAddName:
                module = self._parent
                while module and not isinstance(module, Module):
                    module = module.parent()
                if module:
                    module.blockNames().add(self._eslname, self)
        val = portXmlElement.getAttribute("initial-value")
        if val is not None:
            self._eslValue.loadStr(val)
        val = portXmlElement.getAttribute("sign")
        if val is not None: self._sign = val
        val = portXmlElement.getAttribute("fix-dimensions")
        if val is not None: self._fixDimensions = val
        val = portXmlElement.getAttribute("show-id")
        if val is not None: self._show_id = val
        val = portXmlElement.getAttribute("show-tag")
        if val is not None: self._show_tag = val
        val = portXmlElement.getAttribute("show-eslname")
        if val is not None: self._show_eslname = val
        val = portXmlElement.getAttribute("show-description")
        if val is not None: self._show_description = val
        val = portXmlElement.getAttribute("show-initial-value")
        if val is not None: self._show_initialValue = val

    def loadData(self, data, suppressAddName=False):
        xmlElement = xut.xmlElement(data)
        if xmlElement:
            self.load(xmlElement, suppressAddName)

    def save(self, indent=None, level=0, saveDefaults=False, savePortWithId=False, exemplarPort=None):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ""
        properties = ""
        if Port.PortDefaults is None:
            Port.PortDefaults = Port(None)
        exemplar = exemplarPort
        if exemplar is None:
            exemplar = Port.PortDefaults
        datatype = self.datatype()
        dimensions = self.dimensions()
        if saveDefaults or (datatype != exemplar.datatype() or dimensions != exemplar.dimensions()):
            properties += ' type="' + datatype + '"'
            properties += ' dimensions="' + dimensions + '"'
        if saveDefaults or self._tag != exemplar._tag:
            properties += ' tag="' + self._tag + '"'
        if saveDefaults or self._designation != exemplar._designation:
            properties += ' designation="' + self._designation + '"'
        if saveDefaults or self._eslname != exemplar._eslname:
            properties += ' eslname="' + self._eslname + '"'
        eslValueSaveStr = self._eslValue.saveStr()
        if saveDefaults or eslValueSaveStr != exemplar._eslValue.saveStr():
            properties += ' initial-value="' + xut.entitise(eslValueSaveStr) + '"'
        if saveDefaults or self._sign != exemplar._sign:
            properties += ' sign="' + self._sign + '"'
        if saveDefaults or self._fixDimensions != exemplar._fixDimensions:
            properties += ' fix-dimensions="' + self._fixDimensions + '"'
        if saveDefaults or self._description != exemplar._description:
            properties += ' description="' + xut.entitise(self._description) + '"'
        if saveDefaults or self._show_id != exemplar._show_id:
            properties += ' show-id="' + self._show_id + '"'
        if saveDefaults or self._show_tag != exemplar._show_tag:
            properties += ' show-tag="' + self._show_tag + '"'
        if saveDefaults or self._show_eslname != exemplar._show_eslname:
            properties += ' show-eslname="' + self._show_eslname + '"'
        if saveDefaults or self._show_description != exemplar._show_description:
            properties += ' show-description="' + self._show_description + '"'
        if saveDefaults or self._show_initialValue != exemplar._show_initialValue:
            properties += ' show-initial-value="' + self._show_initialValue + '"'
        if properties or savePortWithId:
            result = ind + '<port id="' + str(self._id) + '"' + properties + '/>' + nl
        return result

    def shortPortValueText(self, showName=True, showValue=False, showFixDimensions=False):
        val_text = "<port id=\""+str(self.id())+"\""
        val_text += " type=\""+self.datatype()
        dimensions = self.dimensions()
        if dimensions:
            val_text += "("+dimensions+")"
        val_text += "\""
        if showName and self._eslname:
            val_text += " name=\""+self._eslname+"\""
        if showValue and self._eslValue.saveStr() != ESLValue.DefaultEslValueSaveStr:
            val_text += " initial-value("+self._eslValue.mode()+")=\""+self._eslValue.valueStr()+"\""
        if showFixDimensions and self._fixDimensions:
            val_text += " fix-dimensions=\"" + self._fixDimensions + "\""
        val_text += ">"
        return val_text

    @staticmethod
    def validateCompatibleDimensionsSizes(thisDimensions, otherDimensions):
        valid = True
        rejection = ""
        bestDimensions = thisDimensions
        if thisDimensions == DimensionalityParseObject.UniversalToken:
            bestDimensions = otherDimensions
        if thisDimensions != DimensionalityParseObject.UniversalToken and otherDimensions != DimensionalityParseObject.UniversalToken: # any (valid) fixed dimensions valid if this is universal
            #pos, thisDimensionality = self._eslValue.parseEsl().parseDimensions(thisDimensions, 0, None, checkNothingLeft=False, allowStar=True)
            thisDimensionality = ParseEsl.get_dimensionality(thisDimensions, checkNothingLeft=False, allowStar=True)
            otherDimensionality = None
            if thisDimensionality is None:
                valid = False
                rejection = "error re-parsing dimensions (%s)" % thisDimensions
            if valid:
                #pos, otherDimensionality = self._eslValue.parseEsl().parseDimensions(otherDimensions, 0, None, checkNothingLeft=False, allowStar=False)
                otherDimensionality = ParseEsl.get_dimensionality(otherDimensions, checkNothingLeft=False, allowStar=True)
                if otherDimensionality is None:
                    valid = False
                    rejection = "error re-parsing other dimensions (%s)" % otherDimensions
            if valid:
                thisDimensionalityNumber = thisDimensionality.number()
                if thisDimensionalityNumber != otherDimensionality.number():
                    valid = False
                    rejection = "not same number of dimensions (%s vs %s)" % (thisDimensions, otherDimensions)
                if valid:
                    thisDimensionalitySizes = thisDimensionality.sizes()
                    otherDimensionalitySizes = otherDimensionality.sizes()
                    bestDimensions = ""
                    for ix in range(thisDimensionalityNumber):
                        if (thisDimensionalitySizes[ix] != DimensionalityParseObject.StarDimension and
                            (otherDimensionalitySizes[ix] != DimensionalityParseObject.StarDimension and thisDimensionalitySizes[ix] != otherDimensionalitySizes[ix])):
                            valid = False
                            rejection = "dimension ("+str(ix+1)+") size not compatible (%s vs %s)" % (thisDimensions, otherDimensions)
                            break
                        if bestDimensions: bestDimensions += ","
                        if thisDimensionalitySizes[ix] == DimensionalityParseObject.StarDimension:
                            size = otherDimensionalitySizes[ix]
                            if size == DimensionalityParseObject.StarDimension: size = "*"
                            bestDimensions += str(size)
                        else:
                            size = thisDimensionalitySizes[ix]
                            if size == DimensionalityParseObject.StarDimension: size = "*"
                            bestDimensions += str(size)
                    pass
                pass
            pass
        return valid, rejection, bestDimensions

    @staticmethod
    def validateDimensionsForJoinedPorts(joinedPorts) -> (bool, str):
        valid = True
        msg = ""
        joinedDimensions = []
        joinedDimensionalities = []
        for port in joinedPorts:
            portStr = port.parent().identification()+"."+port.id()
            dimensions = port.dimensions()
            if port.isGeneric():
                fixDimensions = port.fixDimensions()
                if fixDimensions:
                    dimensions = fixDimensions
            joinedDimensions.append(dimensions)
            dimensionality = None
            if dimensions is not None:
                dimensionality = ParseEsl.get_dimensionality(dimensions, checkNothingLeft=False, allowStar=True)
                if len(dimensionality.messages) > 0:
                    thisMsg = portStr
                    for message in dimensionality.messages:
                        if dimensions != DimensionalityParseObject.UniversalToken or not message.message.startswith("no bounds"):
                            valid = False
                            thisMsg += " " + message.message
                            msg += thisMsg + "\n"
            joinedDimensionalities.append(dimensionality)
        if len(joinedPorts) > 1:
            pairOfIndices = pairwiseIndices(len(joinedPorts))
            for pair in pairOfIndices:
                i = pair[0]
                j = pair[1]
                portStrI = joinedPorts[i].parent().identification()+"."+joinedPorts[i].id()
                portStrJ = joinedPorts[j].parent().identification()+"."+joinedPorts[j].id()
                if (joinedDimensions[i] != DimensionalityParseObject.UniversalToken and
                    joinedDimensions[j] != DimensionalityParseObject.UniversalToken):
                    if (joinedDimensions[i] == "" and joinedDimensions[j] != "" or
                        joinedDimensions[i] != "" and joinedDimensions[j] == ""):
                        valid = False
                        msg += portStrI + " and "+ portStrJ + " not both scalar" + "\n"
                    if joinedDimensionalities[i].number() != joinedDimensionalities[j].number():
                        valid = False
                        msg += portStrI + " and "+ portStrJ + " not same number of dimensions" + "\n"
                    else:
                        sizesI = joinedDimensionalities[i].sizes()
                        sizesJ = joinedDimensionalities[j].sizes()
                        for ix in range(len(sizesI)):
                            if (sizesI[ix] != DimensionalityParseObject.StarDimension and
                                sizesJ[ix] != DimensionalityParseObject.StarDimension and
                                sizesI[ix] != sizesJ[ix]):
                                valid = False
                                msg += portStrI + " and "+ portStrJ + " dimension ("+str(ix+1)+") size not compatible" + "\n"
                                break
                        pass
        return valid, msg

    def validatePortPropertyChange(self, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue) -> (bool, str, str, str, str, str, str):
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, val_oldValue:str, val_newValue:str, updatedPropertyValue:str """
        valid = True
        rejection = ""
        updatedPropertyValue = None
        dummyPort = Port(None)
        dummyPort.loadData(newValue)
        val_item += ".Port " + str(self._id)
        if self.eslname().upper() != dummyPort.eslname().upper():
            #oldName = self.eslname()
            newName = dummyPort.eslname()
            #val_item += ".ESL Name" - don't need to append this now using shortPortValueText
            module = self._parent
            while module and not isinstance(module, Module):
                module = module.parent()
            if newName: # can unset port eslname
                errTxt = esl.ValidateName(newName, silent=True)
                if errTxt:
                    rejection = "not a valid ESL name - " + errTxt
                    valid = False
                elif module.eslnameIsInModule(newName):
                    rejection = "name \""+newName+"\" is already in use in " + module.identification()
                    valid = False
            else:  # unless being used (attribute variable)
                if len(self.assignedAttributes()) > 0:
                    rejection = "cannot unset port name as this port is being used for an attribute value"
                    valid = False
            if rejection:
                val_item += ".ESL Name"
                val_oldValue = self.shortPortValueText(showName=True, showValue=False)
                val_newValue = dummyPort.shortPortValueText(showName=True, showValue=False)
        if valid:
            valid, rejection, val_type, val_item, updatedESLValue = self._eslValue.validateESLValuePropertyChange(
                dummyPort._eslValue, val_type, val_item)
            if valid:
                if updatedESLValue is not None:
                    updatedValue = updatedESLValue.valueStr()
                    if updatedValue != dummyPort._eslValue.valueStr():
                        dummyPort._eslValue.set_valueStr(updatedValue)
                    updatedPropertyValue = dummyPort.save(saveDefaults=True)
            if rejection:
                val_item += ".Initial Value"
                val_oldValue = self.shortPortValueText(showName=True, showValue=True)
                val_newValue = dummyPort.shortPortValueText(showName=True, showValue=True)
        if valid:
            fixDimensions = dummyPort.fixDimensions()
            if fixDimensions != self._fixDimensions:
                entity = self._parent
                if entity:
                    diagramInfo = entity.parent()
                    portsConnections = diagramInfo.canvas().EstablishPortsConnections(entity.objectId())
                    thisPortConnected = False
                    entityPortId = self.entityPortId()
                    for pair in portsConnections:
                        if pair[0] == entityPortId:
                            thisPortConnected = True if len(pair[1]) else False
                            break
                    if thisPortConnected:
                        rejection = "cannot fix the dimensions for a generic port while it is connected ("+entity.identification()+")"
                        valid = False
                if valid:
                    if fixDimensions != "": # which is valid
                        if dummyPort.dimensions() == DimensionalityParseObject.UniversalToken and fixDimensions.upper() in Port.ScalarFixDimensions:
                            standardisedDimensions = Port.ScalarFixDimensions[0] # SCALAR
                        else:
                            valid, rejection, standardisedDimensions = self._eslValue.validateESLValueDimensions(fixDimensions)
                        if valid:
                            valid, rejection, bestDimensions = Port.validateCompatibleDimensionsSizes(self.dimensions(), fixDimensions)
                        if valid:
                            if standardisedDimensions != fixDimensions:
                                dummyPort.set_fixDimensions(standardisedDimensions)
                                updatedPropertyValue = dummyPort.save(saveDefaults=True)
                if rejection:
                    val_item += ".Fix Dimensions"
                    val_oldValue = self.shortPortValueText(showName=True, showValue=False, showFixDimensions=True)
                    val_newValue = dummyPort.shortPortValueText(showName=True, showValue=False, showFixDimensions=True)
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updatePortProperty(self, propertyTag, newValue, suppress_action=False):
        entity = self._parent
        module = None
        canvas = None
        if entity:
            diagramInfo = entity.parent()
            if diagramInfo:
                module = diagramInfo.parent()
                canvas = diagramInfo.canvas()
        oldName = self.eslname()
        oldSign = self.sign()
        oldFixDimensions = self.fixDimensions()
        self.loadData(newValue, suppressAddName=True)
        newName = self.eslname()
        newSign = self.sign()
        newFixDimensions = self.fixDimensions()
        if newName != oldName:
            if oldName:
                module.blockNames().delete(oldName)
            if newName:
                module.blockNames().add(newName, self) # add eslname though not a variable
            for attribute in self.assignedAttributes():
                attribute.set_valueStr(newName)
                annotationId, annotationTxt, annotationVisible = dgAction.setEntityAttributeAnnotations(attribute)
                dgAction.sendAnnotationUpdate(entity, annotationId, annotationTxt, annotationVisible)
        if newSign != oldSign or newFixDimensions != oldFixDimensions:
            updateXmlStr = dgAction.makeUpdateEntityPortActionStr(entity, self)
            dgAction.sendDiagramUpdate(entity.parent(), updateXmlStr, applicationDataType="", applicationDataContents="", secondary=False, raiseEvent=False)
            canvas.Refresh()
        annotationId, annotationTxt, annotationVisible = dgAction.setEntityPortAnnotations(entity, self)
        dgAction.sendAnnotationUpdate(entity, annotationId, annotationTxt, annotationVisible)

    def isGeneric(self) -> bool:
        result = Port.isGenericDimensions(self.dimensions())
        return result

    def fixedDimensions(self) -> str:
        # assumes standardised form for dimensions
        dimensions = None
        if not self.isGeneric():
            dimensions = self.dimensions()
        else:
            fixDimensions = self.fixDimensions()
            if fixDimensions:
                if fixDimensions == Port.ScalarFixDimensions[0]:
                    dimensions = ""
                else:
                    dimensions = fixDimensions
            if dimensions is not None and dimensions != "" and not re.match(r"[-\d\.,]+", dimensions): # allow if blank(for scalar) or contains only minus digits dots and commas
                dimensions = None
        return dimensions

    def gatherPortDependencies(self, entityPortsConnectionsDict={}) -> (list[str], list[str]):
        """ returns: entityPortDependencies, connectedPorts - both list of entityPortIds (str) to be resolved for this port to be resolved. """
        entityPortId = self.entityPortId()
        entity = self._parent
        entityPortDependencies = entity.entityResolvePortDimensionsPortDependencies(entityPortId)
        diagramInfo = entity.parent()
        entitysPortsConnections = entityPortsConnectionsDict.get(entity)
        if entitysPortsConnections is None:
            entitysPortsConnections = diagramInfo.canvas().EstablishPortsConnections(entity.objectId())
            entityPortsConnectionsDict[entity] = entitysPortsConnections
        connectedPorts = getPortsConnections(entitysPortsConnections, entityPortId)
        if connectedPorts is not None:
            connectedPorts.sort()
        return entityPortDependencies, connectedPorts

    def getPortResolveDimensionsData(self, entityPortsConnectionsDict={}, portResolveDimensionsDict={}, debugging=False) -> PortResolveDimensionsData:
        entityPortId = self.entityPortId()
        portResolveDimensionsData = portResolveDimensionsDict.get(entityPortId)
        if portResolveDimensionsData is None:
            resolvedState = ""
            dimensions = self.dimensions()
            entityPortDependencies = None
            connectedPorts = []
            if dimensions is not None:
                resolvedState = "defined"  # note: dimensions can be "" for scalar
            if dimensions and (
                    dimensions == DimensionalityParseObject.UniversalToken or dimensions.find("*") != -1):
                resolvedState = "generic"
                fixDimensions = self.fixDimensions()
                if fixDimensions:
                    if fixDimensions == Port.ScalarFixDimensions[0]:
                        dimensions = ""
                    else:
                        dimensions = fixDimensions
                    resolvedState = "fixed"
                else:
                    entityPortDependencies, connectedPorts = self.gatherPortDependencies(entityPortsConnectionsDict=entityPortsConnectionsDict)
            if not resolvedState:
                raise Exception(
                    "Port.getPortResolveDimensionsData failed to establish initial resolved state for port %s" % self.entityPortId())
            dimensionality = ParseEsl.get_dimensionality(dimensions, checkNothingLeft=False, allowStar=True)
            data_id = str(self._parent.parent().parent().moduleId())+":"+entityPortId
            portResolveDimensionsData = PortResolveDimensionsData(data_id, resolvedState, dimensionality.dimensions(),
                                                                  dimensionality, entityPortDependencies, connectedPorts)
            portResolveDimensionsDict[entityPortId] = portResolveDimensionsData
        else:
            if debugging: print(
                "-Port.resolvePortDimensions portId=" + entityPortId + " previously resolved data=" + str(
                    portResolveDimensionsData))
            pass
        pass
        return portResolveDimensionsData

    def collectPortsToResolve(self, entityPortsConnectionsDict={}, portResolveDimensionsDict={}, debugging=False):
        if debugging:
            print(">***[%d] Port.collectPortsToResolve portId=%s" %(len(inspect.stack()), self.entityPortId()))
            if portResolveDimensionsDict:
                print(">  portResolveDimensionsDict=")
                for key, value in portResolveDimensionsDict.items():
                    print(">  " + str(key) + ": " + str(value))
        portResolveDimensionsData = None
        collectingPorts = True
        entity = self._parent
        diagramInfo = entity.parent()
        while collectingPorts:
            lenPortResolveDimensionsDict = len(portResolveDimensionsDict)
            portResolveDimensionsData = self.getPortResolveDimensionsData(
                entityPortsConnectionsDict=entityPortsConnectionsDict,
                portResolveDimensionsDict=portResolveDimensionsDict, debugging=debugging)
            if (lenPortResolveDimensionsDict != len(portResolveDimensionsDict)):
                portDependencies = []
                if portResolveDimensionsData.entityPortDependencies is not None:
                    portDependencies = portResolveDimensionsData.entityPortDependencies
                portDependencies.extend(portResolveDimensionsData.connectedPorts)
                if portDependencies is not None:
                    if debugging and len(portDependencies) > 0:
                        print("----[%2d] Port.collectPortsToResolve portId=%s has dependencies(%d): %s" %
                              (len(inspect.stack()), self.entityPortId(), len(portDependencies), str(portDependencies)))
                    for entityPortId in portDependencies:
                        otherEntity, otherPort = Port.getEntityAndPort(diagramInfo, entityPortId)
                        dimensionsData = otherPort.collectPortsToResolve(
                            entityPortsConnectionsDict=entityPortsConnectionsDict,
                            portResolveDimensionsDict=portResolveDimensionsDict, debugging=debugging)
            else:
                collectingPorts = False
        pass # end-while
        if debugging:
            print("<***[%2d] Port.collectPortsToResolve portId=%s portResolveDimensionsData=%s"
                  % (len(inspect.stack()), self.entityPortId(), str(portResolveDimensionsData)))
            if portResolveDimensionsDict:
                print("<  portResolveDimensionsDict=")
                for key, value in portResolveDimensionsDict.items():
                    print("<   " + str(key) + ": " + str(value))

    def tryResolvingPort(self, entityPortsConnectionsDict={}, portResolveDimensionsDict={},
                         debugging=False) -> (bool, PortResolveDimensionsData):
        changed = False
        entityPortId = self.entityPortId()
        if debugging: print(">Port.tryResolvingPort portId=%s" % entityPortId)
        portResolveDimensionsData = portResolveDimensionsDict.get(entityPortId)
        dependenciesDimensionsList = []
        if portResolveDimensionsData.entityPortDependencies is not None:
            entity = self._parent
            entityPortDimensions = entity.entityResolvePortDimensions(self, entityPortsConnectionsDict,
                                                                      portResolveDimensionsDict, debugging)
            if entityPortDimensions is not None:
                dependenciesDimensionsList.append(entityPortDimensions)

        for otherEntityPortId in portResolveDimensionsData.connectedPorts:
            otherPortResolveDimensionsData = portResolveDimensionsDict.get(otherEntityPortId)
            if otherPortResolveDimensionsData.resolvedState in Port.GenericOrResolvedStates: # not conflicted or error
                dependenciesDimensionsList.append(otherPortResolveDimensionsData.resolvedDimensions)
            else:
                if otherPortResolveDimensionsData.resolvedState in Port.BadResolvedStates:
                    portResolveDimensionsData.resolvedState = "error"
                    portResolveDimensionsData.resolvedDimensions = Port.ErrorDimensions
                    rejectMsg = portResolveDimensionsData.resolvedRejectMsg
                    if not rejectMsg:
                        rejectMsg = "Failed to resolve resolved dimensions for %s" % entityPortId
                    rejectMsg += (" - port %s resolved state %s " %
                                  (otherEntityPortId, otherPortResolveDimensionsData.resolvedState))
                    portResolveDimensionsData.resolvedRejectMsg = rejectMsg
                    changed = True
                else: # shouldn't have happened
                    raise Exception("Unexpected resolved state \"%s\" for port-id %d" %
                                    (otherPortResolveDimensionsData.resolvedState, otherEntityPortId))
                pass
        pass # end for other dependencies
        if portResolveDimensionsData.resolvedState != "error" and len(dependenciesDimensionsList) > 0:
            dependenciesDimensionsList.insert(0, portResolveDimensionsData.resolvedDimensions)  # include self first in the reconciliation
            reconciledDimensions, reconciledRejectMsg = Port.reconcileConnectedDimensions(
                dependenciesDimensionsList, debugging)
            if reconciledDimensions == Port.ConflictedDimensions:
                portResolveDimensionsData.resolvedState = "conflicted"
                portResolveDimensionsData.resolvedDimensions = reconciledDimensions # i.e. Port.ConflictedDimensions
                if reconciledRejectMsg:
                    portResolveDimensionsData.resolvedRejectMsg = reconciledRejectMsg
                else:
                    portResolveDimensionsData.resolvedRejectMsg = "conflicting dimensions"
                changed = True
            elif reconciledRejectMsg:
                portResolveDimensionsData.resolvedState = "error"
                portResolveDimensionsData.resolvedDimensions = Port.ErrorDimensions
                portResolveDimensionsData.resolvedRejectMsg = reconciledRejectMsg
                changed = True
            elif reconciledDimensions is not None and reconciledDimensions != portResolveDimensionsData.resolvedDimensions:
                if not Port.isGenericDimensions(reconciledDimensions):
                    portResolveDimensionsData.resolvedState = "resolved"
                portResolveDimensionsData.resolvedDimensions = reconciledDimensions
                # should we have a reconciledDimensionality from reconcileConnectedDimensions - if not, or till then
                portResolveDimensionsData.resolvedDimensionality = ParseEsl.get_dimensionality(reconciledDimensions,
                                                                                       checkNothingLeft=False,
                                                                                       allowStar=True)
                changed = True
        pass # end if others are resolved
        if debugging: print("<Port.tryResolvingPort portId=%s resolved=%s portResolveDimensionsData=%s" %
                            (entityPortId, str(changed), str(portResolveDimensionsData)))
        return changed, portResolveDimensionsData

    def resolvePortDimensions(self, entityPortsConnectionsDict={}, portResolveDimensionsDict={}, debugging=False) -> PortResolveDimensionsData:
        # entityPortsConnectionsDict is a dict of simulation-entity containing the (full) EstablishPortsConnections data (list-tree of str) from the diagram for the entity
        # portResolveDimensionsDict is a dict of port containing a list [ resolvedState:str, resolvedDimensions:str, resolvedDimensionality:DimensionalityParseObject]
        # where resolvedState can be ""(=not yet determined ?or error) "defined", "fixed", "generic", resolving" "resolved-by-connections" resolved-by-entity" "conflicted"
        # resolvedDimensions is "" for a scalar, otherwise (generally) the standard form for a set of dimensions (may be ... or include * if generic)
        # resolvedDimensionality is the result of parsing dimensions [or may/or may not be None for scalar] - shouldn't happen but may have parsing messages if error encountered
        # resolvedRejectMsg if error during the resolve
        if debugging:
            print(">***[%d] Port.resolvePortDimensions portId=%s" %(len(inspect.stack()), self.entityPortId()))
            if portResolveDimensionsDict:
                print(">  portResolveDimensionsDict=")
                for key, value in portResolveDimensionsDict.items():
                    print(">  " + str(key) + ": " + str(value))

        self.collectPortsToResolve(entityPortsConnectionsDict=entityPortsConnectionsDict,
                                   portResolveDimensionsDict=portResolveDimensionsDict, debugging=debugging)

        portResolveDimensionsData = portResolveDimensionsDict.get(self.entityPortId())
        last_resolved_state = portResolveDimensionsData.resolvedState

        entity = self._parent
        diagramInfo = entity.parent()

        resolving = True
        nrChanges = 0
        passCount = 1
        passCountMax = 20 * len(portResolveDimensionsDict)
        while resolving:
            nrChanges = 0
            if debugging:
                nrGenerics = len(list(filter(lambda portData: portData.resolvedState == "generic", portResolveDimensionsDict.values())))
                print("-Port.resolvePortDimensions doing passCount=%d portId=%s nrGenerics=%d (in %d)" %
                      (passCount, self.entityPortId(), nrGenerics, len(portResolveDimensionsDict)))
                if portResolveDimensionsDict:
                    print(">  portResolveDimensionsDict=")
                    for key, value in portResolveDimensionsDict.items():
                        print(">  " + str(key) + ": " + str(value))
            for entityPortId, entityPortResolveDimensionsData in portResolveDimensionsDict.items():
                if entityPortResolveDimensionsData.resolvedState == "generic":
                    otherEntity, otherPort = Port.getEntityAndPort(diagramInfo, entityPortId)
                    changed, entityPortResolveDimensionsData = otherPort.tryResolvingPort(
                        entityPortsConnectionsDict=entityPortsConnectionsDict,
                        portResolveDimensionsDict=portResolveDimensionsDict, debugging=debugging)
                    if changed:
                        nrChanges += 1
            pass # end pass trying to resolve
            if debugging:
                print("-Port.resolvePortDimensions done passCount=%d portId=%s nrChanges=%d " %
                      (passCount, self.entityPortId(), nrChanges))
            if nrChanges == 0:
                resolving = False
            else:
                passCount += 1
                if passCount > passCountMax:
                    resolving = False
        pass # end while resolving

        if debugging:
            change = " "
            if last_resolved_state != portResolveDimensionsData.resolvedState:
                change = "changed from '"+last_resolved_state+"' to '"+portResolveDimensionsData.resolvedState+"' "
            print("<***[%2d] Port.resolvePortDimensions portId=%s %sportResolveDimensionsData=%s"
                %(len(inspect.stack()), self.entityPortId(), change, str(portResolveDimensionsData)))
            if portResolveDimensionsDict:
                print("<  portResolveDimensionsDict=")
                for key, value in portResolveDimensionsDict.items():
                    print("<   " + str(key) + ": " + str(value))
        if passCount > passCountMax:
            raise Exception("Broke loop resolving port dimensions -  portId=%s passCount=%d"
                            %(self.entityPortId(), passCount))
        return portResolveDimensionsData

    @staticmethod
    def getEntityAndPort(diagramInfo, portId) -> ('SimulationEntity', 'Port'):
        entity = None
        port = None
        portIdSplit = portId.split(PortConnectorSeparator)
        if len(portIdSplit) > 1:
            entityId = portIdSplit[0]
            ports_id = portIdSplit[1]
            entity = diagramInfo.simulationEntities().get(entityId)
            if entity is not None:
                port = entity.ports().get(ports_id)
        return entity, port

    @staticmethod
    def reconcileConnectedDimensions(connectedDimensionsList, debugging=False):
        if debugging: print(">Port.reconcileConnectedDimensions connectedDimensionsList=" + str(connectedDimensionsList))
        dimensions = None
        rejectMsg = ""
        if len(connectedDimensionsList) > 1:
            pickedDimensions = connectedDimensionsList[0]
            valid = True
            for otherDimensions in connectedDimensionsList[1:]:
                if otherDimensions != pickedDimensions:
                    valid, rejection, bestDimensions = Port.validateCompatibleDimensionsSizes(pickedDimensions, otherDimensions)
                    if not valid:
                        break
                    pickedDimensions = bestDimensions
            if not valid:
                dimensions = Port.ConflictedDimensions
                rejectMsg = "Conflicting resolved connections"
                if rejection: rejectMsg += " ("+rejection+")"
            else:
                dimensions = pickedDimensions
        if debugging: print("<Port.reconcileConnectedDimensions dimensions="+str(dimensions)+" rejectMsg="+rejectMsg)
        return dimensions, rejectMsg

    def generateArrayElementReferences(self, dimensions):
        # assumes dimensions is fixed (numerical bounds)
        # note does not include enclosing brackets
        refsList = []
        if dimensions:
            pos, dimensionality = self._eslValue.parseEsl().parseDimensions(dimensions, 0, None, checkNothingLeft=False, allowStar=False)
            if dimensionality is not None:
                number = dimensionality.number()
                bounds = dimensionality.bounds()
                for ix1 in range(bounds[0][0],bounds[0][1]+1):
                    ref1 = str(ix1)
                    if number >= 2:
                        for ix2 in range(bounds[1][0],bounds[1][1]+1):
                            ref2 = ref1+","+str(ix2)
                            if number == 3:
                                for ix3 in range(bounds[2][0],bounds[2][1]+1):
                                    ref3 = ref2+","+str(ix3)
                                    refsList.append(ref3)
                            else:
                                refsList.append(ref2)
                    else:
                        refsList.append(ref1)
        return refsList

    @staticmethod
    def isGenericDimensions(dimensions):
        result = False
        if dimensions and (dimensions == DimensionalityParseObject.UniversalToken or dimensions.find("*") != -1):
            result = True
        return result

def getPortsConnections(entitysPortsConnections, portId):
    thisPortsConnections = None
    for pair in entitysPortsConnections:
        if pair[0] == portId:
            thisPortsConnections = pair[1]
            break
    return thisPortsConnections

def pairwiseIndices(n):
    pairOfIndices = []
    for i in range(n):
        for j in range(i+1, n):
            pairOfIndices.append((i, j))
    return pairOfIndices
