#! /usr/bin/python

from collections import OrderedDict

import wx
import wx.propgrid as wxpg

from .. import utils as Utils
from ..propertiescontrol import PropertyRefSeparator, PropertyIdSeparator, PropertyChildSeparator
from .propertiesviewpage import PropertiesViewPage
from .propertiesviewsimulationentity import PropertiesViewSimulationEntity
from .propertiesviewtransferfunction import PropertiesViewTransferFunction
from .propertiesviewsubmodelcall import PropertiesViewSubmodelCall
from .propertiesviewsegmentcall import PropertiesViewSegmentCall
from .propertiesviewfunctioncall import PropertiesViewFunctionCall
from .propertiesviewinputargument import PropertiesViewInputArgument
from .propertiesviewoutputargument import PropertiesViewOutputArgument
from .propertiesviewcodeinsert import PropertiesViewCodeInsert
from .propertiesviewconstantinput import PropertiesViewConstantInput
from .properties.attributeproperty import makeAttributeProperty, AttributeProperty
from .properties.portproperty import PortProperty
from .properties.coreproperties import CompoundProperty, FlagsProperty
from ..application.attribute import Attribute
from ..application.diagraminfo import DiagramInfo

class PropertiesViewEntity(PropertiesViewPage):
    def __init__(self, propertiesView):
        PropertiesViewPage.__init__(self, propertiesView)
        self._supportObjects = OrderedDict()
        self._application = self._propertiesView.application()
        self._page = self._propertiesView.page()
        self._pgm = self._propertiesView.pgm()
        self._pagePropertyId = ""
        self._supportPage = None
        # properties
        self._definedCategory = None
        self._definedProperties = dict() # type summary help view
        self._entityCategory = None
        self._entityProperties = dict() # description submodel(special SubmodelCall) annotations (for entity properties)
        self._specialCategory = None
        self._specialProperties = dict() # any special entity properties (after entity properties before attributes)
        self._attributesCategory = None
        self._nrAttributes = 0 # number being shown (not number in _attributePropertiesList)
        self._attributePropertiesList = []
        self._special2Category = None
        self._special2Properties = dict() # any special (2) entity properties (after attributes properties before ports)
        self._portsCategory = None
        self._nrPorts = 0 # number being shown (not number in _portPropertiesList)
        self._portPropertiesList = []
        self._special3Category = None
        self._special3Properties = dict() # any special (3) entity properties (after ports)
        self._entitySubprogram = None

    def page(self): return self._page
    def pgm(self): return self._pgm

    def getSupportObject(self, specialType):
        if not specialType:
            specialType = "Simulation Entity"
        support = self._supportObjects.get(specialType)
        if support is None:
            if specialType == "Transfer Function":
                support = PropertiesViewTransferFunction(self)
            elif specialType == "Submodel Call":
                support = PropertiesViewSubmodelCall(self)
            elif specialType == "Segment Call":
                support = PropertiesViewSegmentCall(self)
            elif specialType == "Function Call":
                support = PropertiesViewFunctionCall(self)
            elif specialType == "Input Argument":
                support = PropertiesViewInputArgument(self)
            elif specialType == "Output Argument":
                support = PropertiesViewOutputArgument(self)
            elif specialType == "Code Insert":
                support = PropertiesViewCodeInsert(self)
            elif specialType == "Constant Input":
                support = PropertiesViewConstantInput(self)
            else:
                support = PropertiesViewSimulationEntity(self)
            self._supportObjects[specialType] = support
        return support

    def setMode(self, mode):
        properties = [ ] #definedPropertiesw - always disabled
        properties.extend(self._entityProperties.values())
        properties.extend(self._specialProperties.values())
        properties.extend(self._attributePropertiesList)
        properties.extend(self._special2Properties.values())
        properties.extend(self._portPropertiesList)
        properties.extend(self._special3Properties.values())
        for property in properties:
            if property:
                if isinstance(property, CompoundProperty):
                    property.enableWithChildren(mode == "editing")
                else:
                    property.Enable(mode == "editing")

    def resetPropertiesForNewApplication(self):
        # Ensure first item called after this (for new application) is treated as a new item
        self._pagePropertyId = ""
        self._supportPage = None

    def setEntityPropertyPage(self, pageType, propertyId, headerText):
        self._propertiesView.clearPropertyPage(headerText, pageType, 'entity', 0, propertyId)

        if not self._definedCategory:
            self._definedCategory = wxpg.PropertyCategory('Defined Properties')
            self._page.Append(self._definedCategory)

        if not self._entityCategory:
            self._entityCategory = wxpg.PropertyCategory('Entity Properties')
            self._page.Append(self._entityCategory)
            self._entityCategory.Hide(True) # we dont want to see this - is used to locate the entity properties

        if not self._specialCategory:
            self._specialCategory = wxpg.PropertyCategory('Special Properties')
            self._page.Append(self._specialCategory)

        if not self._attributesCategory:
            self._attributesCategory = wxpg.PropertyCategory('Attributes')
            self._page.Append(self._attributesCategory)

        if not self._special2Category:
            self._special2Category = wxpg.PropertyCategory('Special2 Properties')
            self._page.Append(self._special2Category)

        if not self._portsCategory:
            self._portsCategory = wxpg.PropertyCategory('Ports')
            self._page.Append(self._portsCategory)

        if not self._special3Category:
            self._special3Category = wxpg.PropertyCategory('Special3 Properties')
            self._page.Append(self._special3Category)

        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            canvasId = propertyIdSplit[0]
            objectId = propertyIdSplit[1]
            simulationEntity = self._application.getEntityForCanvasObjectIds(canvasId, objectId)
            if simulationEntity:

                self._supportPage = self.getSupportObject(simulationEntity.specialType())
                if self._supportPage:
                    self._supportPage.setEntityPropertyPage(pageType, propertyId, headerText, canvasId, objectId, simulationEntity)

        self.checkMode()

    def updateProperties(self, pageType, category, moduleId, propertyId, propertyTag, newValue):
        propertyIdSplit = propertyId.split(PropertyIdSeparator)
        if propertyIdSplit and len(propertyIdSplit) == 2:
            canvasId = int(propertyIdSplit[0])
            objectId = int(propertyIdSplit[1])
            headerText = None # don't change current header
            self.setEntityPropertyPage(pageType, propertyId, headerText)

    def createAttributeProperty(self, attributesCategory, attRef, attribute):
        property, valueEnumProperty = makeAttributeProperty(self, attRef, attribute)
        if attribute.hint():
            property.SetHelpString(attribute.hint())
        prop = self._page.Insert(attributesCategory, -1, property)
        if valueEnumProperty is not None:
            if attribute.hint():
                valueEnumProperty.SetHelpString(attribute.hint())
            prop = self._page.Insert(attributesCategory, -1, valueEnumProperty)
        return property, valueEnumProperty

    def appendAttributeProperty(self, attributesCategory, attRef, attribute):
        property, valueEnumProperty = self.createAttributeProperty(attributesCategory, attRef, attribute)
        self._propertiesView.variableProperties()[attRef] = property
        self._attributePropertiesList.append(property)
        if valueEnumProperty is not None:
            self._propertiesView.variableProperties()[valueEnumProperty.attRef()] = valueEnumProperty
            self._attributePropertiesList.append(valueEnumProperty)
        return property, valueEnumProperty

    def setEntityAttributeProperties(self, attributesCategory, newItem, simulationEntity, ref):
        allAttributes = list(simulationEntity.attributes().values())
        # only include attributes with a description - that aren't special
        attributes = []
        for i in range(len(allAttributes)):
            attribute = allAttributes[i]
            if attribute.description() and attribute.is_special() != "true":
                attributes.append(attribute)
        self._nrAttributes = len(attributes)
        attributesCategory.Hide(self._nrAttributes == 0)
        # Reusable attributes
        attributePropertyConservation = True # True to keep attribute properties in the grid - False to do fresh attribute properties each time for a new item.
        if self._nrAttributes > 0:
            if newItem:
                if not attributePropertyConservation:
                    for prop in self._attributePropertiesList:
                        attRef = prop.attRef()
                        property = self._page.GetProperty(attRef)
                        if property:
                            self._page.DeleteProperty(property)
                        del self._propertiesView.variableProperties()[attRef]
                self._attributePropertiesList = []
                self.setActiveAttributesPropertiesVisibility(None)
                for i in range(len(attributes)):
                    property = None
                    valueEnumProperty = None
                    attribute = attributes[i]
                    attRef = 'A' + PropertyRefSeparator + self._pagePropertyId + PropertyRefSeparator + attribute.tag()
                    if attributePropertyConservation:
                        property = self._page.GetProperty(attRef)
                        if property:
                            self._propertiesView.variableProperties()[attRef] = property
                            property.setAttributeProperty(attRef, attribute)
                            self._attributePropertiesList.append(property)
                            valueEnumProperty = property.getOtherProperty()
                            if valueEnumProperty:
                                valueEnumProperty.setAttributeProperty(attRef+Attribute.ValueEnumRefExtn, attribute)
                                self._propertiesView.variableProperties()[valueEnumProperty.attRef()] = valueEnumProperty
                                self._attributePropertiesList.append(valueEnumProperty)
                    if property is None:
                        property, valueEnumProperty = self.appendAttributeProperty(attributesCategory, attRef, attribute)
                    property.checkTopLevelValueFeatures()
                    if valueEnumProperty:
                        valueEnumProperty.checkTopLevelValueFeatures()
            else:
                self.setActiveAttributesPropertiesVisibility(simulationEntity)
                for property in self._attributePropertiesList:
                    attRef = property.attRef()
                    attTag = property.attTag()
                    attribute = simulationEntity.getAttribute(attTag)
                    if attribute:
                        propertyForm = property.propertyForm()
                        if propertyForm == 'ESLValue':
                            property.Hide(attribute.source() != Attribute.SourceValue)
                        elif propertyForm == 'ValueEnum':
                            property.Hide(attribute.source() == Attribute.SourceValue)
                        self._propertiesView.variableProperties()[attRef] = property
                        property.setAttributeProperty(attRef, attribute)
            Utils.queueFunctionCall(self.setActiveAttributesPropertiesVisibility, simulationEntity)

    def setActiveAttributesPropertiesVisibility(self, simulationEntity):
        for property in self._page.GetPyIterator():
            if isinstance(property, AttributeProperty):
                show = False
                if simulationEntity and property.entity() == simulationEntity:
                    show = self.isActiveAttributeProperty(property)
                property.Hide(not show)
                if show:
                    property.checkHiddenChildren()
                    show = property.setTopESLValueVisibility()

    def isActiveAttributeProperty(self, property):
        # A (special) simulation entity may decide this based on other attributes.
        active = True
        if self._supportPage:
            active = self._supportPage.isActiveAttributeProperty(property)
        return active

    def appendPortProperty(self, portsCategory, portRef, port):
        property = PortProperty(self, portRef, port)
        prop = self._page.Insert(portsCategory, -1, property)
        self._propertiesView.variableProperties()[portRef] = property
        self._portPropertiesList.append(property)
        return property

    def setEntityPortProperties(self, portsCategory, newItem, simulationEntity, ref):
        ports = list(simulationEntity.ports().values())
        self._nrPorts = len(ports)
        portsCategory.Hide(self._nrPorts == 0)
        # Reusable ports
        portPropertyConservation = True # True to keep port properties in the grid - False to do fresh port properties each time for a new item.
        if self._nrPorts > 0:
            if newItem:
                if not portPropertyConservation:
                    for prop in self._portPropertiesList:
                        portRef = prop.portRef()
                        property = self._page.GetProperty(portRef)
                        if property:
                            self._page.DeleteProperty(property)
                        del self._propertiesView.variableProperties()[portRef]
                self._portPropertiesList = []
                self.setPortsVisibility()
                for i in range(len(ports)):
                    property = None
                    port = ports[i]
                    portRef = 'O' + PropertyRefSeparator + self._pagePropertyId + PropertyRefSeparator + port.id()
                    if portPropertyConservation:
                        property = self._page.GetProperty(portRef)
                        if property:
                            property.Hide(False)
                            self._propertiesView.variableProperties()[portRef] = property
                            property.setPortProperty(portRef, port)
                            self._portPropertiesList.append(property)
                    if property is None:
                        self.appendPortProperty(portsCategory, portRef, port)
            else:
                self.setPortsVisibility()
                for property in self._portPropertiesList:
                    portRef = property.portRef()
                    pos = portRef.rfind(PropertyRefSeparator)
                    portId = ""
                    if pos >= 0:
                        portId = portRef[pos + 1:]
                    port = simulationEntity.ports().get(portId)
                    if port:
                        self._propertiesView.variableProperties()[portRef] = property
                        property.setPortProperty(portRef, port)

    def checkAttributesHiddenChildren(self):
        for prop in self._attributePropertiesList:
            prop.checkHiddenChildren()

    def getAttPropertyRef(self, category, canvasNObjectId, attributeTag):
        attRef = ''
        if category == 'entity-attribute':
            attRef = 'A'
        elif category == 'special-property':
            attRef = 'S'
        if attRef:
            attRef += PropertyRefSeparator
            attRef += str(canvasNObjectId)
            attRef += PropertyRefSeparator + attributeTag
        return attRef

    def setPortsVisibility(self):
        for property in self._page.GetPyIterator():
            if isinstance(property, PortProperty):
                show = property in self._portPropertiesList
                property.Hide(not show)

    def clearViewPage(self):
        #self.printPropertiesViewInfo()

        self._pagePropertyId = ""
        self._supportPage = None
        # properties
        self._definedCategory = None
        self._definedProperties = dict() # type summary help view
        self._entityCategory = None
        self._entityProperties = dict() # description submodel(special SubmodelCall) annotations (for entity properties)
        self._specialCategory = None
        self._specialProperties = dict() # any special entity properties (after entity properties before attributes)
        self._attributesCategory = None
        self._nrAttributes = 0 # number being shown (not number in _attributePropertiesList)
        self._attributePropertiesList = []
        self._special2Category = None
        self._special2Properties = dict() # any special (2) entity properties (after attributes properties before ports)
        self._portsCategory = None
        self._nrPorts = 0 # number being shown (not number in _portPropertiesList)
        self._portPropertiesList = []
        self._special3Category = None
        self._special3Properties = dict() # any special (3) entity properties (after ports)
        self._entitySubprogram = None

        self._page.Clear()

        #self.printPropertiesViewInfo()
        pass

    def printPropertiesViewInfo(self):
        result = ""
        pageProperties = list(self._page.GetPyIterator())
        text = ">PropertiesViewEntity.printPropertiesInfo nProps="+str(len(pageProperties))
        print(text)
        result += text + "\n"
        for property in pageProperties:
            propertyRef = "----"
            try:
                propertyRef = property.GetName()
            except:
                pass # if property had been somehow deleted from page
            text = "- propertyRef="+propertyRef
            print(text)
            result += text + "\n"
        text = "_definedProperties=" + str(list(self._definedProperties.keys()))
        print(text)
        result += text + "\n"
        text = "_entityProperties=" + str(list(self._entityProperties.keys()))
        print(text)
        result += text + "\n"
        text = "_specialProperties=" + str(list(self._specialProperties.keys()))
        print(text)
        result += text + "\n"
        propertyRefs = []
        for property in self._attributePropertiesList:
            propertyRef = "----"
            try:
                propertyRef = property.GetName()
            except:
                pass  # if property had been somehow deleted from page
            propertyRefs.append(propertyRef)
        text = "_attributePropertiesList=" + str(propertyRefs)
        print(text)
        result += text + "\n"
        text = "_special2Properties=" + str(list(self._special2Properties.keys()))
        print(text)
        result += text + "\n"
        propertyRefs = []
        for property in self._portPropertiesList:
            propertyRef = "----"
            try:
                propertyRef = property.GetName()
            except:
                pass  # if property had been somehow deleted from page
            propertyRefs.append(propertyRef)
        text = "_portPropertiesList=" + str(propertyRefs)
        print(text)
        result += text + "\n"
        text = "_special3Properties=" + str(list(self._special3Properties.keys()))
        print(text)
        result += text + "\n"
        return result
