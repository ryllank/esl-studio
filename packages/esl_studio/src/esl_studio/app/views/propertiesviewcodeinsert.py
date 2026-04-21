#! /usr/bin/python

import wx.propgrid as wxpg

from .propertiesviewsimulationentity import PropertiesViewSimulationEntity
from .. import utils as Utils
from ..application.codeinsert import CodeInsert
from ..propertiescontrol import PropertyRefSeparator
from .properties.longstringproperty import LongStringProperty

class PropertiesViewCodeInsert(PropertiesViewSimulationEntity):

    Prop_types = ["region", "insert", "esl", "outputs"]
    Prop_labels = ["ESL Region", "Insert Position", "ESL Code", "Output Ports"]
    Prop_helps = ["ESL region in generated code to insert the code.\nNote: The \"terminal\" and \"analysis\" regions are only applicable in a MODEL subprogram.",
                  "Insert the code at the beginning or end of the region - i.e. before or after generated code for the region.\nThe default is at the end.",
                  "The code insert's ESL text (source code).\nPress the button to see and edit the code in a multi-line dialog.\n"+
                  "This code is not validated in ESL-Studio (but is checked by the ESL compiler when the code is generated).\n"+
                  "Note: Procedural code to be inserted in the \"dynamic\" region will have to be in a WHEN statement or PROCEDURAL model block.",
                  "A semicolon-separated set of ESL Data Types for the output ports (valid for dynamic, communications & step regions).\n"+
                  "Note: You must set the ESL Names for these ports to use in the ESL Code of this code insert."]
    Region_enumTexts = CodeInsert.Region_values
    Insert_enumTexts = ["beginning of region", "end of region"]

    def __init__(self, propertiesViewEntityPage):
        PropertiesViewSimulationEntity.__init__(self, propertiesViewEntityPage)

    def setSpecialProperties(self, newItem, simulationEntity, ref):
        # When create these insert in the specials category (hidden or relabelled)
        self._entityPage._specialCategory.SetLabel("Code Insert Properties")

        specialRef = 'S' + PropertyRefSeparator + self._entityPage._pagePropertyId + PropertyRefSeparator

        propType = PropertiesViewCodeInsert.Prop_types[0]
        propLabel = PropertiesViewCodeInsert.Prop_labels[0]
        helpText = PropertiesViewCodeInsert.Prop_helps[0]
        value = simulationEntity.region()
        enum_value = CodeInsert.Region_values.index(value)
        prop = self._entityPage._specialProperties.get(propType)
        if not prop:
            enum_texts = PropertiesViewCodeInsert.Region_enumTexts
            enum_values = list(range(len(enum_texts)))
            prop = wxpg.EnumProperty(propLabel, ref + propType, enum_texts, enum_values, enum_value)
            prop.SetHelpString(helpText)
            self._entityPage._page.AppendIn(self._entityPage._specialCategory, prop)
            self._entityPage._specialProperties[propType] = prop
        else:
            prop.SetName(ref + propType)
            prop.SetValue(enum_value)

        propType = PropertiesViewCodeInsert.Prop_types[1]
        propLabel = PropertiesViewCodeInsert.Prop_labels[1]
        helpText = PropertiesViewCodeInsert.Prop_helps[1]
        value = simulationEntity.insert_position()
        enum_value = CodeInsert.Insert_values.index(value)
        prop = self._entityPage._specialProperties.get(propType)
        if not prop:
            enum_texts = PropertiesViewCodeInsert.Insert_enumTexts
            enum_values = list(range(len(enum_texts)))
            prop = wxpg.EnumProperty(propLabel, ref + propType, enum_texts, enum_values, enum_value)
            prop.SetHelpString(helpText)

            self._entityPage._page.AppendIn(self._entityPage._specialCategory, prop)
            self._entityPage._specialProperties[propType] = prop
        else:
            prop.SetName(ref + propType)
            prop.SetValue(enum_value)

        propType = PropertiesViewCodeInsert.Prop_types[2]
        propLabel = PropertiesViewCodeInsert.Prop_labels[2]
        helpText = PropertiesViewCodeInsert.Prop_helps[2]
        value = Utils.escapeText(simulationEntity.esl())
        prop = self._entityPage._specialProperties.get(propType)
        if not prop:
            prop = LongStringProperty(propLabel, ref + propType, value=value)
            prop.SetHelpString(helpText)

            self._entityPage._page.AppendIn(self._entityPage._specialCategory, prop)
            self._entityPage._specialProperties[propType] = prop
        else:
            prop.SetName(ref + propType)
            prop.SetValue(value)

        propType = PropertiesViewCodeInsert.Prop_types[3]
        propLabel = PropertiesViewCodeInsert.Prop_labels[3]
        helpText = PropertiesViewCodeInsert.Prop_helps[3]
        value = simulationEntity.outputs()
        prop = self._entityPage._specialProperties.get(propType)
        if not prop:
            prop = wxpg.StringProperty(propLabel, specialRef + propType, value=value)
            prop.SetHelpString(helpText)

            self._entityPage._page.AppendIn(self._entityPage._specialCategory, prop)
            self._entityPage._specialProperties[propType] = prop
        else:
            prop.SetName(specialRef + propType)
            prop.SetValue(value)
        prop.Enable(simulationEntity.region() in CodeInsert.Regions_for_outputs)

        self._entityPage._specialCategory.Hide(False)
        # Have to hide/show properties *after* show the category.
        for propType in self._entityPage._specialProperties.keys():
            hide = True if propType not in PropertiesViewCodeInsert.Prop_types else False
            self._entityPage._specialProperties[propType].Hide(hide)
