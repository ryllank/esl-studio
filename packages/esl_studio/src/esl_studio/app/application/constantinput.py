#! /usr/bin/python

from ..esl.parseesl import ParseEsl, DimensionalityParseObject
from .simulationentity import SimulationEntity
from .port import PortConnectorSeparator
from .diagraminfo import DiagramInfo
from . import diagramactions as dgAction

class ConstantInput(SimulationEntity):

    def __init__(self, parent, type="", objectId=""):
        SimulationEntity.__init__(self, parent, type, objectId)
        self._scalar_default_value = ""
        # Constant Input's Value attribute is first, and its scalar-default-value is specified in the (profile) definitions for that attribute.
        if self._entityDefnXmlElement:
            attributeXmlElementList = self._entityDefnXmlElement.getXmlElementListByName("attribute", recurse=True)
            val = attributeXmlElementList[0].getAttribute("scalar-default-value")
            if val is not None:
                self._scalar_default_value = val
        self._parseEsl = ParseEsl()
        valueAttribute = self.get_valueAttribute()
        if self._scalar_default_value and valueAttribute is not None:
            self.reset_defaultValueStr(valueAttribute)
        return

    def get_valueAttribute(self):
        valueAttribute = None
        if len(self._attributes) > 0:
            valueAttribute = list(self._attributes.values())[0]  # first attribute is for the Value (tag maybe K, K or L depending on type)
        return valueAttribute

    def reset_defaultValueStr(self, valueAttribute):
        valueStr = self._scalar_default_value
        dimensionsAttribute = self._attributes.get('dimensions') # Dimensions attribute has tag 'dimensions',
        if dimensionsAttribute:
            dimensions = dimensionsAttribute.valueStr()
            if dimensions != "":
                pos, dimensionality = self._parseEsl.parseDimensions(dimensions, 0, None, checkNothingLeft=True, allowStar=False)
                valueStr = str(dimensionality.size()) + "*" + valueStr
        valueAttribute.eslValue().set_defaultValueStr(valueStr)

    def load(self, entityDescrXmlElement, suppressAddName=False):
        super(ConstantInput, self).load(entityDescrXmlElement, suppressAddName)
        valueAttribute = self.get_valueAttribute()
        if self._scalar_default_value and valueAttribute is not None:
            self.reset_defaultValueStr(valueAttribute)
        # See if constant input's output port dimensions should be set
        dimensions = valueAttribute.dimensions()
        if dimensions:
            # Should always have just one output port (id '1')
            port = list(self._ports.values())[0]
            if port is not None:
                port.set_dimensions(dimensions)
                # Update the diagram entity port datatype
                newEntityObjectId = ""
                if self._parent.oldToNewObjectIds():
                    newEntityObjectId = self._parent.oldToNewObjectIds().get(self.objectId())
                actionStr = dgAction.makeUpdateEntityPortActionStr(self, port, newEntityObjectId)
                dgAction.sendDiagramUpdate(self._parent, actionStr, applicationDataType="",
                                           applicationDataContents="", secondary=False, raiseEvent=False)
                self._parent.canvas().Refresh()
        return

    def copyFrom(self, anotherConstantInput, parent):
        self._scalar_default_value = anotherConstantInput._scalar_default_value
        super(ConstantInput, self).copyFrom(anotherConstantInput, parent)

    def validateEntityAttributePropertyChange(self, propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue
        ) -> (bool, str, str, str, str, str, str):         # Override this in any special types of simulation entity that have entity properties that need validating.
        """ returns: valid:bool, rejection:str, val_type:str, val_item:str, val_oldValue:str, val_newValue:str, updatedPropertyValue:str """
        valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue = super(ConstantInput, self).validateEntityAttributePropertyChange(
            propertyTag, newValue, attribute, val_type, val_item, val_oldValue, val_newValue)
        if valid:
            if propertyTag == 'dimensions':
                dummyAttribute = attribute.detachedCopy(attribute.parent())
                dummyAttribute.loadData(newValue, suppressAddName=True)
                dimensionsText = dummyAttribute.valueStr() # Attribute's value (String) - not the same as the Attribute/Variable(ESLValue).dimensions
                dimensionality = None
                if dimensionsText != attribute.valueStr(): # else no change to *actual* dimensions (an annotation)
                    if dimensionsText and dimensionsText[0] == "(":
                        if dimensionsText[-1] == ")":
                            dimensionsText = dimensionsText[1:-1].strip()
                        else:
                            rejection = "dimensions should not be in mis-matched brackets"
                            valid = False
                    if valid and dimensionsText != "": # allow blank dimensions
                        diagramInfo = self._parent
                        subprogram = diagramInfo.parent()
                        port = list(self._ports.values())[0] # Should always have just one output port (id '1')
                        if port is not None:
                            portsConnections = diagramInfo.canvas().EstablishPortsConnections(self.objectId())
                            portIsConnected = False
                            portId = str(self.objectId()) + PortConnectorSeparator + str(port.id())
                            for pair in portsConnections:
                                if pair[0] == portId:
                                    portIsConnected = True if len(pair[1]) else False
                                    break
                            if portIsConnected:
                                rejection = "cannot change the dimensions of a constant input while it is connected to something in its diagram (" + subprogram.identification() + ")"
                                valid = False
                        if valid:
                            # Validate Value attribute (tag maybe K, K or L depending on type) - not assigned to a variable
                            valueAttribute = self.get_valueAttribute()
                            if valueAttribute is not None:
                                if valueAttribute.variableOrPort() is not None:
                                    rejection = "cannot change the dimensions of a constant input while its Value attribute is assigned to a variable or output port"
                                    valid = False
                                pass
                        # Validate dimensions via parseDimensions
                        if valid:
                            pos, dimensionality = self._parseEsl.parseDimensions(dimensionsText, 0, None, checkNothingLeft=True, allowStar=False)
                            if dimensionality is not None:
                                for parseMessage in dimensionality.messages:
                                    dimMsg = parseMessage.message + " "
                                    if dimMsg:
                                        rejection += dimMsg
                                        valid = False
                    if valid:
                        updatedValueStr = ""
                        if dimensionality is not None:
                            updatedValueStr = dimensionality.dimensions()  # standard form for dimensions
                        if updatedValueStr != dummyAttribute.valueStr():
                            dummyAttribute.set_valueStr(updatedValueStr)
                        updatedPropertyValue = dummyAttribute.save(saveDefaults=True)
                if rejection:
                    val_item = "Dimensions"
                    val_oldValue = attribute.shortAttributeValueText(showName=True, showValue=True)
                    val_newValue = dummyAttribute.shortAttributeValueText(showName=True, showValue=True)
        return valid, rejection, val_type, val_item, val_oldValue, val_newValue, updatedPropertyValue

    def updateEntityAttributeProperty(self, propertyTag, newValue, attribute, tempOldAttribute, suppress_action=False) -> bool:  # Handle update of Dimensions attribute property.
        updateEntityPropertiesView = False
        module = None
        if isinstance(self.parent(), DiagramInfo):
            module = self.parent().parent()
        if propertyTag == 'dimensions':
            # The attribute's valueStr property is now standard form for dimensions
            dimensions = attribute.valueStr()
            if dimensions != tempOldAttribute.valueStr():
                # Should always have just one output port (id '1')
                port = list(self._ports.values())[0]
                if port is not None:
                    port.set_dimensions(dimensions)
                # Check (or change if default) Value attribute (tag maybe K, K or L depending on type).
                valueAttribute = self.get_valueAttribute()
                if valueAttribute is not None:
                    valueAttribute.set_dimensions(dimensions)
                    self.reset_defaultValueStr(valueAttribute)
                    valueAttribute.eslValue().checkValidity()
                    pass
                if port is not None:
                    # Update the diagram entity port datatype
                    actionStr = dgAction.makeUpdateEntityPortActionStr(self, port)
                    dgAction.sendDiagramUpdate(self._parent, actionStr, applicationDataType="",
                                               applicationDataContents="", secondary=False, raiseEvent=False)
                    self._parent.canvas().Refresh()
                updateEntityPropertiesView = True
        return updateEntityPropertiesView
