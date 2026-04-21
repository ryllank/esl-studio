#! /usr/bin/python

import wx.propgrid as wxpg

from ..application.segmentcall import SegmentCall
from ..application.attribute import Attribute
from ..esl.esl import EslTypeNames
from ..propertiescontrol import PropertyRefSeparator, PropertyChildSeparator
from .propertiesviewcallentity import PropertiesViewCallEntity
from .properties.eslvaluestrproperty import ESLValueStrProperty, ESLValueStrPropertyButtonEditor
from .properties.attributeproperty import AttributeProperty

class PropertiesViewSegmentCall(PropertiesViewCallEntity):

    Prop_types = SegmentCall.SpecialAttributeTags #["frequency", "delay"]
    Prop_propertyTypes = SegmentCall.SpecialAttributeDatatypes #["Integer", "Real"]
    Prop_labels = SegmentCall.SpecialAttributeDescriptions # also description for annotations
    Prop_help = [
        "Frequency of communication region calls for the segment - a multiple of communication interval (CINT)." +
            "\nNote: The segment should have its Simulation Parameter CINT set to this value multiplied by the CINT of the calling module.",
        "Frequency of communication region calls for the segment - a multiple of communication interval (CINT)." +
        "\nNote: The segment should have its Simulation Parameter TSTART set to this value."
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

        self._entityPage._specialCategory.Hide(False)
        # Have to hide/show properties *after* show the category.
        for propKey in self._entityPage._specialProperties.keys():
            primePropKey = propKey.split(PropertyChildSeparator)[0]
            if primePropKey.endswith(Attribute.ValueEnumRefExtn):
                primePropKey = primePropKey[:-len(Attribute.ValueEnumRefExtn)]
            hide = True if primePropKey not in PropertiesViewSegmentCall.Prop_types else False
            prop = self._entityPage._specialProperties[propKey]
            if not hide:
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
