#! /usr/bin/python

import wx.propgrid as wxpg

from ..application.segmentcall import SegmentCall
from ..application.attribute import Attribute
from ..esl.esl import EslTypeNames
from ..propertiescontrol import PropertyRefSeparator, PropertyChildSeparator
from .propertiesviewcallentity import PropertiesViewCallEntity
from .properties.eslvaluestrproperty import ESLValueStrProperty, ESLValueStrPropertyButtonEditor
from .properties.attributeproperty import AttributeProperty
from .properties.longstringproperty import LongStringProperty

class PropertiesViewSegmentCall(PropertiesViewCallEntity):

    Prop_types = SegmentCall.SpecialAttributeTags #["frequency", "delay", "callorder", "postcallcode"]
    Prop_propertyTypes = SegmentCall.SpecialAttributeDatatypes #["Integer", "Real", "Integer", "String"]
    Prop_labels = SegmentCall.SpecialAttributeDescriptions # also description for annotations
    Prop_help = [
        "Frequency of communication region calls for the segment - a multiple of communication interval (CINT)." +
            "\nNote: The segment should have its Simulation Parameter CINT set to this value multiplied by the CINT of the calling module.",
        "Frequency of communication region calls for the segment - a multiple of communication interval (CINT)." +
        "\nNote: The segment should have its Simulation Parameter TSTART set to this value.",
        # For the Call Order and Post Call Code properties
        "Order (integer) to determine the position of this segment call, where there are multiple segment calls, in the generated code for the diagram subprogram this is in.\nA higher call order value inserts the segment call after a lower one.",
        "ESL code to be inserted directly after the segment call in the generated code for the calling module.\nPress the button to see and edit the code in a multi-line dialog.\n" +
        "This code is not validated in ESL-Studio (but is checked by the ESL compiler when the code is generated)."
    ]

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewCallEntity.__init__(self, propertiesViewEntityPage)

    def setSpecialProperties(self, newItem, simulationEntity, ref):
        # When create these insert in the specials category (hidden or relabelled)
        self._entityPage._specialCategory.SetLabel("Segment Call Control")

        # Not specialRef = 'S' + PropertyRefSeparator + self._entityPage._pagePropertyId + PropertyRefSeparator
        # Note currently ref = 'E' + PropertyRefSeparator + str(canvasId) + PropertyRefSeparator + str(objectId) + PropertyChildSeparator
        specialRef = ref

        definedAttributesDict = {}
        if simulationEntity.type():
            definedAttributesDict = self._entityPage.propertiesView().frame().control().entities().getAttributesDict(simulationEntity.type())

        # Frequency
        frequencyAttribute = simulationEntity.frequencyAttribute()
        prop = self.setSpecialProperty(newItem, simulationEntity, specialRef, 0, frequencyAttribute, definedAttributesDict)

        # Delay
        delayAttribute = simulationEntity.delayAttribute()
        prop = self.setSpecialProperty(newItem, simulationEntity, specialRef, 1, delayAttribute, definedAttributesDict)

        # Call Order (property not attribute)
        propIndex = 2
        propType = PropertiesViewSegmentCall.Prop_types[propIndex] # tag
        definedAttribute = definedAttributesDict.get(propType)
        value = simulationEntity.call_order()
        prop = self._entityPage._specialProperties.get(propType)
        if not prop:
            propLabel = PropertiesViewSegmentCall.Prop_labels[propIndex]
            helpText = PropertiesViewSegmentCall.Prop_help[propIndex]
            if definedAttribute:
                if definedAttribute.description():
                    propLabel = definedAttribute.description()
                if definedAttribute.hint():
                    helpText = definedAttribute.hint()
            if value is None:
                value = 0
            prop = wxpg.IntProperty(propLabel, ref + propType, value=value)
            prop.SetHelpString(helpText)
            self._entityPage._page.AppendIn(self._entityPage._specialCategory, prop)
            self._entityPage._specialProperties[propType] = prop
        else:
            prop.SetName(ref + propType)
            prop.SetValue(value)

        # Post Call Code (property not attribute)
        propIndex = 3
        propType = PropertiesViewSegmentCall.Prop_types[propIndex] # tag
        definedAttribute = definedAttributesDict.get(propType)
        value = simulationEntity.post_call_code()
        prop = self._entityPage._specialProperties.get(propType)
        if not prop:
            propLabel = PropertiesViewSegmentCall.Prop_labels[propIndex]
            helpText = PropertiesViewSegmentCall.Prop_help[propIndex]
            if definedAttribute:
                if definedAttribute.description():
                    propLabel = definedAttribute.description()
                if definedAttribute.hint():
                    helpText = definedAttribute.hint()
            prop = LongStringProperty(propLabel, ref + propType, value=value)
            prop.SetHelpString(helpText)
            self._entityPage._page.AppendIn(self._entityPage._specialCategory, prop)
            self._entityPage._specialProperties[propType] = prop
        else:
            prop.SetName(ref + propType)
            prop.SetValue(value)

        self._entityPage._specialCategory.Hide(False)
        # Have to hide/show properties *after* show the category.
        for propKey in self._entityPage._specialProperties.keys():
            primePropKey = propKey.split(PropertyChildSeparator)[0]
            if primePropKey.endswith(Attribute.ValueEnumRefExtn):
                primePropKey = primePropKey[:-len(Attribute.ValueEnumRefExtn)]
            hide = True if primePropKey not in PropertiesViewSegmentCall.Prop_types else False
            prop = self._entityPage._specialProperties[propKey]
            if not hide:
                if primePropKey != "callorder" and primePropKey != "postcallcode": # then it is an Attribute property - must cope with its Source variant
                    source = None
                    if primePropKey == 'frequency':
                        source = frequencyAttribute.source()
                    elif primePropKey == 'delay':
                        source = delayAttribute.source()
                    if propKey == primePropKey:  # The main property
                        if source != Attribute.SourceValue:
                            hide = True
                    else: # the other property
                        if source == Attribute.SourceValue:
                            hide = True
            prop.Hide(hide)
            if not hide:
                if primePropKey != "callorder" and primePropKey != "postcallcode":
                    prop.checkHiddenChildren()

    def setSpecialProperty(self, newItem, simulationEntity, specialRef, propIndex, value, definedAttributesDict):
        propType = PropertiesViewSegmentCall.Prop_types[propIndex]
        propertyType = PropertiesViewSegmentCall.Prop_propertyTypes[propIndex]
        propLabel = PropertiesViewSegmentCall.Prop_labels[propIndex]
        definedAttribute = definedAttributesDict.get(propType)
        attribute = simulationEntity.attributes().get(propType)
        if definedAttribute and definedAttribute.description():
            propLabel = definedAttribute.description()
        if attribute and attribute.description():
            propLabel = attribute.description()
        helpText = PropertiesViewSegmentCall.Prop_help[propIndex]
        if definedAttribute and definedAttribute.hint():
            helpText = definedAttribute.hint()
        if attribute and attribute.hint():
            helpText = attribute.hint()
        attributesCategory = self._entityPage._specialCategory
        attRef = specialRef + propType
        prop = self._entityPage._specialProperties.get(propType)
        if not prop:
            prop = self._entityPage.page().GetProperty(attRef)
        if not prop:
            prop, valueEnumProperty = self._entityPage.createAttributeProperty(attributesCategory, attRef, value)
            self._entityPage._specialProperties[propType] = prop
            if valueEnumProperty:
                self._entityPage._specialProperties[propType+Attribute.ValueEnumRefExtn] = valueEnumProperty

            prop.SetHelpString(helpText)
        else:
            otherProp = prop.getOtherProperty()
            prop.SetName(attRef)
            prop.SetLabel(propLabel)
            prop.SetHelpString(helpText)
            prop.setAttributeProperty(attRef, value)
            if otherProp:
                otherAttRef = otherProp.attRef()
                if otherAttRef.endswith(Attribute.ValueEnumRefExtn):
                    otherAttRef = otherAttRef[:-len(Attribute.ValueEnumRefExtn)]
                otherAttRef += Attribute.ValueEnumRefExtn
                otherProp.SetName(otherAttRef)
                otherProp.SetLabel(propLabel)
                otherProp.SetHelpString(helpText)
                otherProp.setAttributeProperty(otherAttRef, value)
        if newItem:
            prop.SetExpanded(False)
        return prop
