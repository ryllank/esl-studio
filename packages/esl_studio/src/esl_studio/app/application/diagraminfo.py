#! /usr/bin/python

from collections import OrderedDict

from esl_diagram.canvas.diagram import sortedValues

from .. import utils as Utils
from . import diagramactions as dgAction
from .simulationentity import SimulationEntity
from .port import Port
from .displaydefinition import DisplayDefinition
from .infoblock import InfoBlock
from .variable import Variable

class DiagramInfo(object):
    def __init__(self, parent):
        self._parent = parent
        self._importedPackageNames = []
        self._canvas = None
        self._simulationEntities = OrderedDict() # keyed by objectId - for their attributes
        self._displayDefinitions = OrderedDict() # keyed by objectId
        self._infoBlocks = OrderedDict() # keyed by objectId
        self._application = self._parent.application() # for convenience
        self._control = self._application.frame().control() # for convenience
        self._oldToNewObjectIds = {}

    def parent(self): return self._parent
    def importedPackageNames(self): return self._importedPackageNames
    def parameters(self):
        return self._parent.variables()
    def canvas(self): return self._canvas
    def simulationEntities(self): return self._simulationEntities
    def displayDefinitions(self): return self._displayDefinitions
    def oldToNewObjectIds(self): return self._oldToNewObjectIds

    def set_canvas(self, canvas):
        self._canvas = canvas

    def set_importedPackageNames(self, packageNames):
        self._importedPackageNames = packageNames

    def load(self, subprogramXmlElement, raiseEvent=False, selectObjects=False, pasting=False):
        objectIds = []
        xmlElement = subprogramXmlElement.getXmlElementByName("packages", False)
        if xmlElement:
            packageNames = xmlElement.getContent()
            self._importedPackageNames = packageNames.split()
        xmlElement = subprogramXmlElement.getXmlElementByName("parameters", False)
        if xmlElement:
            variableXmlList = xmlElement.getXmlElementListByName("variable", False)
            for variableXmlElement in variableXmlList:
                var = Variable(self._parent)
                var.load(variableXmlElement)
                if var.eslname():
                    self._parent.addVariable(var)
        objectsXmlElement = subprogramXmlElement.getXmlElementByName("diagram", False)
        if not objectsXmlElement: # alternatively look for objects (as for clipboard)
            objectsXmlElement = subprogramXmlElement.getXmlElementByName("objects", False)
        self._oldToNewObjectIds = {}
        if objectsXmlElement:
            self._oldToNewObjectIds = self._canvas.LoadObjectsFromXml(subprogramXmlElement, raiseEvent=raiseEvent, selectObjects=selectObjects, pasting=pasting)
        xmlElement = subprogramXmlElement.getXmlElementByName("simulation-entities", False)
        if xmlElement:
            entityXmlList = xmlElement.getXmlElementListByName("entity", False)
            for entityXmlElement in entityXmlList:
                type = entityXmlElement.getAttribute('type')
                entity = self._application.makeSimulationEntity(self, type)
                if entity.type() == type: # has a valid type
                    valid = self.checkValidToLoad(entity)
                    if valid:
                        entity.load(entityXmlElement) # will use the oldid
                        oldId = entity.objectId()
                        diagramEntityXml = None
                        if oldId:
                            if self._application.compatibility() == 1: # Fix for port signs not being previously saved.
                                if objectsXmlElement:
                                    diagramEntityXml = objectsXmlElement.findXmlElementWithAttribute("entity", "id", oldId)
                                if diagramEntityXml:
                                    entity.updateEntityFromDiagramChange(diagramEntityXml)
                            newId = self._oldToNewObjectIds.get(oldId)
                            if newId:
                                entity._objectId = newId # like friend in C++
                                self._simulationEntities[entity._objectId] = entity
                            else:
                                if not pasting:
                                    self._control.appendMessage(
                                        'Simulation element for object '+str(oldId)+' not found in diagram\n')
            for entity in list(self._simulationEntities.values()):
                if not entity.isCall() or not (entity.subprogram() is None and entity.subprogramName()): # links to variables will be done after subprogram assigned
                    for attribute in list(entity.attributes().values()):
                        variableOrPort = attribute.getVariableFromSource()
                        attribute.linkAttributeWithVariableOrPort(variableOrPort)

        xmlElement = subprogramXmlElement.getXmlElementByName("display-definitions", False)
        if xmlElement:
            displayXmlList = xmlElement.getXmlElementListByName("display", False)
            for displayXmlElement in displayXmlList:
                type = displayXmlElement.getAttribute('type')
                display = DisplayDefinition(self, type)
                if display.type() == type: # has a valid type
                    display.load(displayXmlElement) # will use the oldid
                    oldId = display.objectId()
                    if oldId:
                        newId = self._oldToNewObjectIds.get(oldId)
                        if newId:
                            display._objectId = newId # like friend in C++
                            self._displayDefinitions[display._objectId] = display
                        else:
                            self._control.appendMessage(
                                'Display definition element for object '+str(oldId)+' not found in diagram\n')

        xmlElement = subprogramXmlElement.getXmlElementByName("info-blocks", False)
        if xmlElement:
            infoXmlList = xmlElement.getXmlElementListByName("info", False)
            for infoXmlElement in infoXmlList:
                type = infoXmlElement.getAttribute('type')
                info = InfoBlock(self, type)
                if info.type() == type: # has a valid type
                    info.load(infoXmlElement) # will use the oldid
                    oldId = info.objectId()
                    if oldId:
                        newId = self._oldToNewObjectIds.get(oldId)
                        if newId:
                            info._objectId = newId # like friend in C++
                            self._infoBlocks[info._objectId] = info
                            if info.type() == "Module Annotation":
                                self._parent.moduleAnnotationInserted(info)
                            elif  info.type() == "Program Annotation":
                                self._parent.programAnnotationInserted(info)
                        else:
                            self._control.appendMessage(
                                'Info block element for object '+str(oldId)+' not found in diagram\n')

        return list(self._oldToNewObjectIds.values())

    def save(self, indent=None, level=0, saveDefaults=False):
        nl, ind, ind2 = Utils.indentation(indent, level)
        result = ''
        if len(self._importedPackageNames) > 0 or saveDefaults:
            result += ind + '<packages>'
            for packagename in self._importedPackageNames:
                result += str(packagename)
                result += ' '
            result = result.rstrip()
            result += '</packages>' + nl
        if self._canvas:
            result += self._canvas.SaveObjects(indent, level, saveDefaults, includeVersion=False)
        if len(self._simulationEntities) > 0 or saveDefaults:
            result += ind + '<simulation-entities>' + nl
            for entity in sortedValues(self._simulationEntities):
                result += entity.save(indent, level + 1, saveDefaults)
            result += ind + '</simulation-entities>' + nl
        if len(self._parent.variables()) > 0 or saveDefaults:
            result += ind + '<parameters>' + nl
            for variable in sortedValues(self._parent.variables()):
                result += variable.save(indent, level + 1, saveDefaults)
            result += ind + '</parameters>' + nl
        if len(self._displayDefinitions) > 0 or saveDefaults:
            result += ind + '<display-definitions>' + nl
            for display in sortedValues(self._displayDefinitions):
                result += display.save(indent, level + 1, saveDefaults)
            result += ind + '</display-definitions>' + nl
        if len(self._infoBlocks) > 0 or saveDefaults:
            result += ind + '<info-blocks>' + nl
            for info in sortedValues(self._infoBlocks):
                result += info.save(indent, level + 1, saveDefaults)
            result += ind + '</info-blocks>' + nl
        return result

    def setupSubprogramCalls(self):
        for simentity in list(self._simulationEntities.values()):
            if simentity.isCall():
                subprogramTypeTxt = "Submodel"
                if simentity.isSegmentCall():
                    subprogramTypeTxt = "Segment"
                elif simentity.isFunctionCall():
                    subprogramTypeTxt = "Function"
                subprogram = simentity.getSubprogram()
                if subprogram:
                    if subprogram != self._parent and subprogram.valid():
                        if self._parent.blockNames().isin(subprogram.eslname()):
                            raise Exception(subprogramTypeTxt + ' name "' + subprogram.eslname() + '" in use in the module')
                        else:
                            simentity.linkSubprogramCallWithSubprogram(subprogram)
                            simentity.setupSubprogramCallPortsNAtts(matchPortsById=True)
                else: # should we reshape it
                    if simentity.subprogramName():
                        simentity.set_subprogram(None)
                        annotationsChangeInfo = simentity.setupSubprogramCallPortsNAtts(matchPortsById=True)
                        portsActionStr = dgAction.makeSubprogramPortsActionStr(None)
                        updateActionStr = dgAction.makeUpdateSubprogramCallActionStr(simentity, portsActionStr, annotationsChangeInfo=annotationsChangeInfo)
                        dgAction.sendDiagramUpdate(self, updateActionStr, applicationDataType="", applicationDataContents="", secondary=False, raiseEvent=False) # raiseEvent=False so wont register as an alteration
                        self.canvas().Refresh()

    def checkNameIsCalledSubprogramName(self, eslname):
        result = False
        for simentity in list(self._simulationEntities.values()):
            if simentity.isCall():
                subprogram = simentity.getSubprogram()
                if subprogram:
                    if eslname.upper() == subprogram.eslname().upper():
                        result = True
                        break
        return result

    def insertEntity(self, entity):
        if isinstance(entity, SimulationEntity):
            if entity.isCall():
                subprogram = entity.getSubprogram()
                if subprogram and subprogram.application() is None: # preloaded
                    if len(subprogram.subprogramCalls()) == 1:      #### TODO why is this 1 - not using hasSubprogramCalls()
                        self._application.blockNames().add(subprogram.eslname(), subprogram)
            self._simulationEntities[entity.objectId()] = entity
            self._application.frame().viewManager().applicationView().addInEntity(self.parent(), entity)
        elif isinstance(entity, DisplayDefinition):
            self._displayDefinitions[entity.objectId()] = entity
        elif isinstance(entity, InfoBlock):
            self._infoBlocks[entity.objectId()] = entity
            if entity.type() == "Module Annotation":
                self._parent.moduleAnnotationInserted(entity)
            elif entity.type() == "Program Annotation":
                self._parent.programAnnotationInserted(entity)

    def checkValidToLoad(self, entity):
        valid = True
        msg = ''
        if entity.isCall():
            valid, msg = entity.checkValidToLoad()
        if msg:
            self._control.appendMessage(msg)
        return valid

    def checkValidToInsert(self, entityElement):
        valid = True
        msg = ''
        type = entityElement.getAttribute('type')
        entityDefnXmlElement = self._control.entities().getEntityDefnXmlElement(type)
        if not entityDefnXmlElement:
            msg = "Simulation entity \"" + type + "\" not defined (library or profile file may be missing)\n"
            valid = False
        else:
            specialType = entityDefnXmlElement.getAttribute("special-type")
            if specialType == "Submodel Call" or specialType == "Segment Call" or specialType == "Function Call":
                subprogramTxt = "submodel"
                if specialType == "Segment Call":
                    subprogramTxt = "segment"
                elif specialType == "Function Call":
                    subprogramTxt = "function"
                subprogramName = entityElement.getAttribute(subprogramTxt)
                if subprogramName:
                    if specialType == "Submodel Call":
                        subprogram = self._application.getSubmodelByName(subprogramName)
                    elif specialType == "Segment Call":
                        subprogram = self._application.getSegmentByName(subprogramName)
                    elif specialType == "Function Call":
                        subprogram = self._application.getFunctionByName(subprogramName)
                    if not subprogram:
                        subprogram = self._control.entities().getPreloadedSubprogram(subprogramName)
                    if subprogram:
                        isPreloaded = subprogram.application() is None
                        if not subprogram.valid():
                            msg = 'Cannot create '+subprogramTxt+' call as '
                            if isPreloaded: msg += 'preloaded '
                            msg += subprogramTxt+' is not valid\n'
                            valid = False

                        if isPreloaded and len(subprogram.subprogramCalls()) == 1:      #### TODO why is this 1 - not using hasSubprogramCalls()
                            if self._application.blockNames().isin(subprogram.eslname()):
                                msg = 'Cannot create '+subprogramTxt+' call for preloaded '+subprogramTxt+' as '+subprogramTxt+' name "'+\
                                    subprogram.eslname()+'" is already being used\n'
                                valid = False
                    else:
                        msg = "Cannot create "+subprogramTxt+" call as no "+subprogramTxt+" named \"" + subprogramName + "\"\n"
                        valid = False
            elif specialType == "Input Argument" or specialType == "Output Argument":
                argName = ""
                argNameAttributeElement = entityElement.findXmlElementWithAttribute("attribute", "tag", "ARG")
                if argNameAttributeElement:
                    argName = argNameAttributeElement.getAttribute("value")
                if argName:
                    if self._parent.blockNames().isin(argName):
                        msg = "Cannot create "+type+" with Arg Name \""+argName+"\" as the name is already in use in the module\n"
                        valid = False
        if msg:
            self._control.appendMessage(msg)
        return valid

    def checkValidNewLink(self, linkElement):
        valid = True
        msg = ''
        linkType = linkElement.getAttribute("type")
        if linkType != "Instrumentation":               # we dont validate instrumentation lines (for displays)
            linkId = linkElement.getAttribute("id")
            linkConnections = self._canvas.EstablishLinksConnections(linkId)
            affectedSimulationEntities = []
            joinedEntityPorts = []
            for item in linkConnections[0] + linkConnections[1]:
                itemSplit = item.split("-")
                if len(itemSplit) == 2:
                    simulationEntity = self._simulationEntities.get(itemSplit[0])
                    if simulationEntity:
                        joinedEntityPorts.append(simulationEntity.ports().get(itemSplit[1]))
                        if simulationEntity not in affectedSimulationEntities:
                            affectedSimulationEntities.append(simulationEntity)
            #print("***DiagramInfo.checkValidNewLink link="+linkElement.getAttribute("id")+" type="+linkElement.getAttribute("type") +
            #      "\n link connections="+str(linkConnections) +
            #      "\n affectedSimulationEntities="+" ".join(list(map(lambda it: str(it), affectedSimulationEntities))))
            valid, msg = Port.validateDimensionsForJoinedPorts(joinedEntityPorts)
            if valid:
                entityPortsConnectionsDict = {}
                portResolveDimensionsDict = {}
                for simulationEntity in affectedSimulationEntities:
                    thisValid, thisMsg = simulationEntity.validateEntityLinks(entityPortsConnectionsDict, portResolveDimensionsDict)
                    if not thisValid:
                        valid = False
                    if thisMsg:
                        msg += thisMsg
        if msg:
            self._control.appendMessage(msg)
        return valid

    def removeEntity(self, entity):
        if isinstance(entity, SimulationEntity):
            subprogram = None
            if entity.isCall():
                subprogram = entity.getSubprogram()
                if subprogram:
                    entity.unlinkSubprogramCallWithSubprogram()
            if entity.isArgument():
                argName = entity.argName()
                if argName:
                    self._parent.blockNames().delete(argName)
            for attribute in list(entity.attributes().values()):
                attribute.unlinkAttributeWithVariableOrPort()
                eslname = attribute.eslname()
                if eslname:
                    self._parent.blockNames().delete(eslname)
            for port in list(entity.ports().values()):
                eslname = port.eslname()
                if eslname:
                    self._parent.blockNames().delete(eslname)
            #### if subprogram and subprogram.application() is None: # preloaded TODO handle preloaded subprograms
            ####    if not subprogram.hasSubprogramCalls():
            ####        self._application.blockNames().delete(subprogram.eslname())
            del self._simulationEntities[entity.objectId()]
            self._application.frame().viewManager().applicationView().removeEntity(self.parent().moduleId(), entity.objectId())
        elif isinstance(entity, DisplayDefinition):
            self._application.displayNames().delete(entity.name)
            del self._displayDefinitions[entity.objectId()]
        elif isinstance(entity, InfoBlock):
            if entity.type() == "Module Annotation":
                self._parent.moduleAnnotationRemoved(entity)
            elif entity.type() == "Program Annotation":
                self._parent.programAnnotationRemoved(entity)
            del self._infoBlocks[entity.objectId()]

    def checkValidToRemove(self, entity):
        valid = True
        msg = ''
        if isinstance(entity, SimulationEntity):
            for port in list(entity.ports().values()):
                if len(port.assignedAttributes()) > 0:
                    valid = False
                    msg = 'Cannot delete simulation entity as a port is being used as an attribute value\n'
                    break
        if msg:
            self._control.appendMessage(msg)
        return valid

    def getEntity(self, objectId):
        entity = self._simulationEntities.get(objectId)
        if not entity:
            entity = self._displayDefinitions.get(objectId)
        if not entity:
            entity = self._infoBlocks.get(objectId)
        return entity

    def getLibraryList(self):
        libraryList = []
        for entity in self._simulationEntities.values():
            libList = entity.includeList()
            if len(libList) > 0:
                newLibs = filter(lambda lib: lib not in libraryList, libList)
                libraryList.extend(newLibs)
        return libraryList

    def updateSubprogramCalls(self, subprogram, portsActionStr, suppress_action=False):
        for entity in list(self._simulationEntities.values()):
            if entity.isCall() and entity.subprogram() is not None:
                if entity.subprogram().eslname().upper() == subprogram.eslname().upper():
                    annotationsChangeInfo = entity.setupSubprogramCallPortsNAtts(matchPortsById=False)
                    self._control.propertiesControl().refreshEntityProperties(entity)
                    if not suppress_action:
                        updateActionStr = dgAction.makeUpdateSubprogramCallActionStr(entity, portsActionStr, annotationsChangeInfo=annotationsChangeInfo)
                        dgAction.sendDiagramUpdate(self, updateActionStr, applicationDataType="", applicationDataContents="", secondary=True, raiseEvent=True) # or should that be raiseEvent=False

    def setupAnnotationTexts(self):
        updateActionStr = ""
        for entity in list(self._simulationEntities.values()):
            updateActionStr += dgAction.makeUpdateEntitySetupAnnotationsActionStr(entity)
        if updateActionStr:
            dgAction.sendDiagramUpdate(self, updateActionStr, applicationDataType="annotation", applicationDataContents="",
                                   secondary=False, raiseEvent=False)
