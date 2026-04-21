#! /usr/bin/python

import wx
import wx.propgrid as wxpg

from ..application.argumententity import ArgumentEntity
from ..application.applicationtypes import CALLABLEMODULETYPES
from ..propertiescontrol import PropertyRefSeparator, PropertyChildSeparator
from .propertiesviewsimulationentity import PropertiesViewSimulationEntity
from .properties.eslvaluestrproperty import ESLValueStrProperty, ESLValueStrPropertyButtonEditor
from .properties.coreproperties import FlagsProperty, PROPERTY_DEFAULT_COLOUR, PROPERTY_STANDARD_COLOUR

class PropertiesViewArgumentEntity(PropertiesViewSimulationEntity):

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewSimulationEntity.__init__(self, propertiesViewEntityPage)
        self._isInput = False
        self._isForSegment = False

    def setAttributeProperties(self, newItem, simulationEntity, ref, label="Argument Attributes"):
        super(PropertiesViewArgumentEntity, self).setAttributeProperties(newItem, simulationEntity, ref, label)

        self._isInput = simulationEntity.isInputArgument()
        module = simulationEntity.parent().parent()
        self._isForSegment = module.moduleType() in CALLABLEMODULETYPES and module.callableType() == 'segment'

        # Arg Name
        self.checkGeneratedArgName(simulationEntity)
        # Arg Description
        # Dimensions
        # is Attribute (bool)
        # Initial Value (ESLValue) - for outputs

    def isActiveAttributeProperty(self, property):
        # May want the (special) simulation entity to decide this based on other attributes.
        active = True
        attTag = property.attTag()
        if attTag == "ATTR":
            active = self._isInput
        elif attTag == "INIT":
            active = True if not self._isInput and self._isForSegment else False
        return active

    def checkGeneratedArgName(self, simulationEntity):
        attribute = simulationEntity.getAttribute("ARG")
        attRef = self._entityPage.getAttPropertyRef('entity-attribute', self._entityPage._pagePropertyId, "ARG")
        property = self._entityPage._page.GetProperty(attRef)
        if property:
            argNameDescription = attribute.description()
            if not simulationEntity.argName():
                genArgName = simulationEntity.getArgName()
                property.attribute().eslValue().set_defaultValueStr(genArgName)
                property.GetCell(0).SetBgCol(PROPERTY_DEFAULT_COLOUR)
                property.GetCell(1).SetBgCol(PROPERTY_DEFAULT_COLOUR)
                property.SetLabel(argNameDescription + " *")
            else:
                property.GetCell(0).SetBgCol(PROPERTY_STANDARD_COLOUR)
                property.GetCell(1).SetBgCol(PROPERTY_STANDARD_COLOUR)
                property.SetLabel(argNameDescription)
        pass
