#! /usr/bin/python

import os
from collections import OrderedDict

import esl_diagram.xmlutil as xut

from .. import utils as Utils
from ..application.attribute import Attribute
from ..application.port import Port, PortIoDesignations
from ..application.submodel import Submodel

class Entities(object):

    TagAttributeProfileDict = {"entity":"type", "display":"type", "info":"type"}

    def __init__(self, control):
        self._control = control
        self._entitiesXmlProfile = xut.XmlElement("<entities-profile/>")

    def setup(self):
        self.clear()

    def clear(self):
        self._entities = {}
        self._preloadedSubmodels = OrderedDict()
        self._entitiesXmlProfile = xut.XmlElement("<entities-profile/>")

    def get(self, type):
        result = self._entities.get(type)
        return result

    def getPreloadedSubprogram(self, submodelName):
        result = self._preloadedSubmodels.get(submodelName)
        return result

    def loadFromFile(self, filepath):
        if os.path.exists(filepath):
            xmlElement, error = xut.xmlElementFromFile(filepath)
            if xmlElement:
                self.loadFromXml(xmlElement)

    def loadFromString(self, strng):
        xmlElement = xut.xmlElement(strng)
        if xmlElement:
            self.loadFromXml(xmlElement)

    def loadFromXml(self, xmlElement):
        if xmlElement.name() == "entities": entitiesXmlElement = xmlElement
        else: entitiesXmlElement = xmlElement.getXmlElementByName("entities", True)
        if entitiesXmlElement:
            entityXmlList = entitiesXmlElement.getChildren()
            for entityXmlElement in entityXmlList:
                self._entitiesXmlProfile.replaceOrAppendChild(entityXmlElement, Entities.TagAttributeProfileDict)

    def installProfile(self):
        self._modelEntityDefinitions = xut.XmlElement('<definitions/>')
        self._subprogramEntityDefinitions = xut.XmlElement('<definitions/>')
        entityXmlList = self._entitiesXmlProfile.getChildren()
        for entityXmlElement in entityXmlList:
            category = entityXmlElement.name()
            if category == "entity" or category == "display" or category == "info":
                type = entityXmlElement.getAttribute("type")
                if type:
                    self._entities[type] = entityXmlElement
                    self.appendDiagramDefinition(entityXmlElement, category, type)
                    subprogramName = self._setupPreloadedSubprogram(entityXmlElement)       #### TODO something when sort out preloaded code subprograms
        self._control.appendDiagramDefinition(self._modelEntityDefinitions, 'model-diagram')
        self._control.appendDiagramDefinition(self._subprogramEntityDefinitions, 'subprogram-diagram')

    def getEntityDefnXmlElement(self, type):
        return self._entities.get(type)

    def appendDiagramDefinition(self, entityXmlElement, category, type):
        designElements = entityXmlElement.getXmlElementListByName("design")
        for designElement in designElements:
            designType = designElement.getAttribute("type")
            designElement.setAttribute("category", category)
            designElement.setAttribute("type", type)
            Utils.hardenPaths(designElement)
            if not designType or designType == 'block-diagram':
                self._modelEntityDefinitions.appendChild(designElement)
                self._subprogramEntityDefinitions.appendChild(designElement)
            elif designType == 'model-diagram':
                self._modelEntityDefinitions.appendChild(designElement)
            elif designType == 'subprogram-diagram':
                self._subprogramEntityDefinitions.appendChild(designElement)

    def getAttributesDict(self, type):
        result = OrderedDict()
        entityDefnXmlElement = self._entities.get(type)
        if entityDefnXmlElement:
            entityModelXmlElement = entityDefnXmlElement.getXmlElementByName("model")
            if entityModelXmlElement:
                attXmlList = entityModelXmlElement.getXmlElementListByName("attribute", False)
                index = 0
                for attXmlElement in attXmlList:
                    index += 1
                    attribute = Attribute(None)
                    attribute.load(attXmlElement)
                    if not attribute.tag():
                        attribute.set_tag('Att'+str(index))
                    tag = attribute.tag()
                    initial_value =  attXmlElement.getAttribute("value")
                    if initial_value and initial_value == attribute.valueStr(): # this should be the default as well as the value
                        attribute.set_default_value(initial_value)
                    result[tag] = attribute
        return result

    def getPortsDict(self, type):
        result = OrderedDict()
        entityDefnXmlElement = self._entities.get(type)
        if entityDefnXmlElement:
            entityModelXmlElement = entityDefnXmlElement.getXmlElementByName("model")
            if entityModelXmlElement:
                ioXmlList = []
                children = entityModelXmlElement.getChildren()
                for child in children:
                    if child.name() in list(PortIoDesignations.keys()):
                        ioXmlList.append(child)
                index = 0
                for ioXmlElement in ioXmlList:
                    index += 1
                    port = Port(None)
                    port._id = str(index)
                    port.load(ioXmlElement)
                    result[port.id()] = port
        return result

    def _setupPreloadedSubprogram(self, entityXmlElement):        #### TODO this must now be PreloadedCodeSubprogram(s)
        submodelName = None
        modelXmlElement = entityXmlElement.getXmlElementByName("model")
        if modelXmlElement:
            entityModelType = modelXmlElement.getAttribute("type")
            codeType = None
            if entityModelType == "ESL-submodel":
                codeType = "ESL"
            elif entityModelType == "file-submodel":
                codeType = "file"
            if codeType:
                submodel = Submodel(None, moduleId=0)
                submodel.set_codeType(codeType)
                submodel.load(modelXmlElement, preload=True)
                badName = "?-" + str(len(self._preloadedSubmodels))  # use invalid submodelname if submodel is invalid
                submodelName = badName
                if submodel.valid():
                    submodelName = submodel.eslname()
                    if submodelName:
                        previous = self._preloadedSubmodels.get(submodelName)
                        if previous:
                            msg = 'Cannot use preloaded submodel with a duplicate name "'+submodelName+'"\n'
                            self._control.appendMessage(msg)
                            submodelName = badName
                    else:
                        submodelName = badName
                self._preloadedSubmodels[submodelName] = submodel
                if modelXmlElement: # add submodel name to model element
                    modelXmlElement.setAttribute("submodel", submodelName)
        return submodelName
