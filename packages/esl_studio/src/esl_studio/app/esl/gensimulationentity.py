#! /usr/bin/python

from collections import OrderedDict

from .. import utils as Utils
from ..application.port import PortConnectorSeparator
from ..application.attribute import Attribute
from .lexer import inclusionStartString, inclusionEndString
from .generate import eslDatatype
from .generate import nl
from .genport import GenPort

class GenSimulationEntity(object):
    def __init__(self, genDiagramInfo, objectId, appSimEntity):
        self._genDiagramInfo = genDiagramInfo
        self._objectId = objectId
        self._appSimEntity = appSimEntity
        self._prefix = None
        if appSimEntity.prefix():
            self._prefix = appSimEntity.prefix()
        self._entityDefnXmlElement = self.generate().entities().getEntityDefnXmlElement(self._appSimEntity.type())
        self._entityModelXmlElement = self._entityDefnXmlElement.getXmlElementByName("model")
        self._portsConnections = []
        self._ports = OrderedDict()
        self._insert_position = None
        # to order these for resolving port dimensions
        self._rank = 0
        self._upLinkedSimulationEntities = []

    def __str__(self):
        return "<Gen-"+self.identification()+">"

    def genDiagramInfo(self):
        return self._genDiagramInfo
    def objectId(self):
        return self._objectId
    def appSimEntity(self):
        return self._appSimEntity
    def isSubmodelCall(self):
        return self._appSimEntity.isSubmodelCall()
    def isSegmentCall(self):
        return self._appSimEntity.isSegmentCall()
    def isCall(self):
        return self._appSimEntity.isCall()
    def isInputArgument(self):
        return self._appSimEntity.isInputArgument()
    def isOutputArgument(self):
        return self._appSimEntity.isOutputArgument()
    def portsConnections(self):
        return self._portsConnections
    def ports(self):
        return self._ports
    def insert_position(self):
        return self._insert_position
    def rank(self):
        return self._rank
    def set_rank(self, rank):
        self._rank = rank
    def upLinkedSimulationEntities(self):
        return self._upLinkedSimulationEntities
    def addUpLinkedGenSimEntity(self, upLinkedGenSimEntity):
        if upLinkedGenSimEntity not in self._upLinkedSimulationEntities:
            self._upLinkedSimulationEntities.append(upLinkedGenSimEntity)

    def type(self):
        return self._appSimEntity.type()
    def identification(self):
        return self._appSimEntity.identification()
    def generate(self):
        return self._genDiagramInfo.generate()

    def makeEslName(self, tag):
        return self._appSimEntity.makeEslName(tag)

    def gather(self):
        portsInfoList = (self._genDiagramInfo.appDiagramInfo().canvas().
                                GetPortsInfo(self._objectId))
        self._portsConnections = (self._genDiagramInfo.appDiagramInfo().canvas().
                                 EstablishPortsConnections(self._objectId))

        for portInfo in portsInfoList:
            portId = portInfo[0]
            diagType = portInfo[1]
            diagDirection = portInfo[2]
            diagSign = portInfo[3]
            port = GenPort(self, portId, diagType, diagDirection, diagSign)
            self._ports[str(portId)] = port

    def gatherForPorts(self):
        inputSigns = None
        #inp = 0
        for genPort in list(self._ports.values()):
            portKind = genPort.kind()
            if portKind == 'ESL-value' and genPort.direction() == 'input':
                genPort.set_eslname(self.findConnectedPortEslname(genPort))
            elif portKind == 'natural':
                genPort.set_natural_in_eslname(self.findConnectedPortEslname(genPort))
            #elif genPort.direction() == 'output':
            #    genPort.eslName = self.makeEslName(genPort.tag())

    def findConnectedPortEslname(self, genPort):
        # find its corresponding output - in portConnections
        # find this entity-tag
        # - its corresponding list should contain 1 output port on another entity
        portRef = self.makeEslName(genPort.tag())
        result = inclusionStartString+'Input ' + portRef + ' is not attached to any outputs'+inclusionEndString
        portStr = str(self._objectId) + PortConnectorSeparator + str(genPort.portId())
        for item in self._portsConnections:
            if item[0] == portStr:
                connectedPorts = item[1]
                nOuts = 0
                for connections in connectedPorts:
                    connectionparts = connections.split(PortConnectorSeparator)
                    if len(connectionparts) == 2:
                        otherObjectId = connectionparts[0]
                        otherPortId = connectionparts[1]
                        if otherObjectId == self._objectId and otherPortId == str(genPort.portId()):
                            result = inclusionStartString+'Input ' + portRef + ' is connected to itself'+inclusionEndString
                            break
                        else:
                            otherGenSimEntity = self._genDiagramInfo.simulationEntities().get(otherObjectId) # we don't consider display definititions
                            if otherGenSimEntity:
                                otherGenPort = otherGenSimEntity.ports()[otherPortId]
                                if otherGenPort:
                                    portKind = otherGenPort.kind()
                                    if ((portKind == 'ESL-value' and otherGenPort.direction() == 'output') or
                                        portKind == 'natural'):
                                        nOuts += 1
                                        if nOuts > 1:
                                            result = inclusionStartString+'Input ' + portRef + ' has more than one output connection'+inclusionEndString
                                        else:
                                            result = otherGenPort.eslname()
        return result

    def generateAttributeEsl(self, coderegion, attribute):
        result = ""
        if coderegion == "declarations":
            datatype = attribute.datatype()
            if datatype.title() not in ['Enum', 'Boolean', 'String']:
                result += "-- Attribute "
                result += attribute.tag()
                descr = attribute.description()
                if descr:
                    result += " (" + descr + ")"
                result += " for " + self._appSimEntity.identification() + nl
                if attribute.constant() and attribute.constant() == "true":
                    result += "CONSTANT "
                if not datatype: datatype = "Real"
                result += eslDatatype(datatype)
                result += ": "
                if attribute.eslname():
                    result += attribute.eslname()
                else:
                    result += self.makeEslName(attribute.tag())
                if attribute.dimensions():
                    d = attribute.dimensions()
                    d = self.substitute(d)
                    result += "(" + d + ")"
                source = attribute.source()
                if not source: source = Attribute.SourceValue
                if source == Attribute.SourceValue:
                    eslValue = attribute.eslValue()
                    valueStr = eslValue.valueStr()
                    if not valueStr:
                        valueStr = eslValue.defaultValueStr()
                    if valueStr:
                        valueStrSubstituted = self.substitute(valueStr)
                        if valueStrSubstituted != valueStr:
                            eslValue = eslValue.detachedCopy(None)  # clone
                            eslValue.set_valueStr(valueStrSubstituted)
                        result += eslValue.getInitialisationValue()
                # else: # Not Value - No initialisation here (is assigned to source value [or default-value] in initial or dynamic region to instead (below))

            if result:
                result += ";" + nl

        elif coderegion == "initial" or coderegion == "dynamic":
            value = attribute.valueStr()
            if not value:
                value = attribute.defaultValueStr()
            if value:
                source = attribute.source()
                if not source:
                    source = Attribute.SourceValue
                if source != Attribute.SourceValue:
                    targetCoderegion = self.determineCodeRegionForAttributeAssignment(attribute, source, value)
                    if coderegion == targetCoderegion:
                        if attribute.eslname():
                            result += attribute.eslname()
                        else:
                            result += self.makeEslName(attribute.tag())
                        result += " := "
                        result += value
                        result += ";" + nl
        return result

    def generateAttributesEsl(self, coderegion):
        result = ""
        for attribute in self.appSimEntity().attributes().values():
            if attribute.is_special() != "true":
                result += self.generateAttributeEsl(coderegion, attribute)
        return result

    def determineCodeRegionForAttributeAssignment(self, appAttribute, source, value):
        if False:
            # One interpretation of "attribute" is they are for setting *initial* values for an entity.
            # In many (most) cases this is the case (subprogram calls, library submodels for constant input arguments).
            targetCoderegion = "initial"
        else:
            # An alternative (adopted) interpretation of "attribute" is they may allow the values to be dynamic for an entity.
            # The is just for restricted cases - previously when a module parameter or package variable has been defined with
            # 'kind' Variable (as opposed to 'Constant' or 'Parameter') - which has since been removed.
            # Now attribute assignments to a variable are treated always as constant-like irrespective of kind of variable are generated in the "initial" region.
            targetCoderegion = "dynamic"
            if self.isCall():   # As call attributes are CONSTANT arguments.
                targetCoderegion = "initial"
            else:
                if source == "Output":
                    targetCoderegion = "dynamic"
                elif source == "RESERVED": # Simulation parameter
                    if value == "T":
                        targetCoderegion = "dynamic"
                    else:
                        targetCoderegion = "initial"
                else:
                    ## Previously depended on kind of variable - commented out
                    ##variable = None
                    ##if source == 'Parameter': # The value is variable name
                    ##    variable = self._appSimEntity.parent().parent().blockNames().get(value)
                    ##elif source not in ["Value", "Parameter", "Output"]: # it is a used Package name (the value is variable name)
                    ##    package = self._appSimEntity.parent().parent().application().getPackageByName(source)
                    ##    if package:
                    ##        variable = package.blockNames().get(value)
                    ##if variable:
                    ##    if variable.constant() == "true" or  variable.parameter() == "true":
                    #        targetCoderegion = "initial"
                    targetCoderegion = "initial"
                    ## Now, for these variables, always "initial".
        return targetCoderegion

    def generateDefinitionModelTemplate(self, coderegion):
        result = ""
        generateXmlElement = self._entityModelXmlElement.getXmlElementByName("generate", False)
        if generateXmlElement:
            coderegionXmlElement = generateXmlElement.getXmlElementByName(coderegion, False)
            if coderegionXmlElement:
                content = coderegionXmlElement.getContent()
                content = content.strip()
                content = content.replace("\t", "")
                result += content
                result += nl
        return result

    def generateEsl(self, coderegion): # Gen-code for special entities may override this completely (or just generateAttributesEsl and/or generateDefinitionModelTemplate)
        """ coderegion : "include" "declarations" "initial" "dynamic" "step" "communication" + "terminal" "analysis" """
        result = ""
        if self._entityModelXmlElement:

            result += self.generateAttributesEsl(coderegion)

            result += self.generateDefinitionModelTemplate(coderegion)

            if result: # Always run through the template substitution (OK even if not a template).
                result = self.substitute(result)
        return result

    def generateEslPositioned(self, coderegion, position):  # override for simulation entities that support positioned code generation
        # coderegion : "declarations" "initial" "dynamic" "step" "communication" + "terminal" "analysis"
        # position: "beginning" "end"
        result = ""
        return result

    def substitute(self, eslStr):
        subst = ""
        value = ""
        if (eslStr.find("{O:") != -1):
            for port in list(self._ports.values()):
                if port.direction() == "output":
                    if port.kind() == 'ESL-value':
                        subst = "{O:" + port.tag() + "}"
                        value = port.eslname()
                        eslStr = eslStr.replace(subst, value)
                    elif port.kind() == 'natural':
                        subst = "{O:" + port.tag() + ".out}"
                        value = port.eslname()
                        eslStr = eslStr.replace(subst, value)
                        subst = "{O:" + port.tag() + ".in}"
                        value = port.natural_in_eslname()
                        eslStr = eslStr.replace(subst, value)

        if (eslStr.find("{I:") != -1):
            for port in list(self._ports.values()):
                if port.direction() == "input":
                    if port.kind() == 'ESL-value':
                        subst = "{I:" + port.tag() + "}"
                        value = port.eslname()
                        if port.sign() == "minus": value = "(-" + value + ")"
                        eslStr = eslStr.replace(subst, value)
                    elif port.kind() == 'natural':
                        subst = "{I:" + port.tag() + ".out}"
                        value = port.eslname()
                        eslStr = eslStr.replace(subst, value)
                        subst = "{I:" + port.tag() + ".in}"
                        value = port.natural_in_eslname()
                        eslStr = eslStr.replace(subst, value)
        if (eslStr.find("{A:") != -1):
            for attribute in list(self._appSimEntity.attributes().values()):
                subst = "{A:" + attribute.tag() + "}"
                if attribute.eslname():
                    value = attribute.eslname()
                else:
                    value = self.makeEslName(attribute.tag())
                eslStr = eslStr.replace(subst, value)
        if (eslStr.find("{A#") != -1):
            for attribute in list(self._appSimEntity.attributes().values()):
                subst = "{A#" + attribute.tag() + "}"
                value = attribute.valueStr()
                if not value:
                    value = attribute.defaultValueStr()
                eslStr = eslStr.replace(subst, value)
        if (eslStr.find("{O*") != -1):
            ostar1 = eslStr.find("{O*")
            ostar2 = eslStr.find("}", ostar1)
            replace = eslStr[ostar1:ostar2+1]
            extra = eslStr[ostar1+3:ostar2]
            value = ""
            for port in list(self._ports.values()):
                if port.direction() == "output":
                    if value: value += ", "
                    value += port.eslname()
            if value: value += extra
            eslStr = eslStr.replace(replace, value)
        IAstarActive = False
        posn = eslStr.find("{I*}")
        if (posn != -1):
            if eslStr[posn:].startswith("{I*}{A*}"):
                IAstarActive = True         # we have (I*}{A*} in the template
            value = ""
            for port in list(self._ports.values()):
                if port.direction() == "input":
                    if value: value += ", "
                    item = port.eslname()
                    if port.sign() == "minus": item = "(-" + item + ")"
                    value += item
            eslStr = eslStr.replace("{I*}", value)
            if IAstarActive and not value:
                IAstarActive = False        # no values for {I*} so deactivate
        if (eslStr.find("{A*}") != -1):
            value = ""
            for attribute in list(self._appSimEntity.attributes().values()):
                if attribute.is_special() != "true":
                    if value: value += ", "
                    item = attribute.eslname()
                    if not item:
                        item = self.makeEslName(attribute.tag())
                    value += item
            if value:
                posn = eslStr.find("{A*}")
                if IAstarActive:    # Join the values from I* and A* with a ,
                    value = ", " + value
            eslStr = eslStr.replace("{A*}", value)
        return eslStr

    def resetForResolveSimulationEntities(self):
        self._upLinkedSimulationEntities = []
        self._rank = 0

    def resolveSimulationEntityPorts(self):
        if self.generate().debugging:
            print(">GenSimEntity.resolveSimulationPorts "+str(self))
        for genPort in list(self._ports.values()):
            portKind = genPort.kind()
            if portKind == 'ESL-value' and genPort.direction() == 'output':
                if self.generate().debugging:
                    print("-GenSimEntity.resolveSimulationPorts portId=" + str(genPort.portId()))
                portResolveDimensionsData = genPort.appPort().resolvePortDimensions(
                    entityPortsConnectionsDict=self._genDiagramInfo.appEntityPortsConnectionsDict(),
                    portResolveDimensionsDict=self._genDiagramInfo.appPortResolveDimensionsDict())
                pass
        if self.generate().debugging:
            print("<GenSimEntity.resolveSimulationPorts "+str(self))
