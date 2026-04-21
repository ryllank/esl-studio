#! /usr/bin/python

import wx.propgrid as wxpg

from ..propertiescontrol import PropertyRefSeparator, PropertyIdSeparator, PropertyChildSeparator
from .properties.coreproperties import FlagsProperty

class PropertiesViewSimulationEntity():

    DefinedPropertyTypes = ["type", "summary", "help", "view"]
    DefinedPropertyLabels = {"type": "Type", "summary": "Summary", "help": "Help", "view": "View"}
    DefinedPropertyHelpTexts = {
       "type": "The type of the simulation entity",
       "summary": "",  # Use simulationEntity.summary
       "help": "Source for help information for this type of simulation entity" +
               "\nDouble click property row to open.",
        "view": "Source for help information for this type of simulation entity" +
                "\nDouble click property row to open.",
    }
    EntityPropertyLabels = {"description": "Description", "submodel": "Submodel", "segment": "Segment", "function": "Function", "annotations": "Annotations"}
    EntityPropertyHelpTexts = {
       "description": "Description of this specific simulation entity" +
                      "\nNote: This is not used in generated ESL",
       "submodel": "The submodel for the submodel call",
       "segment": "The segment for the segment call",
       "function": "The function for the function call",
       "annotations": "Show annotations for the simulation entity on the diagram",
    }
    EntityAnnotationHelpTexts = {
        "description": "Show the simulation entity's description annotation on the diagram",
        "submodel": "Show the simulation entity's submodel's ESL name annotation on the diagram",
        "segment": "Show the simulation entity's segment's ESL name annotation on the diagram",
        "function": "Show the simulation entity's function's ESL name annotation on the diagram",
    }

    def __init__(self, propertiesViewEntityPage):
        self._entityPage = propertiesViewEntityPage

    def setDefinedProperties(self, newItem, simulationEntity, ref):
        # These properties are appended to the defined category - which is is set to the type
        categoryProp = self._entityPage._definedCategory
        propType = "type"
        propLabel = PropertiesViewSimulationEntity.DefinedPropertyLabels.get(propType)
        value = simulationEntity.type()
        helpText = PropertiesViewSimulationEntity.DefinedPropertyHelpTexts.get(propType)
        categoryProp.SetLabel(propLabel)
        categoryProp.SetValue(value)
        categoryProp.SetHelpString(helpText)
        for propType in PropertiesViewSimulationEntity.DefinedPropertyTypes:
            value = ""
            if propType == "type":
                #value = simulationEntity.type()
                continue # dont append a new property - as using the category itself
            elif propType == "summary":
                value = simulationEntity.summary()
            elif propType == "help":
                value = simulationEntity.help()
            elif propType == "view":
                value = simulationEntity.view()
            prop = self._entityPage._definedProperties.get(propType)
            if not prop:
                propLabel = PropertiesViewSimulationEntity.DefinedPropertyLabels.get(propType)
                helpText = PropertiesViewSimulationEntity.DefinedPropertyHelpTexts.get(propType)
                prop = wxpg.StringProperty(propLabel, ref + propType, value=value)
                prop.SetHelpString(helpText)
                self._entityPage._page.AppendIn(categoryProp, prop)
                self._entityPage._definedProperties[propType] = prop
            else:
                prop.SetName(ref + propType)
                prop.SetValue(value)
                prop.Hide(value == "")
            if propType == "summary":
                helpText = simulationEntity.summary()
                prop.SetHelpString(helpText)
            prop.Enable(False)

    def setEntityProperties(self, newItem, simulationEntity, ref):
        # These properties are inserted to the "root" property above the dummy entity category
        categoryProp = self._entityPage._entityCategory
        propType = "description"
        value = simulationEntity.description()
        propLabel = PropertiesViewSimulationEntity.EntityPropertyLabels.get(propType)
        helpText = PropertiesViewSimulationEntity.EntityPropertyHelpTexts.get(propType)
        prop = self._entityPage._entityProperties.get(propType)
        if not prop:
            prop = wxpg.StringProperty(propLabel, ref + propType, value=value)
            prop.SetHelpString(helpText)
            #self._entityPage._page.AppendIn(categoryProp, prop) - dont want these in a category
            self._entityPage._page.Insert(categoryProp, prop) # insert prior to the dummy category property
            self._entityPage._entityProperties[propType] = prop
        else:
            prop.SetName(ref + propType)
            prop.SetValue(value)

        propType = "annotations"
        value = None
        propLabel = PropertiesViewSimulationEntity.EntityPropertyLabels.get(propType)
        helpText = PropertiesViewSimulationEntity.EntityPropertyHelpTexts.get(propType)
        annotations = 0
        if simulationEntity.show_description() == "true": annotations += 1
        showAnnotations = [PropertiesViewSimulationEntity.EntityPropertyLabels["description"]]
        annotationHints = [PropertiesViewSimulationEntity.EntityAnnotationHelpTexts["description"]]
        choiceBits = [1]
        prop = self._entityPage._entityProperties.get(propType)
        if not prop:
            prop = FlagsProperty(propLabel, ref + propType, showAnnotations, choiceBits,
                                              annotations)
            prop.SetHelpString(helpText)
            self._entityPage._page.SetPropertyReadOnly(prop, True, wxpg.PG_DONT_RECURSE)
            #self._entityPage._page.AppendIn(categoryProp, prop) - dont want these in a category
            self._entityPage._page.Insert(categoryProp, prop)  # insert prior to the dummy category property
            self._entityPage._entityProperties[propType] = prop
        else:
            prop.setNameChoicesAndValue(ref + propType, showAnnotations, choiceBits, annotations)
            if newItem:
                self._entityPage._page.Collapse(prop)
        prop.SetValue(annotations)
        prop.setHelpStrings(annotationHints)

        for propType in self._entityPage._entityProperties.keys():
            if propType not in ["description", "annotations"]:
                self._entityPage._entityProperties[propType].Hide(True)

    def setSpecialProperties(self, newItem, simulationEntity, ref):
        # When create these insert in the specials category (hidden or relabelled)
        for prop in self._entityPage._specialProperties.values():
            prop.Hide(True)
        self._entityPage._specialCategory.Hide(True)

    def setAttributeProperties(self, newItem, simulationEntity, ref, label="Attributes"):
        attributesCategory = self._entityPage._attributesCategory
        attributesCategory.SetLabel(label)
        self._entityPage.setEntityAttributeProperties(attributesCategory, newItem, simulationEntity, ref)

    def setSpecial2Properties(self, newItem, simulationEntity, ref):
        # When create these insert in the specials2 category (hidden or relabelled)
        for prop in self._entityPage._special2Properties.values():
            prop.Hide(True)
        self._entityPage._special2Category.Hide(True)

    def setPortProperties(self, newItem, simulationEntity, ref):
        portsCategory = self._entityPage._portsCategory
        self._entityPage.setEntityPortProperties(portsCategory, newItem, simulationEntity, ref)

    def setSpecial3Properties(self, newItem, simulationEntity, ref):
        # When create these insert in the specials3 category (hidden or relabelled)
        for prop in self._entityPage._special3Properties.values():
            prop.Hide(True)
        self._entityPage._special3Category.Hide(True)

    def setEntityPropertyPage(self, pageType, propertyId, headerText, canvasId, objectId, simulationEntity):
        newItem = propertyId != self._entityPage._pagePropertyId
        entityCallSubprogram = None
        entityInsertOutputs = ""
        if simulationEntity.isCall():
            entityCallSubprogram = simulationEntity.subprogram()
            if not newItem:
                if entityCallSubprogram != self._entityPage._entityCallSubprogram:
                    newItem = True
        elif simulationEntity.isCodeInsert():
            entityInsertOutputs = simulationEntity.outputs()
            if not newItem:
                if entityInsertOutputs != self._entityPage._entityInsertOutputs:
                    newItem = True
        self._entityPage._entityCallSubprogram = entityCallSubprogram
        self._entityPage._entityInsertOutputs = entityInsertOutputs
        self._entityPage._pagePropertyId = propertyId

        ref = 'E' + PropertyRefSeparator + str(canvasId) + PropertyRefSeparator + str(objectId) + PropertyChildSeparator

        self.setDefinedProperties(newItem, simulationEntity, ref)

        self.setEntityProperties(newItem, simulationEntity, ref)

        self.setSpecialProperties(newItem, simulationEntity, ref)

        self.setAttributeProperties(newItem, simulationEntity, ref)

        self.setSpecial2Properties(newItem, simulationEntity, ref)

        self.setPortProperties(newItem, simulationEntity, ref)

        self.setSpecial3Properties(newItem, simulationEntity, ref)

    def isActiveAttributeProperty(self, property):
        # A (special) simulation entity may decide this based on other attributes.
        active = True
        return active
