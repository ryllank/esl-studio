#! /usr/bin/python

from collections import OrderedDict
import copy

from .. import utils as Utils

from . import diagramactions as dgAction
from .callablesubprogram import CallableSubprogram
from .simulationentity import SimulationEntity

class CallEntity(SimulationEntity):

    def __init__(self, parent, type="", objectId=""):
        self._show_subprogram = "false"
        self._subprogram = None
        self._subprogramName = "" # just used during loading
        # Note: Does not make use of defined attributes.
        SimulationEntity.__init__(self, parent, type, objectId)

    def show_subprogram(self): return self._show_subprogram
    def set_show_subprogram(self, value): self._show_subprogram = value
    def subprogram(self): return self._subprogram
    def subprogramName(self): return self._subprogramName
    def set_subprogram(self, subprogram):
        self._subprogram = subprogram
        self._subprogramName = ""
    def callType(self): # 'submodel' or 'segment' or 'function'
        callType = None
        if self._subprogram:
            callType = self._subprogram.callableType()
        return callType

    def load(self, entityDescrXmlElement, suppressAddName=False):
        super(CallEntity, self).load(entityDescrXmlElement, suppressAddName)
        val = entityDescrXmlElement.getAttribute("show-subprogram")
        if val is None and self._application.compatibility() == 1:
            val = entityDescrXmlElement.getAttribute("show-submodel")
        if val is not None:
            self._show_subprogram = val

    def specialSaveXmlAttributes(self, indent=None, level=0, saveDefaults=False): # Has no attributes specifically for this class.
        xmlAttributeText = ""
        if self._show_subprogram == "true":
            xmlAttributeText += ' show-subprogram="true"'
        elif saveDefaults:
            xmlAttributeText += ' show-subprogram="false"'
        return xmlAttributeText

    #def specialSaveXmlContents(self, indent=None, level=0, saveDefaults=False): # Has no contents.

    def initPortsNAttributes(self, entities):
        subprogram = self.getSubprogram()
        self.linkSubprogramCallWithSubprogram(subprogram)
        if not self._subprogram:
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
        else:
            self._ports = self._subprogram.getPorts()
            for port in list(self._ports.values()): port.set_parent(self)
            self._attributes = self._subprogram.getAttributes()
            for attribute in list(self._attributes.values()): attribute.set_parent(self)

            # Get preloaded subprogram calls to show ports
            isPreloaded = self._subprogram.application() is None
            if isPreloaded:
                ports = self._subprogram.getPorts()
                portsActionStr = dgAction.makeSubprogramPortsActionStr(ports)
                updateActionStr = dgAction.makeUpdateSubprogramCallActionStr(self, portsActionStr, annotationsChangeInfo=None)
                dgAction.sendDiagramUpdate(self._parent, updateActionStr, applicationDataType="", applicationDataContents="", secondary=False, raiseEvent=True) # or should that be raiseEvent=False

    def getOrderedPorts(self, ports:OrderedDict) -> (list, list):
        portsInputs = []
        portsOthers = []
        for port in ports.values():
            if port.direction() == "input":
                portsInputs.append(port)
            else:
                portsOthers.append(port)
        return portsInputs, portsOthers

    def setupSubprogramCallPortsNAtts(self, matchPortsById=False):
        # Preset obsolete port annotation info for all prior ports
        commonPortIdAnnotationPairDict = {}
        obsoletePortIdToAnnotationIdDict = {}
        priorPorts = OrderedDict(self._ports)
        priorPortsInputs, priorPortsOthers = self.getOrderedPorts(priorPorts)
        inputIx = 0
        otherIx = 0
        for priorPort in priorPortsInputs:
            inputIx += 1
            portAnnotationId = "port-input-" + str(inputIx)
            obsoletePortIdToAnnotationIdDict[priorPort.id()] = portAnnotationId
        for priorPort in priorPortsOthers:
            otherIx += 1
            portAnnotationId = "port-" + str(otherIx)
            obsoletePortIdToAnnotationIdDict[priorPort.id()] = portAnnotationId
        # Preset obsolete attribute annotation info for all prior attributes
        priorAttributes = OrderedDict(self._attributes)
        commonAttributeTagAnnotationPairDict = {}
        obsoleteAttributeTagToAnnotationIdDict = {}
        for priorAttribute in list(priorAttributes.values()):
            obsoleteAttributeTagToAnnotationIdDict[priorAttribute.tag()] = "attribute-" + priorAttribute.tag()
        if self._subprogram:
            # Look for port's matching prior port - by index for inputs and (separately) index for others (outputs)
            currentPorts = self._subprogram.getPorts()
            for port in list(currentPorts.values()): port.set_parent(self)
            inputIx = 0
            otherIx = 0
            for port in list(currentPorts.values()):
                priorPort = None
                if matchPortsById:
                    priorPort = self._ports.get(port.id())
                else:
                    portAnnotationId = "port-"
                    if port.direction() == "input":
                        if inputIx < len(priorPortsInputs):
                            priorPort = priorPortsInputs[inputIx]
                        inputIx += 1
                        portAnnotationId += "input-" + str(inputIx)
                    else:
                        if otherIx < len(priorPortsOthers):
                            priorPort = priorPortsOthers[otherIx]
                        otherIx += 1
                        portAnnotationId += str(otherIx)
                if priorPort:
                    if (not priorPort.datatype() or priorPort.datatype() == port.datatype()) and priorPort.direction() == port.direction():
                        priorPortAnnotationId = obsoletePortIdToAnnotationIdDict[priorPort.id()]
                        commonPortIdAnnotationPairDict[port.id()] = (portAnnotationId, priorPortAnnotationId)
                        del obsoletePortIdToAnnotationIdDict[priorPort.id()]    # prior port is replaced by this port - so remove from obsolete port annotation info
                        subprogramDescription = port.description()
                        port.copyAssignables(priorPort)
                        if port.description() == subprogramDescription: # Do not copy subprogram port description to subprogram call port
                            port.set_description("")
            self._ports = currentPorts

            # Look for attribute's matching prior attribute
            currentAttributes = self._subprogram.getAttributes()
            for attribute in list(currentAttributes.values()): attribute.set_parent(self)
            for attribute in list(currentAttributes.values()):
                attributeTag = attribute.tag()
                attributeAnnotationTag = "attribute-" + attributeTag
                priorAttribute = priorAttributes.get(attributeTag)
                if not priorAttribute:
                    argument = attribute.argument() # For attribute derived from an input argument - match if had changed the Arg Name
                    if argument:
                        lastArgName = argument.getLastArgName()
                        if lastArgName:
                            priorAttribute = Utils.getCaseInsensitive(priorAttributes, lastArgName)
                        if not priorAttribute and self._application.compatibility() == 1: # Might be using old-style default tags (A1 A2 etc).
                            argName = argument.argName()
                            if not argName:
                                ix = list(currentAttributes.values()).index(attribute)
                                if ix >= 0:
                                    oldStyleDefaultAttributeTag = "A" + str(ix + 1)
                                    priorAttribute = priorAttributes.get(oldStyleDefaultAttributeTag) # case-sensitive
                if not priorAttribute: # Look for match by tag - case insensitive
                    priorAttribute = Utils.getCaseInsensitive(priorAttributes, attributeTag)
                if priorAttribute:
                    if not priorAttribute.datatype() or attribute.datatype() == priorAttribute.datatype():
                        priorAttributeAnnotationId = obsoleteAttributeTagToAnnotationIdDict[priorAttribute.tag()]
                        commonAttributeTagAnnotationPairDict[attribute.tag()] = (attributeAnnotationTag, priorAttributeAnnotationId)
                        del obsoleteAttributeTagToAnnotationIdDict[priorAttribute.tag()]    # prior attribute is replaced by this attribute - so remove from obsolete attribute annotation info
                        attribute.copyAssignables(priorAttribute)
            self._attributes = currentAttributes
        else:
            self._ports = OrderedDict()
            self._attributes = OrderedDict()
        return commonPortIdAnnotationPairDict, obsoletePortIdToAnnotationIdDict, commonAttributeTagAnnotationPairDict, obsoleteAttributeTagToAnnotationIdDict

    def getSubprogram(self):
        subprogram = None
        if self._subprogram:
            subprogram = self._subprogram
        elif self.isSubmodelCall():
            if self._subprogramName:
                subprogram = self._application.getSubmodelByName(self._subprogramName)
                if not subprogram and self._application.compatibility() == 1:
                    # An old style "submodel call" may in fact be a "segment call"
                    subprogram = self._application.getSegmentByName(self._subprogramName)
                    if subprogram:
                        segmentCall = self._application.makeSimulationEntity(self._parent, "Segment Call", self._objectId)
                        segmentCall.copyFrom(self, self._parent)
                        self.unlinkSubprogramCallWithSubprogram()
                        segmentCall.linkSubprogramCallWithSubprogram(subprogram)
                        segmentCall.setupSubprogramCallPortsNAtts(matchPortsById=True)
                        objXmlStr = self._parent.canvas().SaveObjectById(self.objectId())
                        updateXmlStr = objXmlStr.replace('type="Submodel Call"', 'type="Segment Call"')
                        updateXmlStr = updateXmlStr.replace('<annotation id="submodel"', '<annotation id="subprogram"')
                        self._parent.canvas().Action(
                            '<action name="Update"><application-data raise-event="false"/><objects>' + updateXmlStr + '</objects></action>')
                        self._parent.simulationEntities()[segmentCall._objectId] = segmentCall # replace the submodel with the segment in the diagram info
                        msg = "Converting old-style Submodel Call ("+str(self.objectId())+") to Segment Call (check connections)\n"
                        self._application.frame().control().appendMessage(msg)
                        subprogram = None
        elif self.isSegmentCall():
            if self._subprogramName:
                subprogram = self._application.getSegmentByName(self._subprogramName)
        elif self.isFunctionCall():
            if self._subprogramName:
                subprogram = self._application.getFunctionByName(self._subprogramName)
        return subprogram

    def getSubprogramName(self):
        result = ''
        if self._subprogram:
            result = self._subprogram.eslname()
        elif self._subprogramName:
            result = self._subprogramName
        return result

    def unlinkSubprogramCallWithSubprogram(self):
        currentSubprogram = self.subprogram()
        if currentSubprogram is not None:
            currentSubprogram.subprogramCalls().remove(self)

    def linkSubprogramCallWithSubprogram(self, subprogram):
        self.unlinkSubprogramCallWithSubprogram()
        if subprogram is not None:
            if subprogram.valid():
                subprogram.subprogramCalls().append(self)
            else:
                subprogram = None
        self.set_subprogram(subprogram)

    def subprogramRename(self, module, oldsubprogramname, newsubprogramname):
        if self._subprogram == module:
            if self._show_subprogram == "true":
                annotationId = "subprogram"
                annotationTxt = newsubprogramname
                annotationVisible = self._show_subprogram
                dgAction.sendAnnotationUpdate(self, annotationId, annotationTxt, annotationVisible)

    def copyFrom(self, anotherCallEntity, parent):
        self._show_subprogram = anotherCallEntity._show_subprogram
        self._subprogram = anotherCallEntity._subprogram
        self._subprogramName = anotherCallEntity._subprogramName
        super(CallEntity, self).copyFrom(anotherCallEntity, parent)

    def doSubprogramCallSubprogramPropertyChange(self, newSubprogramName, suppress_action=False):
        newSubprogram = None
        if newSubprogramName:
            newSubprogram = self._application.blockNames().get(newSubprogramName)
        oldSubprogram = self.subprogram()
        oldSubprogramName = ""
        if oldSubprogram:
            oldSubprogramName = oldSubprogram.eslname()
        diagramInfo = self._parent
        canvas = diagramInfo.canvas()
        if oldSubprogram != newSubprogram:
            undoChangeApplicationData = self._application.setupUndoChangeApplicationData(canvas, [self])
            self.linkSubprogramCallWithSubprogram(newSubprogram)
            annotationsChangeInfo = self.setupSubprogramCallPortsNAtts(matchPortsById=False)
            if not suppress_action:
                ports = None
                if newSubprogram is not None and isinstance(newSubprogram, CallableSubprogram):
                    ports = newSubprogram.getPorts(allowBlankTag=True)
                portsActionStr = dgAction.makeSubprogramPortsActionStr(ports)
                updateActionStr = dgAction.makeUpdateSubprogramCallActionStr(self, portsActionStr, annotationsChangeInfo=annotationsChangeInfo)
                applicationDataContents = "<undo-updated>" + undoChangeApplicationData.xml() + "</undo-updated>"
                dgAction.sendDiagramUpdate(diagramInfo, updateActionStr, applicationDataType="", applicationDataContents=applicationDataContents, secondary=True, raiseEvent=True) # or should that be raiseEvent=False
                canvas.Refresh()

    # def updateEntity(self, updateXmlElement): # No property update (at this level)

    # def validateEntityPropertyChange(self, propertyTag, newValue, val_type, val_item): # No property validation (at this level)

    # def updateEntityProperty(self, propertyTag, newValue, suppress_action=False): # No property update (at this level)

    # def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, tempNewAttribute, val_type, val_item, val_oldValue, val_newValue): # No attribute property validation (at this level)

    # def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False): # No attribute property update (at this level)
