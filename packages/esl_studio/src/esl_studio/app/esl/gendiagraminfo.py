#! /usr/bin/python

import os
from collections import OrderedDict

from .genorder import GenResolveSimulationEntitiesOrder
from .. import utils as Utils
from ..application.displaydefinition import DisplayDefinition
from ..application.port import PortConnectorSeparator, Port, getPortsConnections
from .lexer import inclusionStartString
from .generate import nl, indent, indentate
from .gensimulationentity import GenSimulationEntity
from .gentransferfunction import GenTransferFunction
from .gensubmodelcall import GenSubmodelCall
from .gensegmentcall import GenSegmentCall
from .genfunctioncall import GenFunctionCall
from .geninputargument import GenInputArgument
from .genoutputargument import GenOutputArgument
from .gencodeinsert import GenCodeInsert
from .genconstantinput import GenConstantInput

class GenDiagramInfo(object):
    def __init__(self, module, appDiagramInfo):
        self._module = module
        self._appDiagramInfo = appDiagramInfo
        self._genResolveSimulationEntitiesOrder = GenResolveSimulationEntitiesOrder(self)
        self._simulationEntities = OrderedDict()
        self._libraryList = []
        self._inputs = []
        self._outputs = []
        self._calledAppSubprograms = []
        self._preloadedSubprograms = []
        self._appEntityPortsConnectionsDict = {} # a dict of application simulation-entity containing the (full) EstablishPortsConnections data (list-tree of str) from the diagram for the entity (for resolving port dimensions)
        self._appPortResolveDimensionsDict = {} # a dict of application port containing a list [ resolvedState:str, resolvedDimensions:str, resolvedDimensionality:DimensionalityParseObject]
        self._toResolveSimulationEntities: list[GenSimulationEntity] = []
        #inputs & outputs for 'submodels' with those kinds of elements
          # consider adding an attribute in ise-entities for these argument entities
        #dict of entities paralleling appDiagramInfo.simulationEntities
        # -> genSimulationEntities
        # make use of canvas/diagram... to have in GenSimulationEntity
        # - list of GenPorts?, each list of connections i.e. other entity GenPorts
        # - ask canvas etc for this (given entityObjectId)
    def module(self):
        return self._module
    def appDiagramInfo(self):
        return self._appDiagramInfo
    def simulationEntities(self):
        return self._simulationEntities
    def inputs(self):
        return self._inputs
    def outputs(self):
        return self._outputs
    def libraryList(self):
        return self._libraryList
    def calledAppSubprograms(self):
        return self._calledAppSubprograms
    def preloadedSubprograms(self):
        return self._preloadedSubprograms
    def importedPackageNames(self):
        return self._appDiagramInfo.importedPackageNames()
    def appEntityPortsConnectionsDict(self):
        return self._appEntityPortsConnectionsDict
    def appPortResolveDimensionsDict(self):
        return self._appPortResolveDimensionsDict
    def toResolveSimulationEntities(self):
        return self._toResolveSimulationEntities

    def generate(self):
        return self._module.generate()

    def makeGenSimulationEntity(self, entityObjectId, appSimEntity):
        genSimEntity = None
        specialType = appSimEntity.specialType()
        if specialType == "Transfer Function":
            genSimEntity = GenTransferFunction(self, entityObjectId, appSimEntity)
        elif specialType == "Submodel Call":
            genSimEntity = GenSubmodelCall(self, entityObjectId, appSimEntity)
        elif specialType == "Segment Call":
            genSimEntity = GenSegmentCall(self, entityObjectId, appSimEntity)
        elif specialType == "Function Call":
            genSimEntity = GenFunctionCall(self, entityObjectId, appSimEntity)
        elif specialType == "Input Argument":
            genSimEntity = GenInputArgument(self, entityObjectId, appSimEntity)
        elif specialType == "Output Argument":
            genSimEntity = GenOutputArgument(self, entityObjectId, appSimEntity)
        elif specialType == "Code Insert":
            genSimEntity = GenCodeInsert(self, entityObjectId, appSimEntity)
        elif specialType == "Constant Input":
            genSimEntity = GenConstantInput(self, entityObjectId, appSimEntity)
        else:
            genSimEntity = GenSimulationEntity(self, entityObjectId, appSimEntity)
        return genSimEntity

    def gather(self):
        #setup data on what's not in the app equivalent
        self._calledAppSubprograms = []
        simulationEntities = self._appDiagramInfo.simulationEntities()
        for entityObjectId in simulationEntities:
            appSimEntity = simulationEntities[entityObjectId]
            genSimEntity = self.makeGenSimulationEntity(entityObjectId, appSimEntity)
            self._simulationEntities[entityObjectId] = genSimEntity
            genSimEntity.gather()
            appSubprogram = None
            if genSimEntity.isCall():
                appSubprogram = genSimEntity.appSimEntity().subprogram()
            if appSubprogram and appSubprogram not in self._calledAppSubprograms:
                self._calledAppSubprograms.append(appSubprogram)

    def gatherForPorts(self):
        for genSimEntity in list(self._simulationEntities.values()):
            genSimEntity.gatherForPorts()

    def gatherForResolvePortDimensions(self):
        if self.generate().debugging:
            print(">GenDiagramInfo.gatherForResolvePortDimensions " + str(self._module.appModule().eslname()))
        self._appEntityPortsConnectionsDict = {}
        self._appPortResolveDimensionsDict = {}
        self._toResolveSimulationEntities = []
        for genSimEntity in self._simulationEntities.values():
            self._appEntityPortsConnectionsDict[genSimEntity.appSimEntity()] = genSimEntity._portsConnections
            genSimEntity.resetForResolveSimulationEntities()
            # See if simulation entity has generic output ports
            for genPort in list(genSimEntity.ports().values()):
                portKind = genPort.kind()
                if portKind == 'ESL-value' and genPort.direction() == 'output':
                    appPort = genPort.appPort()
                    if appPort.isGeneric():
                        self.addToResolveSimulationEntities(genSimEntity)
                        break
            pass
        for genSimEntity in self._toResolveSimulationEntities.copy():
            for genPort in list(genSimEntity.ports().values()):
                portKind = genPort.kind()
                if portKind == 'ESL-value' and genPort.direction() == 'input':
                    appPort = genPort.appPort()
                    thisPortsConnections = getPortsConnections(genSimEntity._portsConnections, appPort.entityPortId())
                    for connectedPortId in thisPortsConnections:
                        upLinkedAppSimEntity, itsAppPort = Port.getEntityAndPort(self._appDiagramInfo, connectedPortId)
                        if upLinkedAppSimEntity:
                            upLinkedGenSimEntity = self._simulationEntities[upLinkedAppSimEntity.objectId()]
                            genSimEntity.addUpLinkedGenSimEntity(upLinkedGenSimEntity)
                            self.addToResolveSimulationEntities(genSimEntity)
        pass
        self.resolveSimulationEntitiesOrder()
        if self.generate().debugging:
            print("<GenDiagramInfo.gatherForResolvePortDimensions " + str(self._module.appModule().eslname()))

    def addToResolveSimulationEntities(self, genSimEntity):
        if genSimEntity not in self._toResolveSimulationEntities:
            self._toResolveSimulationEntities.append(genSimEntity)

    def resolveSimulationEntitiesOrder(self):   # called after gatherForResolvePortDimensions has done resetForResolveSimulationEntities
        if self.generate().debugging:
            print(">GenDiagramInfo.resolveSimulationEntitiesOrder " + str(self._module.appModule().eslname()))
        orderedSimEntities, errMsg = self._genResolveSimulationEntitiesOrder.establishSimulationEntitiesOrder()
        if errMsg:
            msg = "problem resolving generic ports in " + str(self._module.appModule().identification()) + ": " + errMsg + "\n"
            self.generate().control().appendMessage(msg)
        for genSimEntity in orderedSimEntities:
            genSimEntity.resolveSimulationEntityPorts()
        pass
        if self.generate().debugging:
            print("<GenDiagramInfo.resolveSimulationEntitiesOrder " + str(self._module.appModule().eslname()))

    def setupLibraryList(self):
        for genSimEntity in list(self._simulationEntities.values()):
            libstr = genSimEntity.generateEsl("include")
            if libstr:
                liblst = libstr.split(',')
                for lib in liblst:
                    lib = lib.strip()
                    lib = Utils.deEslLibFile(lib)
                    if not lib[0] == '"':
                        if lib.find(' ') != -1 or lib.find(os.sep) != -1:
                            lib = '"' + lib + '"'
                    if lib not in self._libraryList:
                        self._libraryList.append(lib)

    def setupArguments(self):
        for genSimEntity in list(self._simulationEntities.values()):
            entityObjectId = genSimEntity.objectId()
            if genSimEntity.isInputArgument():
                self._inputs.append(entityObjectId)
            if genSimEntity.isOutputArgument():
                self._outputs.append(entityObjectId)

    def setupCallSubprograms(self):
        for genSimEntity in list(self._simulationEntities.values()):
            if genSimEntity.isCall():
                isPreloaded = genSimEntity.setupCallSubprogram()
                if isPreloaded == True:
                    subprogram = genSimEntity.subprogram()
                    if subprogram not in self._preloadedSubprograms:
                        self._preloadedSubprograms.append(subprogram)

    def generateEslPositioned(self, positionalGenSimEntities, coderegion, extraForeEslStr=None, extraAfterEslStr=None):
        eslStr = ""
        position = "beginning"
        for positionalGenSimEntity in positionalGenSimEntities:
            eslStr += positionalGenSimEntity.generateEslPositioned(coderegion, position)
        if extraForeEslStr:
            eslStr += extraForeEslStr
        for genSimEntity in self._simulationEntities.values():
            eslStr += genSimEntity.generateEsl(coderegion)
        if extraAfterEslStr:
            eslStr += extraAfterEslStr
        position = "end"
        for positionalGenSimEntity in positionalGenSimEntities:
            eslStr += positionalGenSimEntity.generateEslPositioned(coderegion, position)
        return eslStr

    def generateCodeInsert(self, runDirect, simParStr=""):
        #// Create declaration
        eslStr = ''
        subprogram = self._appDiagramInfo.parent()
        eslname = subprogram.eslname()
        declarationsStr = ""
        initialStr = ""
        dynamicStr = ""
        stepStr = ""
        communicationStr = ""
        terminalStr = ""
        analysisStr = ""
        positionalGenSimEntities = []
        extraDeclarationsForeStr = ""
        if len(self._appDiagramInfo.parameters()) > 0:
            extraDeclarationsForeStr = "-- Parameters" + nl
            for appVariable in list(self._appDiagramInfo.parameters().values()):
                extraDeclarationsForeStr += self.generate().generateVariableDeclaration(appVariable) + nl
            extraDeclarationsForeStr += nl # blank after Parameters
        extraDeclarationsAfterStr = ""
        for genSimEntity in list(self._simulationEntities.values()):
            for genPort in list(genSimEntity.ports().values()):
                s = genPort.generateESLDeclaration()
                if s:
                    extraDeclarationsAfterStr += s
                    extraDeclarationsAfterStr += ";" + nl

        extraStepAfterStr = ""
        extraCommunicationAfterStr = ""
        for display in list(self._appDiagramInfo.displayDefinitions().values()):
            if runDirect or display.display == DisplayDefinition.Display_values[1] or display.display == DisplayDefinition.Display_values[2]:
                displayEsl = self.generateDisplayEsl(display)
                if display.update == "step":
                    extraStepAfterStr += displayEsl
                else:
                    extraCommunicationAfterStr += displayEsl

        for genSimEntity in self._simulationEntities.values():
            if genSimEntity.insert_position():
                positionalGenSimEntities.append(genSimEntity)

        declarationsStr += self.generateEslPositioned(positionalGenSimEntities, "declarations", extraDeclarationsForeStr, extraDeclarationsAfterStr)
        initialStr += self.generateEslPositioned(positionalGenSimEntities, "initial")
        dynamicStr += self.generateEslPositioned(positionalGenSimEntities, "dynamic")
        stepStr += self.generateEslPositioned(positionalGenSimEntities, "step", None, extraStepAfterStr)
        communicationStr += self.generateEslPositioned(positionalGenSimEntities, "communication", None, extraCommunicationAfterStr)
        if subprogram.moduleType() == "model" and subprogram.modelType() == "model":
            terminalStr += self.generateEslPositioned(positionalGenSimEntities, "terminal")
            analysisStr += self.generateEslPositioned(positionalGenSimEntities, "analysis")

        if len(self._libraryList) > 0:
            eslStr += nl + indent + "-- LIBRARY "
            i = 0
            for lib in self._libraryList:
                eslStr += lib
                i += 1
                if i < len(self._libraryList): eslStr += ", "
            eslStr += nl
        packages = self._appDiagramInfo.importedPackageNames()
        if len(packages) > 0:
            eslStr += nl + indent
            eslStr += "USE "
            i = 0
            for packName in packages:
                eslStr += packName
                i += 1
                if i < len(packages): eslStr += ", "
            eslStr += ";" + nl

        if declarationsStr:
            eslStr += nl + indentate(indent, declarationsStr)
        if initialStr or simParStr:
            eslStr += nl + "INITIAL" + nl
            fullInitialStr = ""
            if simParStr:
                fullInitialStr = "-- Simulation Parameters ("+str(simParStr.count(";"))+")\n" + simParStr
                if initialStr:
                    fullInitialStr += "--\n" # Comment (empty) after Simulation Parameters
            if initialStr:
                fullInitialStr += initialStr
            eslStr += indentate(indent, fullInitialStr)
        eslStr += nl + "DYNAMIC" + nl #// We always have a DYNAMIC statement
        if dynamicStr:
            eslStr += indentate(indent, dynamicStr)
        if stepStr:
            eslStr += nl + "STEP" + nl
            eslStr += indentate(indent, stepStr)
        if communicationStr:
            eslStr += nl + "COMMUNICATION" + nl
            eslStr += indentate(indent, communicationStr)
        if terminalStr:
            eslStr += nl + "TERMINAL" + nl
            eslStr += indentate(indent, terminalStr)
        if analysisStr:
            eslStr += nl + "ANALYSIS" + nl
            eslStr += indentate(indent, analysisStr)
        eslStr += nl + "END "
        eslStr += eslname
        eslStr += ";" + nl
        return eslStr

    def generateCodeInsertArguments(self):
        result = ''
        if len(self._inputs) > 0 or len(self._outputs) > 0:
            result += "("
            n = len(self._outputs)
            i = 0
            for objectId in self._outputs:
                genSimEntity = self._simulationEntities[objectId]
                if genSimEntity.isOutputArgument():
                    result += genSimEntity.generateOutputArgument(i)
                i += 1
                if i < n: result += '; '
            n = len(self._inputs)
            if n > 0: result += " := "
            # Non-constant inputs (ports)
            i = 0
            nrDone = 0
            for objectId in self._inputs:
                genSimEntity = self._simulationEntities[objectId]
                if genSimEntity.isInputArgument():
                    eslArgument = genSimEntity.generateInputArgument(i, constant=False)
                    if eslArgument:
                        result += eslArgument
                        nrDone += 1
                    if nrDone < n and eslArgument:
                        result += '; '
                i += 1
            # Constant inputs (attributes)
            i = 0
            for objectId in self._inputs:
                genSimEntity = self._simulationEntities[objectId]
                if genSimEntity.isInputArgument():
                    eslArgument = genSimEntity.generateInputArgument(i, constant=True)
                    if eslArgument:
                        result += eslArgument
                        nrDone += 1
                    if nrDone < n and eslArgument:
                        result += '; '
                i += 1
            result += ')'
        return result

    def generateDisplayEsl(self, display):
        result = ""
        variableRefs = self.getDisplayVariableRefs(display, noModules=True)
        nrVars = len(variableRefs)
        if nrVars:
            if display.type() == "plot":
                result = "PLOT "
                if display.title:
                    result += "\"ESL: " + display.title + "\", "
                else:
                    result += "\"ESL: " + display.name + "\", "
            elif display.type() == "table":
                result = "TABULATE "
                filename = display.tableSpec.outputFile
                if not filename:
                    filename = display.name
                filename = Utils.sanitiseFilename(filename, noSpaces=True)
                filename, extn = os.path.splitext(filename)
                filename += "_ESL"
                if extn:
                    filename += extn
                result += "\"" + filename + "\", "
            elif display.type() == "prepare":
                result = "PREPARE "
                filename = display.prepareSpec.prepareFile
                if not filename:
                    filename = display.name
                filename = Utils.sanitiseFilename(filename, noSpaces=True)
                filename, extn = os.path.splitext(filename)
                filename += "_ESL"
                if extn:
                    filename += extn
                result += "\"" + filename + "\", "
                if display.title:
                    result += "\"" + display.title + "\", "
                if display.subtitle:
                    result += "\"" + display.subtitle + "\", "
            result += "T, "
            for i in range(nrVars):
                if i == 1 and display.type() == "plot":
                    result += "[ "
                result += variableRefs[i]
                if i == nrVars - 1:
                    if i >= 1 and display.type() == "plot":
                        result += " ]"
                else:
                    result += ", "
            if display.type() == "plot":
                # X-Axis
                result += ", "
                min = str(display.plotSpec.xAxis.min)
                if display.plotSpec.xAxis.autoScale:
                    max = min
                else:
                    max = str(display.plotSpec.xAxis.max)
                result += min + ", " + max
                # Y-Axis
                result += ", "
                min = str(display.plotSpec.yAxis.min)
                if display.plotSpec.yAxis.autoScale:
                    max = min
                else:
                    max = str(display.plotSpec.yAxis.max)
                result += min + ", " + max
            result += ";\n"
        return result

    def getDisplayVariableRefs(self, display, noModules=False):
        variableRefs = []
        doneVariableRefs = []
        skipVariableRefs = ""
        appDiagramInfo = self.appDiagramInfo()
        portsConnections = appDiagramInfo.canvas().EstablishPortsConnections(display.objectId())
        for portConnection in portsConnections:
            for connection in portConnection[1]:
                entityPort = connection.split(PortConnectorSeparator)
                entityId = entityPort[0]
                portId = entityPort[1]
                genEntity = self.simulationEntities().get(entityId)
                if genEntity:
                    genPort = genEntity.ports().get(portId)
                    eslname = genPort.eslname()
                    if not eslname.startswith(inclusionStartString):
                        variableRef = ""
                        if not noModules:
                            moduleName = appDiagramInfo.parent().eslname()
                            variableRef = "("+moduleName+") "
                        variableRef += eslname
                        variableRef = variableRef.upper()
                        if variableRef not in doneVariableRefs:
                            portResolveDimensionsData = genPort.appPort().resolvePortDimensions(
                                entityPortsConnectionsDict=self._appEntityPortsConnectionsDict,
                                portResolveDimensionsDict=self._appPortResolveDimensionsDict)
                            dimensions = portResolveDimensionsData.resolvedDimensions
                            rejectMsg = portResolveDimensionsData.resolvedRejectMsg
                            if rejectMsg or Port.isGenericDimensions(dimensions):
                                if skipVariableRefs != "": skipVariableRefs += " "
                                skipVariableRefs += variableRef
                            else:
                                if dimensions:
                                    refsList = genPort.appPort().generateArrayElementReferences(dimensions)
                                    for ref in refsList:
                                        variableRefs.append(variableRef+"("+ref+")")
                                else:
                                    variableRefs.append(variableRef)
                            doneVariableRefs.append(variableRef)
            if skipVariableRefs:
                display_identification = display.type().title() + ' (' + str(display.objectId()) + ')'
                msg = "skipped unresolved generic ports for " + skipVariableRefs + " in display " + display_identification + "\n"
                self.generate().control().appendMessage(msg)
        return variableRefs
