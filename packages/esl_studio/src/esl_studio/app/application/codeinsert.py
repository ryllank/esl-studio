#! /usr/bin/python

import re
from collections import OrderedDict

from .. import utils as Utils
from ..esl.esl import EslBaseTypeNames
from ..esl.parseesl import ParseEsl, DimensionalityParseObject
from .simulationentity import SimulationEntity
from .port import Port
from . import diagramactions as dgAction

_DatatypeSeparator = ";"
_DatatypeBracketsRegex = re.compile(r"\s*([^\(]+)\(([^\)]+)\)\s*")

class CodeInsert(SimulationEntity):

    Region_values = ["declarations", "initial", "dynamic", "step", "communication", "terminal", "analysis"]
    Region_default = "communication"
    Insert_values = ["beginning", "end"]
    Insert_default = "end"
    Regions_for_outputs = ["dynamic", "step", "communication"]

    def __init__(self, parent, type="", objectId=""):
        SimulationEntity.__init__(self, parent, type, objectId)
        self._region = CodeInsert.Region_default
        self._insert_position = CodeInsert.Insert_default
        self._esl:str = ""
        self._outputs:str = ""
        self._parseEsl = ParseEsl()

    def region(self):
        return self._region
    def set_region(self, region):
        self._region = region
    def insert_position(self):
        return self._insert_position
    def set_insert_position(self, insert_position):
        self._insert_position = insert_position
    def esl(self):
        return self._esl
    def set_esl(self, esl):
        self._esl = esl
    def outputs(self):
        return self._outputs
    def set_outputs(self, outputs):
        self._outputs = outputs

    def load(self, entityDescrXmlElement, suppressAddName=False):
        super(CodeInsert, self).load(entityDescrXmlElement, suppressAddName)
        val = entityDescrXmlElement.getAttribute("region")
        if val is not None:
            self._region = val
        val = entityDescrXmlElement.getAttribute("insert-position")
        if val is not None:
            self._insert_position = val
        eslXmlElement = entityDescrXmlElement.getXmlElementByName("esl")
        if eslXmlElement:
            self._esl = eslXmlElement.getContent()
        val = entityDescrXmlElement.getAttribute("outputs")
        if val is not None:
            self._outputs = val
        self.setupCodeInsertPorts(self._outputs)

    def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False): # Override this in any special types of simulation entity which have to add additional XML attributes text.
        xmlAttributeText = ""
        if self._region != CodeInsert.Region_default or saveDefaults:
            xmlAttributeText += ' region="' + self._region+'"'
        if self._insert_position != CodeInsert.Insert_default or saveDefaults:
            xmlAttributeText += ' insert-position="' + self._insert_position+'"'
        if self._outputs != "" or saveDefaults:
            xmlAttributeText += ' outputs="' + self._outputs+'"'
        return xmlAttributeText

    def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False):
        xmlContentsText = ""
        if self._esl or saveDefaults:
            nl, ind, ind2 = Utils.indentation(indent, level)
            xmlContentsText += ind + '<esl>' + nl
            xmlContentsText += ind2 + '<![CDATA[' + str(self._esl) + ']]>' + nl
            xmlContentsText += ind + '</esl>' + nl
        return xmlContentsText

    def updateEntity(self, updateXmlElement):
        val = updateXmlElement.getAttribute("region")
        if val:
            self.set_region(val)
        val = updateXmlElement.getAttribute("insert-position")
        if val:
            self.set_insert_position(val)
        val = ""
        eslXmlElement = updateXmlElement.getXmlElementByName("esl")
        if eslXmlElement:
            val = eslXmlElement.getContent()
        if val:
            self.set_esl(val)
        val = updateXmlElement.getAttribute("outputs")
        if val:
            self.set_outputs(val)
        super(CodeInsert, self).updateEntity(updateXmlElement)

    def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue):
        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = \
            super(CodeInsert, self).validateEntityPropertyChange(propertyTag, newValue, val_type, val_item, val_oldValue, val_newValue)
        if valid:
            if propertyTag == 'outputs':
                val_item = "Code Insert"
                if newValue != '':
                    newValues = newValue.split(_DatatypeSeparator)
                    for val in newValues:
                        val = val.strip()
                        parseRejection, valBaseDatatype, dimensionality = self.parseDatatype(val)
                        if parseRejection:
                            rejection += parseRejection
                            valid = False
                        if valBaseDatatype.upper() not in EslBaseTypeNames:
                            valid = False
                            rejection += "\""+val+"\" is a not a valid ESL Datatype "
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateEntityProperty(self, propertyTag, newValue, suppress_action=False):
        refreshProperty = super(CodeInsert, self).updateEntityProperty(propertyTag, newValue, suppress_action=suppress_action)
        if propertyTag == 'region':
            self.set_region(newValue)
            refreshProperty = True # to be able to check if Output Ports enabled or not
        elif propertyTag == 'insert':
            self.set_insert_position(newValue)
        elif propertyTag == 'esl':
            self.set_esl(newValue)
        elif propertyTag == 'outputs':
            if newValue != '':
                newValues = newValue.split(_DatatypeSeparator)
                sanitisedValues = []
                for val in newValues:
                    sanitisedValues.append(val.strip().title())
                newValue = _DatatypeSeparator.join(sanitisedValues)
            if not suppress_action:
                self.doCodeInsertPortsChange(newValue) # before newValue set for entity (so as to get undo-updated info)
            else:
                self.setupCodeInsertPorts(newValue)
            self.set_outputs(newValue)
            refreshProperty = True
        return refreshProperty

    def getPorts(self, outputsStr):
        ports = OrderedDict()
        if outputsStr:
            count = 1
            outputDatatypes = outputsStr.split(_DatatypeSeparator)
            for outputDatatype in outputDatatypes:
                dimensions = ""
                rejection, baseDatatype, dimensionality = self.parseDatatype(outputDatatype)
                if baseDatatype:
                    if dimensionality is not None and dimensionality.usable:
                        dimensions = dimensionality.dimensions()
                    port = Port(None, str(count), baseDatatype, "output", "", "")
                    if dimensions:
                        port.set_dimensions(dimensions)
                    ports[str(count)] = port
                    count += 1
        return ports

    #def initPortsNAttributes(self, entities):
    #    pass

    def doCodeInsertPortsChange(self, outputsStr):
        diagramInfo = self._parent
        canvas = diagramInfo.canvas()
        ports = self.getPorts(outputsStr)
        undoChangeApplicationData = self._application.setupUndoChangeApplicationData(canvas, [self])
        annotationsChangeInfo = self.setupCodeInsertPorts(outputsStr)
        portsActionStr = dgAction.makeSubprogramPortsActionStr(ports)
        updateActionStr = dgAction.makeUpdateSubprogramCallActionStr(self, portsActionStr,
                                                                     annotationsChangeInfo=annotationsChangeInfo)
        applicationDataContents = "<undo-updated>" + undoChangeApplicationData.xml() + "</undo-updated>"
        dgAction.sendDiagramUpdate(diagramInfo, updateActionStr, applicationDataType="",
                                   applicationDataContents=applicationDataContents, secondary=True, # using False seemed to help (no crashes) but alteration stack got in a mess
                                   raiseEvent=True)  # or should that be raiseEvent=False
        canvas.Refresh()

    def setupCodeInsertPorts(self, outputsStr):
        commonPortIdAnnotationPairDict = {}
        obsoletePortIdToAnnotationIdDict = {}
        priorPorts = list(self._ports.values())
        portIx = 0
        for priorPort in priorPorts:
            portIx += 1
            portAnnotationId = "port-" + str(portIx)
            obsoletePortIdToAnnotationIdDict[priorPort.id()] = portAnnotationId
        currentPorts = self.getPorts(outputsStr)
        for port in list(currentPorts.values()): port.set_parent(self)
        portIx = 0
        for port in list(currentPorts.values()):
            priorPort = None
            portAnnotationId = "port-"
            if portIx < len(priorPorts):
                priorPort = priorPorts[portIx]
            portIx += 1
            portAnnotationId += str(portIx)
            if priorPort:
                if (not priorPort.datatype() or priorPort.datatype() == port.datatype()) and priorPort.direction() == port.direction():
                    priorPortAnnotationId = obsoletePortIdToAnnotationIdDict[priorPort.id()]
                    commonPortIdAnnotationPairDict[port.id()] = (portAnnotationId, priorPortAnnotationId)
                    del obsoletePortIdToAnnotationIdDict[priorPort.id()]  # prior port is replaced by this port - so remove from obsolete port annotation info
                    port.copyAssignables(priorPort)
        self._ports = currentPorts
        commonAttributeTagAnnotationPairDict = {}
        obsoleteAttributeTagToAnnotationIdDict = {}
        return commonPortIdAnnotationPairDict, obsoletePortIdToAnnotationIdDict, commonAttributeTagAnnotationPairDict, obsoleteAttributeTagToAnnotationIdDict

    def parseDatatype(self, datatype:str) -> (str, str, DimensionalityParseObject):
        rejection = ""
        baseDatatype = datatype
        dimensionality = None
        match = _DatatypeBracketsRegex.match(datatype)
        if match:
            baseDatatype = match[1].strip()
            dimensionsText = match[2].strip()
            checkNothingLeft = True
            allowStar = True
            if self._parent.parent().moduleType() != "submodel":
                allowStar = False
            pos, dimensionality = self._parseEsl.parseDimensions(dimensionsText, 0, None, checkNothingLeft=checkNothingLeft, allowStar=allowStar)
            if dimensionality is not None:
                for parseMessage in dimensionality.messages:
                    dimMsg = parseMessage.message + " "
                    if dimMsg:
                        rejection += dimMsg
                whatsLeft = datatype[match.end(2) + 1:]
                if whatsLeft and not whatsLeft.isspace():
                    rejection += "unexpected characters (\"" + whatsLeft + "\") after array specification "
        return rejection, baseDatatype, dimensionality
